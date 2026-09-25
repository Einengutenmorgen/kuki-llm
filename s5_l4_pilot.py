"""Stage 5 - L4 pilot: can the model flag the coded phrases the annotators marked?
Whole-article input, both prompt languages, temperature 0. Evaluated at paragraph level.

usage: python s5_l4_pilot.py --model olmo3-7b
"""
import argparse

import config
import llm_io

EXPERIMENT = "s5_l4_pilot"

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="alias in config.MODELS")
parser.add_argument("--prompt-langs", nargs="+", default=config.PROMPT_LANGS)
args = parser.parse_args()

articles = llm_io.load_split("s5_l4_pilot")
articles = [a for a in articles if a["lang"] in config.MODELS[args.model]["langs"]]

jobs = llm_io.make_jobs(EXPERIMENT, articles, args.model, ["L4"], ["doc"], args.prompt_langs)
llm_io.run_jobs(jobs, EXPERIMENT, args.model)
