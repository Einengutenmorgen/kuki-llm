"""Stage 4 - generalisation check: selected configurations (e.g. best and worst from
Stage 1) on the single-annotated articles that were not used as dev set.

usage: python s4_generalisation.py --model olmo3.1-32b --granularity para_ctx --prompt-lang en
"""
import argparse

import config
import llm_io

EXPERIMENT = "s4_generalisation"

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="alias in config.MODELS")
parser.add_argument("--granularity", required=True, choices=config.GRANULARITIES)
parser.add_argument("--prompt-lang", required=True, choices=config.PROMPT_LANGS)
parser.add_argument("--layers", nargs="+", default=["L1", "L2", "L3"])
args = parser.parse_args()

articles = llm_io.load_split("s4_generalisation")
articles = [a for a in articles if a["lang"] in config.MODELS[args.model]["langs"]]

jobs = llm_io.make_jobs(EXPERIMENT, articles, args.model, args.layers,
                        [args.granularity], [args.prompt_lang])
llm_io.run_jobs(jobs, EXPERIMENT, args.model)
