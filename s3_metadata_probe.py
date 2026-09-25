"""Stage 3 - metadata probe: the same article with no metadata, its true source/author,
or a source/author swapped from the opposite orientation pole (see prep_01).
Whole-article input, English prompt, temperature 0.

usage: python s3_metadata_probe.py --model olmo3.1-32b
"""
import argparse

import config
import llm_io

EXPERIMENT = "s3_metadata_probe"

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="alias in config.MODELS")
parser.add_argument("--layers", nargs="+", default=["L1", "L2", "L3"])
args = parser.parse_args()

articles = llm_io.load_split("s3_metadata_probe")
articles = [a for a in articles if a["lang"] in config.MODELS[args.model]["langs"]]


def meta(source, author):
    """Metadata line: source, plus author where the data has one (the aggregates have none)."""
    m = {"source": config.SOURCES[source][0]}
    if isinstance(author, str) and author:
        m["author"] = author
    return m


for a in articles:
    a["meta"] = {"none": None, "true": meta(a["source"], a.get("author")),
                 "swapped": meta(a["swap_source"], a.get("swap_author"))}

jobs = llm_io.make_jobs(EXPERIMENT, articles, args.model, args.layers, ["doc"], ["en"],
                        metadata_modes=["none", "true", "swapped"])
llm_io.run_jobs(jobs, EXPERIMENT, args.model)
