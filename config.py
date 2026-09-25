"""Shared constants for the KuKi LLM annotation experiments.

All paths are absolute and anchored at this repository folder, so scripts and notebooks
work from any working directory. Real runs use <repo>/data and <repo>/prompts.
The test notebook sets KUKI_TEST=1 before importing anything; then everything lives in
<repo>/test_run/ and real data is never touched.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEST_MODE = os.environ.get("KUKI_TEST") == "1"
BASE_DIR = ROOT / "test_run" if TEST_MODE else ROOT

DATA_DIR = BASE_DIR / "data"
PROMPT_DIR = BASE_DIR / "prompts"
PREP_DIR = DATA_DIR / "prepared"       # written by prep_00_load_data.py
SPLIT_DIR = DATA_DIR / "splits"        # written by prep_01_make_splits.py
PRED_DIR = DATA_DIR / "predictions"    # raw LLM outputs, one JSONL per experiment and model
RESULT_DIR = DATA_DIR / "results"      # written by evaluate.py / analyze_s1_decomposition.py

print(f"[config] {'TEST' if TEST_MODE else 'REAL'} data: {DATA_DIR}")

SEED = 13

# Input: the two aggregate files of the dataset (one record per article, all annotators).
# Not in git (size); copy them into data/. The test notebook writes synthetic ones in the same format.
AGGREGATES = {"ru": DATA_DIR / "kuki_ru_aggregate.jsonl", "tr": DATA_DIR / "kuki_tr_aggregate.jsonl"}
# Label Studio user id -> annotator letter (dataset description, section 3).
ANNOTATOR_IDS = {"ru": {8: "A", 4: "B", 10: "C"}, "tr": {11: "A", 7: "B", 6: "C"}}

# Label sets exactly as they appear in the Label Studio config.
ROLES = ["PROTAGONIST", "ANTAGONIST", "INNOCENT"]
FRAMES = [
    "Economic", "Capacity & resources", "Morality", "Fairness & equality",
    "Legality, constitutionality, jurisprudence", "Policy prescription & evaluation",
    "Crime & punishment", "Security & defense", "Health & safety", "Quality of life",
    "Cultural identity", "Public opinion", "Political", "External regulation & reputation",
]
PERSUASION = ["Attack on Reputation", "Justification", "Simplification",
              "Distraction", "Call", "Manipulative Wording"]
LABELS = {"L1": ROLES, "L2": FRAMES, "L3": PERSUASION}

# Span layer names as they appear in the aggregate files (Label Studio control names).
LS_FIELDS = {"L1": "l1_roles", "L3": "l3_persuasion", "L4": "l4_coded"}

# Crossed factors of the main grid.
GRANULARITIES = ["doc", "para", "para_ctx"]
PROMPT_LANGS = ["en", "native"]

# L2 in paragraph modes: a frame counts for the document if it is predicted in at least
# this many paragraphs. Pre-registered value 1 (= union); 2 is the sensitivity check.
L2_PARA_MIN = 1

# Source -> (name shown in metadata prompts, orientation pole). VERIFY keys and poles.
SOURCES = {
    "ria_novosti": ("RIA Novosti", "gov_close"),
    "ng": ("Nezavisimaya Gazeta", "gov_close"),
    "theinsider": ("The Insider", "gov_distant"),
    "holod": ("Holod", "gov_distant"),
    "sabah": ("Sabah", "gov_close"),
    "cumhuriyet": ("Cumhuriyet", "gov_distant"),
    "yenicag": ("Yeniçağ", "gov_distant"),
    "odatv": ("Oda TV", "gov_distant"),
}

# Model grid. size: S/M/L, profile: english/multilingual/specialised.
# All models run locally with transformers in their native precision (dtype from the checkpoint).
# Optional keys: "template_kwargs" (passed to the chat template), "merge_system" (template has
# no system role). Development starts with the two OLMo models; the rest is added later.
MODELS = {
    "olmo3-7b": {"hf": "allenai/Olmo-3-7B-Instruct", "size": "M", "profile": "english", "langs": ["ru", "tr"]},
    "olmo3.1-32b": {"hf": "allenai/Olmo-3.1-32B-Instruct", "size": "L", "profile": "english", "langs": ["ru", "tr"]},
    # Next: Qwen3 family (1.7B/8B/32B) with "template_kwargs": {"enable_thinking": False}.
    # Then: RU- and TR-specialised models.
    # Mock models: random but schema-valid outputs, for testing the pipeline without a GPU.
    "mock-S": {"hf": "mock", "size": "S", "profile": "english", "langs": ["ru", "tr"]},
    "mock-M": {"hf": "mock", "size": "M", "profile": "multilingual", "langs": ["ru", "tr"]},
}