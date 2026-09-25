"""Stage 0a - load the two aggregate files (data/kuki_ru_aggregate.jsonl, data/kuki_tr_aggregate.jsonl)
into the flat tables used by all experiments. Real and test data go through this same code.

The aggregates already resolve annotator identity and self-duplicates (one entry per person
and article, keyed by Label Studio user id).

Outputs in data/prepared/:
  articles.jsonl      one line per article: content, source, annotators, entities
  human_labels.csv    dense 0/1 labels: lang, article_id, annotator, layer, unit, label, value
                      units: L2 'doc', L3 paragraph 'p<i>', L1 entity 'e:<key>'
  human_l4_spans.csv  coded-language spans with paragraph index and the three text fields

usage: python prep_00_load_data.py [--langs ru tr]
"""
import argparse
import json
import re
from collections import Counter, defaultdict

import pandas as pd
import simplemma

import config
from llm_io import paragraphs, read_jsonl

LAYER_OF = {field: layer for layer, field in config.LS_FIELDS.items()}


def entity_key(text, lang):
    """Lemmatised, case-folded key, so inflected mentions ('Москве', 'Москва') match."""
    text = re.sub(r"['’]\w*", "", text)  # Turkish suffix after apostrophe: Erdoğan'ın -> Erdoğan
    return " ".join(simplemma.lemmatize(tok, lang=lang).casefold() for tok in re.findall(r"\w+", text))


def load_article(rec, dropped):
    """One aggregate record -> (article dict, {annotator: (frames, spans)}).
    Spans whose label belongs to another layer (4 in RU, a Label Studio glitch) are dropped
    and listed in `dropped`; the dataset description counts without them."""
    lang, content = rec["lang"], rec["content"]
    annotations = {}
    for user, ann in rec["annotations"].items():
        annotator = f"{lang}_{config.ANNOTATOR_IDS[lang][int(user)]}"
        spans = []
        for s in ann["spans"]:
            layer = LAYER_OF[s["layer"]]
            if s["label"] not in config.LABELS.get(layer, ["Coded Phrase"]):
                dropped.append((rec["doc_id"], annotator, s["layer"], s["label"], s["text"]))
                continue
            spans.append({**s, "layer": layer, "text": content[s["start"]:s["end"]]})
        bad = [f for f in ann["frames"] if f not in config.FRAMES]
        if bad:
            raise ValueError(f"{rec['doc_id']}: unknown frames {bad}")
        annotations[annotator] = (ann["frames"], spans)

    surface_forms = defaultdict(Counter)  # entities: every L1 mention, grouped by lemma key
    for _, spans in annotations.values():
        for s in spans:
            key = entity_key(s["text"], lang) if s["layer"] == "L1" else ""
            if key:
                surface_forms[key][s["text"].strip()] += 1

    article = {"article_id": rec["doc_id"], "lang": lang, "source": rec["source"],
               "author": rec.get("author"), "published_at": rec.get("published_at"),
               "content": content, "n_paragraphs": len(paragraphs(content)),
               "annotators": sorted(annotations), "n_annotators": len(annotations),
               "entities": [{"key": k, "display": forms.most_common(1)[0][0]}
                            for k, forms in sorted(surface_forms.items())]}
    return article, annotations


def label_rows(article, annotations):
    """Dense human labels (every unit x label for every annotator) and the L4 spans."""
    rows, l4_rows = [], []
    lang, aid, paras = article["lang"], article["article_id"], paragraphs(article["content"])
    for annotator, (frames, spans) in annotations.items():
        def add(layer, unit, positives):
            for label in config.LABELS[layer]:
                rows.append((lang, aid, annotator, layer, unit, label, int(label in positives)))

        add("L2", "doc", set(frames))
        for i, p in enumerate(paras):  # a paragraph is positive if any span of the category overlaps it
            add("L3", f"p{i}", {s["label"] for s in spans
                                if s["layer"] == "L3" and s["start"] < p["end"] and s["end"] > p["start"]})
        roles = defaultdict(set)
        for s in spans:
            if s["layer"] == "L1":
                roles[entity_key(s["text"], lang)].add(s["label"])
        for e in article["entities"]:
            add("L1", f"e:{e['key']}", roles[e["key"]])

        for s in spans:
            if s["layer"] == "L4":
                paragraph = next(i for i, p in enumerate(paras) if s["start"] < p["end"])
                l4_rows.append({"lang": lang, "article_id": aid, "annotator": annotator,
                                "start": s["start"], "end": s["end"], "text": s["text"], "paragraph": paragraph,
                                **{k: s.get(k, "") for k in ("literal", "insider", "why")}})
    return rows, l4_rows


def main(langs):
    articles, rows, l4_rows, dropped = [], [], [], []
    for lang in langs:
        for rec in read_jsonl(config.AGGREGATES[lang]):
            article, annotations = load_article(rec, dropped)
            articles.append(article)
            r, l4 = label_rows(article, annotations)
            rows += r
            l4_rows += l4

    config.PREP_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.PREP_DIR / "articles.jsonl", "w", encoding="utf-8") as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + "\n")
    labels = pd.DataFrame(rows, columns=["lang", "article_id", "annotator", "layer", "unit", "label", "value"])
    labels.to_csv(config.PREP_DIR / "human_labels.csv", index=False)
    pd.DataFrame(l4_rows).to_csv(config.PREP_DIR / "human_l4_spans.csv", index=False)

    summary = pd.DataFrame(articles)
    print("articles per language x number of annotators:")
    print(pd.crosstab(summary["lang"], summary["n_annotators"]))
    print(f"human label rows: {len(labels)}, L4 spans: {len(l4_rows)}")
    print(f"dropped {len(dropped)} spans with a label from another layer:")
    for d in dropped:
        print("  ", *d)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", nargs="+", default=["ru", "tr"])
    main(parser.parse_args().langs)