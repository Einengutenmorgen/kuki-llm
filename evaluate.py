"""Evaluate one experiment: LLM outputs -> unit labels -> agreement with the annotators.

Metrics per configuration and label (summary = mean over labels):
  alpha_h     Krippendorff's alpha among the human annotators
  alpha_rep   mean alpha when one annotator at a time is replaced by the LLM
  q           alpha_rep / alpha_h: ceiling-normalised agreement (1 = like a human annotator)
  alpha_pair  mean alpha between the LLM and each single annotator
  persp_acc   share of units where the LLM label equals at least one annotator's label
  prev_ratio  LLM positive rate / human positive rate (over- or under-labelling)
  brier       squared distance between LLM probability (mean over samples) and human vote share

Pre-registered choices: failed or unparsable calls count as 'no label'; L2 in paragraph
modes uses config.L2_PARA_MIN; alpha uses sample 0 only.

Outputs in data/results/: <experiment>_labels.csv, <experiment>_summary.csv,
plus <experiment>_prevalence_by_meta.csv (s3) or <experiment>_l4.csv (s5).

usage: python evaluate.py --experiment s1_main_grid
"""
import argparse
from collections import Counter, defaultdict

import krippendorff
import numpy as np
import pandas as pd

import config
from llm_io import read_jsonl

CONFIG_COLS = ["model", "lang", "layer", "granularity", "prompt_lang", "metadata"]


# ---------- LLM outputs -> unit labels ----------

def units_of(article, layer):
    if layer == "L2":
        return ["doc"]
    if layer == "L3":
        return [f"p{i}" for i in range(article["n_paragraphs"])]
    return [f"e:{e['key']}" for e in article["entities"]]


def positives(record, article):
    """(unit, label) pairs one LLM call marked as present."""
    out = record["parsed"]
    if not out:
        return set()
    layer = record["layer"]
    if layer == "L2":
        return {("doc", f) for f in out["frames"]}
    if layer == "L3":
        pairs = set()
        for t in out["techniques"]:
            p = t["paragraph"] if record["granularity"] == "doc" else record["target"]
            if isinstance(p, int) and 0 <= p < article["n_paragraphs"]:  # invalid paragraph numbers are ignored
                pairs.add((f"p{p}", t["category"]))
        return pairs
    key_of = {e["display"]: e["key"] for e in article["entities"]}
    return {(f"e:{key_of[r['entity']]}", r["role"]) for r in out["roles"]}


def llm_unit_labels(records, articles):
    """Dense 0/1 LLM labels per configuration, sample, article, unit and label."""
    counts = defaultdict(Counter)
    for rec in records:
        group = tuple(rec[c] for c in CONFIG_COLS) + (rec["sample"], rec["article_id"])
        counts[group].update(positives(rec, articles[rec["article_id"]]))

    rows = []
    for group, c in counts.items():
        cfg = dict(zip(CONFIG_COLS, group))
        sample, aid = group[-2:]
        min_count = config.L2_PARA_MIN if cfg["layer"] == "L2" and cfg["granularity"] != "doc" else 1
        for unit in units_of(articles[aid], cfg["layer"]):
            for label in config.LABELS[cfg["layer"]]:
                rows.append((*group, unit, label, int(c[(unit, label)] >= min_count)))
    return pd.DataFrame(rows, columns=CONFIG_COLS + ["sample", "article_id", "unit", "label", "value"])


# ---------- agreement ----------

def alpha(matrix):
    """Nominal Krippendorff's alpha; rows = coders, columns = units, NaN = missing."""
    if matrix.shape[0] < 2:
        return np.nan
    try:
        return krippendorff.alpha(reliability_data=matrix, level_of_measurement="nominal")
    except ValueError:  # fewer than two distinct values: alpha is undefined
        return np.nan


def label_metrics(H, hard, prob):
    """H: units x annotators (NaN = not annotated); hard: LLM 0/1 of sample 0;
    prob: LLM mean over samples. All indexed by (article_id, unit)."""
    alpha_h = alpha(H.T.values)
    rep, pair = [], []
    for h in H.columns:
        llm_where_h = hard.where(H[h].notna())
        replaced = H.copy()
        replaced[h] = llm_where_h
        rep.append(alpha(replaced.T.values))
        pair.append(alpha(np.vstack([H[h].values, llm_where_h.values])))
    alpha_rep = pd.Series(rep).mean()

    judged = hard.notna() & H.notna().any(axis=1)
    return {
        "alpha_h": alpha_h,
        "alpha_rep": alpha_rep,
        "q": alpha_rep / alpha_h if alpha_h > 0 else np.nan,
        "alpha_pair": pd.Series(pair).mean(),
        "persp_acc": H.eq(hard, axis=0).any(axis=1)[judged].mean(),
        "prev_ratio": hard.mean() / H.stack().mean() if H.stack().mean() > 0 else np.nan,
        "brier": ((prob - H.mean(axis=1)) ** 2).mean(),
    }


