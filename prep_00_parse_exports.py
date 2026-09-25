"""Stage 0a - parse the Label Studio exports (one project per annotator slot) into flat
tables used by all experiments.

Annotator identity comes from the Label Studio user (completed_by), because A annotators also
worked in other slots' projects. If a person annotated the same article in two projects, the
copy from their own project is kept (self-duplicates; the dataset description counts 19).

Outputs in data/prepared/:
  articles.jsonl      one line per article: content, source, author, annotators, entities
  human_labels.csv    dense 0/1 labels: lang, article_id, annotator, layer, unit, label, value
                      units: L2 'doc', L3 paragraph 'p<i>', L1 entity 'e:<key>'
  human_l4_spans.csv  coded-language spans with paragraph index and the three text fields

Articles are identified by a hash of their content, so the same article is matched
across the annotators' projects without relying on task ids.

usage: python prep_00_parse_exports.py [--langs ru tr]
"""
import argparse
import hashlib
import json
import re
from collections import Counter, defaultdict

import pandas as pd
import simplemma

import config
from llm_io import paragraphs


def article_id(content):
    return hashlib.sha1(content.encode("utf-8")).hexdigest()[:12]


def entity_key(text, lang):
    """Lemmatised, case-folded key, so inflected mentions ('Москве', 'Москва') match."""
    text = re.sub(r"['’]\w*", "", text)  # Turkish suffix after apostrophe: Erdoğan'ın -> Erdoğan
    return " ".join(simplemma.lemmatize(tok, lang=lang).casefold() for tok in re.findall(r"\w+", text))


def annotator_of(annotation, lang, where):
    """'ru_A' etc. from the Label Studio user id of an annotation."""
    user = annotation["completed_by"]
    user = user["id"] if isinstance(user, dict) else user  # some LS versions export a user object
    if user not in config.ANNOTATOR_IDS[lang]:
        raise ValueError(f"{where}: unknown Label Studio user {user}")
    return f"{lang}_{config.ANNOTATOR_IDS[lang][user]}"


def same_text(a, b):
    """Offsets check that ignores whitespace: LS exports serialise newlines inconsistently."""
    return re.sub(r"\s", "", a) == re.sub(r"\s", "", b)


def parse_result(result, content, where):
    """Split one annotation into frames, labelled spans and the L4 free-text fields."""
    frames, spans, l4_text = [], [], defaultdict(dict)
    layer_of = {field: layer for layer, field in config.LS_FIELDS.items()}
    for r in result:
        name, v = r["from_name"], r["value"]
        if name == config.LS_FIELDS["L2"]:
            frames += v["choices"]
        elif name in layer_of:
            text = content[v["start"]:v["end"]]  # span text is always taken from content
            if not same_text(text, v["text"]):
                raise ValueError(f"{where}: offsets {v['start']}:{v['end']} do not match {v['text']!r}")
            for label in v["labels"]:
                spans.append({"id": r["id"], "layer": layer_of[name], "start": v["start"],
                              "end": v["end"], "text": text, "label": label})
        elif name in config.L4_TEXT_FIELDS:
            l4_text[r["id"]][config.L4_TEXT_FIELDS[name]] = " ".join(v.get("text", []))
        else:
            raise ValueError(f"{where}: unknown control '{name}'")

    bad = [f for f in frames if f not in config.FRAMES]
    bad += [s["label"] for s in spans if s["layer"] != "L4" and s["label"] not in config.LABELS[s["layer"]]]
    if bad:
        raise ValueError(f"{where}: labels not in config: {bad}")
    return frames, spans, l4_text


