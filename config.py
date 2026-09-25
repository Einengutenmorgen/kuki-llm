"""Shared constants for the KuKi LLM annotation experiments.

Paths can be redirected with the environment variables KUKI_DATA_DIR and
KUKI_PROMPT_DIR (used by the test notebook).
"""
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("KUKI_DATA_DIR", "data"))
PROMPT_DIR = Path(os.environ.get("KUKI_PROMPT_DIR", "prompts"))

RAW_DIR = DATA_DIR / "raw"             # Label Studio JSON exports
PREP_DIR = DATA_DIR / "prepared"       # written by prep_00_parse_exports.py
SPLIT_DIR = DATA_DIR / "splits"        # written by prep_01_make_splits.py
PRED_DIR = DATA_DIR / "predictions"    # raw LLM outputs, one JSONL per experiment
RESULT_DIR = DATA_DIR / "results"      # written by evaluate.py / analyze_s1_decomposition.py

SEED = 13

# One Label Studio project per annotator -> one JSON export per annotator.
EXPORTS = {
    ("ru", "A"): "ru_A.json", ("ru", "B"): "ru_B.json", ("ru", "C"): "ru_C.json",
    ("tr", "A"): "tr_A.json", ("tr", "B"): "tr_B.json", ("tr", "C"): "tr_C.json",
}
# Article metadata: our name -> field name in task["data"] of the export. VERIFY field names.
TASK_META_FIELDS = {"source": "source", "author": "author"}

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

# Label Studio control names (from_name) per layer.
LS_FIELDS = {"L1": "l1_roles", "L2": "l2_frames", "L3": "l3_persuasion", "L4": "l4_coded"}
L4_TEXT_FIELDS = {"l4_literal": "literal", "l4_insider": "insider", "l4_why": "why"}

# Crossed factors of the main grid.
GRANULARITIES = ["doc", "para", "para_ctx"]
PROMPT_LANGS = ["en", "native"]

# L2 in paragraph modes: a frame counts for the document if it is predicted in at least
# this many paragraphs. Pre-registered value 1 (= union); 2 is the sensitivity check.
L2_PARA_MIN = 1

# Source -> (name shown in metadata prompts, orientation pole). VERIFY keys and poles.
SOURCES = {
    "ria_novosti": ("RIA Novosti", "gov_close"),
    "ng_vision": ("Nezavisimaya Gazeta", "gov_close"),
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