def evaluate_layers(records, articles, experiment):
    llm = llm_unit_labels(records, articles)
    human = pd.read_csv(config.PREP_DIR / "human_labels.csv")
    human = human[human["article_id"].isin(llm["article_id"].unique())]
    human_matrix = human.pivot_table(index=["lang", "layer", "label", "article_id", "unit"],
                                     columns="annotator", values="value").sort_index()

    rows = []
    for cfg_values, g in llm.groupby(CONFIG_COLS):
        cfg = dict(zip(CONFIG_COLS, cfg_values))
        for label, gl in g.groupby("label"):
            H = human_matrix.loc[(cfg["lang"], cfg["layer"], label)].dropna(axis=1, how="all")
            per_sample = gl.pivot_table(index=["article_id", "unit"], columns="sample", values="value")
            per_sample = per_sample.reindex(H.index)
            metrics = label_metrics(H, per_sample[0], per_sample.mean(axis=1))
            rows.append({**cfg, "label": label, **metrics})
    label_table = pd.DataFrame(rows)

    calls = pd.DataFrame(records)
    calls["parse_fail"] = ~calls["parse_ok"]
    calls["has_error"] = calls["error"].notna()
    operations = calls.groupby(CONFIG_COLS).agg(
        n_calls=("key", "size"), parse_fail=("parse_fail", "mean"), error_rate=("has_error", "mean"),
        tokens_in=("tokens_in", "mean"), tokens_out=("tokens_out", "mean"), seconds=("seconds", "mean"))
    summary = label_table.groupby(CONFIG_COLS).mean(numeric_only=True).join(operations).reset_index()
    summary["size"] = summary["model"].map(lambda m: config.MODELS[m]["size"])
    summary["profile"] = summary["model"].map(lambda m: config.MODELS[m]["profile"])

    config.RESULT_DIR.mkdir(parents=True, exist_ok=True)
    label_table.to_csv(config.RESULT_DIR / f"{experiment}_labels.csv", index=False)
    summary.to_csv(config.RESULT_DIR / f"{experiment}_summary.csv", index=False)
    print(summary[CONFIG_COLS + ["q", "alpha_pair", "persp_acc", "parse_fail", "error_rate"]].round(3).to_string())

    if llm["metadata"].nunique() > 1:  # s3: label prevalence by metadata condition and true outlet pole
        llm["true_pole"] = llm["article_id"].map(lambda aid: config.SOURCES[articles[aid]["source"]][1])
        prevalence = (llm[llm["sample"] == 0]
                      .groupby(["model", "lang", "layer", "label", "true_pole", "metadata"])["value"]
                      .mean().unstack("metadata"))
        prevalence["shift_true_vs_none"] = prevalence["true"] - prevalence["none"]
        prevalence["shift_swapped_vs_true"] = prevalence["swapped"] - prevalence["true"]
        prevalence.to_csv(config.RESULT_DIR / f"{experiment}_prevalence_by_meta.csv")


# ---------- L4 pilot ----------

def evaluate_l4(records, experiment):
    """Paragraph-level detection: does the LLM flag the paragraphs where annotators marked coded language?"""
    spans = pd.read_csv(config.PREP_DIR / "human_l4_spans.csv")
    human_all = set(zip(spans["article_id"], spans["paragraph"]))

    by_config = defaultdict(list)
    for rec in records:
        by_config[tuple(rec[c] for c in CONFIG_COLS)].append(rec)

    rows = []
    for cfg_values, recs in by_config.items():
        ids = {r["article_id"] for r in recs}
        human = {(aid, p) for aid, p in human_all if aid in ids}
        flagged = {(r["article_id"], item["paragraph"]) for r in recs if r["parsed"] for item in r["parsed"]["coded"]}
        hits = len(human & flagged)
        rows.append({**dict(zip(CONFIG_COLS, cfg_values)),
                     "recall": hits / len(human) if human else np.nan,
                     "precision": hits / len(flagged) if flagged else np.nan,
                     "n_human_paragraphs": len(human), "n_flagged_paragraphs": len(flagged)})
    table = pd.DataFrame(rows)
    config.RESULT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(config.RESULT_DIR / f"{experiment}_l4.csv", index=False)
    print(table.round(3).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", required=True, help="e.g. s1_main_grid, s1_dev, s3_metadata_probe")
    experiment = parser.parse_args().experiment

    files = sorted(config.PRED_DIR.glob(f"{experiment}__*.jsonl"))  # one file per model
    if not files:
        raise FileNotFoundError(f"no predictions for {experiment} in {config.PRED_DIR}")
    records = [r for path in files for r in read_jsonl(path)]
    articles = {a["article_id"]: a for a in read_jsonl(config.PREP_DIR / "articles.jsonl")}
    l4_records = [r for r in records if r["layer"] == "L4"]
    other_records = [r for r in records if r["layer"] != "L4"]
    if other_records:
        evaluate_layers(other_records, articles, experiment)
    if l4_records:
        evaluate_l4(l4_records, experiment)