def main(langs):
    articles = {}      # article_id -> article dict
    raw = {}           # (article_id, annotator) -> (frames, spans, l4_text)
    project_of = {}    # (article_id, annotator) -> slot letter of the project the annotation came from
    seen_tasks = set()
    self_duplicates = 0

    for (lang, slot), filename in config.EXPORTS.items():
        if lang not in langs:
            continue
        path = config.RAW_DIR / filename
        for task in json.loads(path.read_text(encoding="utf-8")):
            content = task["data"]["content"]
            aid = article_id(content)
            where = f"{filename} task {task['id']}"
            if (aid, slot) in seen_tasks:
                raise ValueError(f"{where}: article {aid} appears twice in this project")
            seen_tasks.add((aid, slot))
            meta = {name: task["data"].get(field) for name, field in config.TASK_META_FIELDS.items()}
            art = articles.setdefault(aid, {"article_id": aid, "lang": lang, "content": content, **meta})
            if art["lang"] != lang:
                raise ValueError(f"{where}: article {aid} appears in two languages")

            for annotation in task.get("annotations", []):
                if annotation.get("was_cancelled"):
                    continue
                annotator = annotator_of(annotation, lang, where)
                key = (aid, annotator)
                if key in raw:  # same person, same article, two projects: keep their own project's copy
                    self_duplicates += 1
                    if project_of[key] == annotator[-1]:
                        continue
                    if slot != annotator[-1]:
                        raise ValueError(f"{where}: {annotator} annotated {aid} twice, neither in own project")
                raw[key] = parse_result(annotation["result"], content, where)
                project_of[key] = slot

    for (aid, annotator) in raw:
        articles[aid].setdefault("annotators", []).append(annotator)

    # Entities: every L1 mention, grouped by lemma key.
    for aid, art in articles.items():
        paras = paragraphs(art["content"])
        art["n_paragraphs"] = len(paras)
        art["annotators"] = sorted(art.get("annotators", []))
        art["n_annotators"] = len(art["annotators"])
        surface_forms = defaultdict(Counter)
        for annotator in art["annotators"]:
            for s in raw[(aid, annotator)][1]:
                if s["layer"] != "L1":
                    continue
                key = entity_key(s["text"], art["lang"])
                if key:
                    surface_forms[key][s["text"].strip()] += 1
        art["entities"] = [{"key": k, "display": forms.most_common(1)[0][0]}
                           for k, forms in sorted(surface_forms.items())]

    # Dense human labels: every unit x label for every annotator who annotated the article.
    rows, l4_rows = [], []
    for (aid, annotator), (frames, spans, l4_text) in raw.items():
        art = articles[aid]
        lang, paras = art["lang"], paragraphs(art["content"])

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
        for e in art["entities"]:
            add("L1", f"e:{e['key']}", roles[e["key"]])

        for s in spans:
            if s["layer"] == "L4":
                paragraph = next(i for i, p in enumerate(paras) if s["start"] < p["end"])
                l4_rows.append({"lang": lang, "article_id": aid, "annotator": annotator,
                                "start": s["start"], "end": s["end"], "text": s["text"],
                                "paragraph": paragraph, **l4_text.get(s["id"], {})})

    config.PREP_DIR.mkdir(parents=True, exist_ok=True)
    with open(config.PREP_DIR / "articles.jsonl", "w", encoding="utf-8") as f:
        for art in articles.values():
            f.write(json.dumps(art, ensure_ascii=False) + "\n")
    labels = pd.DataFrame(rows, columns=["lang", "article_id", "annotator", "layer", "unit", "label", "value"])
    labels.to_csv(config.PREP_DIR / "human_labels.csv", index=False)
    pd.DataFrame(l4_rows).to_csv(config.PREP_DIR / "human_l4_spans.csv", index=False)

    summary = pd.DataFrame(articles.values())
    print("articles per language x number of annotators:")
    print(pd.crosstab(summary["lang"], summary["n_annotators"]))
    print(f"human label rows: {len(labels)}, L4 spans: {len(l4_rows)}, self-duplicates resolved: {self_duplicates}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--langs", nargs="+", default=["ru", "tr"])
    main(parser.parse_args().langs)