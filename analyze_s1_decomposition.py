"""Stage 1 analysis - how much of the variation in ceiling-normalised agreement (q)
does each design decision explain? One two-way ANOVA per language and layer on the
Stage-1 summary (one row per configuration).

share = sum of squares of a term / total sum of squares (Type-II sums of squares;
approximate when the grid is unbalanced, e.g. no Turkish L-size specialised model).

usage: python analyze_s1_decomposition.py
"""
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

import config

FACTORS = ["size", "profile", "granularity", "prompt_lang"]

summary = pd.read_csv(config.RESULT_DIR / "s1_main_grid_summary.csv")
tables = []
for (lang, layer), g in summary.groupby(["lang", "layer"]):
    g = g.dropna(subset=["q"])  # q is undefined where human alpha is <= 0 or undefined
    if len(g) < 3:
        print(f"{lang} {layer}: only {len(g)} configurations with defined q, skipped")
        continue
    factors = [f for f in FACTORS if g[f].nunique() > 1]  # a factor with one level explains nothing
    formula = "q ~ (" + " + ".join(f"C({f})" for f in factors) + ") ** 2"
    table = anova_lm(smf.ols(formula, data=g).fit(), typ=2)
    table["share"] = table["sum_sq"] / table["sum_sq"].sum()
    tables.append(table.reset_index(names="term").assign(lang=lang, layer=layer))

result = pd.concat(tables)[["lang", "layer", "term", "share", "sum_sq", "df", "F", "PR(>F)"]]
result = result.sort_values(["lang", "layer", "share"], ascending=[True, True, False])
result.to_csv(config.RESULT_DIR / "s1_decomposition.csv", index=False)
print(result.round(3).to_string(index=False))
