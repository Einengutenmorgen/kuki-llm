"""Stage 0b - define the article set of every experiment (one CSV per experiment in data/splits/).

  dev.csv                  single-annotated articles, only for prompt and parsing debugging
  s1_main_grid.csv         core set: all articles with >= 2 annotators (human ceiling defined)
  s2_stability.csv         core set
  s3_metadata_probe.csv    core set + a swapped source from the opposite orientation pole
  s4_generalisation.csv    single-annotated articles not used in dev
  s5_l4_pilot.csv          random sample of the core set

usage: python prep_01_make_splits.py [--n-dev 20] [--n-l4 25]
"""
import argparse
import random

import pandas as pd

import config
from llm_io import read_jsonl


def with_swaps(df, all_articles):
    """For each article, pick a random article of the same language from the opposite
    orientation pole and take its source (and author, if the data has one) as the 'swapped' metadata."""
    pole = all_articles["source"].map(lambda s: config.SOURCES[s][1])
    rng = random.Random(config.SEED)
    swap_source, swap_author = [], []
    for row in df.itertuples():
        candidates = all_articles[(all_articles["lang"] == row.lang) & (pole != config.SOURCES[row.source][1])]
        pick = candidates.iloc[rng.randrange(len(candidates))]
        swap_source.append(pick["source"])
        swap_author.append(pick["author"])
    return df.assign(swap_source=swap_source, swap_author=swap_author)


def main(n_dev, n_l4):
    articles = pd.DataFrame(read_jsonl(config.PREP_DIR / "articles.jsonl"))
    articles = articles[["article_id", "lang", "n_annotators", "source", "author"]]
    unknown = set(articles["source"]) - set(config.SOURCES)
    if unknown:
        raise ValueError(f"sources missing in config.SOURCES: {unknown}")

    core = articles[articles["n_annotators"] >= 2]
    single = articles[articles["n_annotators"] == 1]
    dev = single.groupby("lang", group_keys=False).sample(n=n_dev, random_state=config.SEED)

    splits = {
        "dev": dev,
        "s1_main_grid": core,
        "s2_stability": core,
        "s3_metadata_probe": with_swaps(core, articles),
        "s4_generalisation": single.drop(dev.index),
        "s5_l4_pilot": core.groupby("lang", group_keys=False).sample(n=n_l4, random_state=config.SEED),
    }

    config.SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"not annotated (excluded everywhere): {(articles['n_annotators'] == 0).sum()}")
    for name, df in splits.items():
        df.to_csv(config.SPLIT_DIR / f"{name}.csv", index=False)
        print(f"{name:20s}", df["lang"].value_counts().sort_index().to_dict())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-dev", type=int, default=20, help="dev articles per language")
    parser.add_argument("--n-l4", type=int, default=25, help="L4 pilot articles per language")
    args = parser.parse_args()
    main(args.n_dev, args.n_l4)