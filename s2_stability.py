"""Stage 2 - stability and soft labels: repeated sampling (default 5 samples at T=0.7)
for one model in one fixed condition, chosen after inspecting the Stage-1 results.

usage: python s2_stability.py --model olmo3-7b --granularity para_ctx --prompt-lang en
"""
import argparse

import config
import llm_io

EXPERIMENT = "s2_stability"

parser = argparse.ArgumentParser()
parser.add_argument("--model", required=True, help="alias in config.MODELS")
parser.add_argument("--granularity", required=True, choices=config.GRANULARITIES)
parser.add_argument("--prompt-lang", required=True, choices=config.PROMPT_LANGS)
parser.add_argument("--layers", nargs="+", default=["L1", "L2", "L3"])
parser.add_argument("--n-samples", type=int, default=5)
parser.add_argument("--temperature", type=float, default=0.7)
args = parser.parse_args()

articles = llm_io.load_split("s2_stability")
articles = [a for a in articles if a["lang"] in config.MODELS[args.model]["langs"]]

jobs = llm_io.make_jobs(EXPERIMENT, articles, args.model, args.layers,
                        [args.granularity], [args.prompt_lang],
                        n_samples=args.n_samples, temperature=args.temperature)
llm_io.run_jobs(jobs, EXPERIMENT, args.model)
