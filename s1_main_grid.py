"""Stage 1 - main grid on the core set: one model x all granularities x both prompt
languages x layers L1-L3, temperature 0. Run once per model (the model is loaded once per run).

usage: python s1_main_grid.py --model olmo3-7b [--dev]
       --dev runs on the dev split (prompt/parsing debugging) and writes to s1_dev__<model>.jsonl
"""
import argparse

import config
import llm_io

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="alias in config.MODELS")
parser.add_argument("--layers", nargs="+", default=["L1", "L2", "L3"])
parser.add_argument("--dev", action="store_true")
args = parser.parse_args()

EXPERIMENT = "s1_dev" if args.dev else "s1_main_grid"
articles = llm_io.load_split("dev" if args.dev else "s1_main_grid")
articles = [a for a in articles if a["lang"] in config.MODELS[args.model]["langs"]]

jobs = llm_io.make_jobs(EXPERIMENT, articles, args.model, args.layers,
                        config.GRANULARITIES, config.PROMPT_LANGS)
llm_io.run_jobs(jobs, EXPERIMENT, args.model)
