# KuKi LLM annotation experiments

Which design decisions (model size, language profile, input granularity, prompt
language) determine how closely LLM annotations of narrative framing in RU/TR opinion
journalism approximate human annotation?

## Order of work

| Step | Script | Output |
|---|---|---|
| 0a | `prep_00_parse_exports.py` | `data/prepared/` articles, dense human labels, L4 spans |
| 0b | `prep_01_make_splits.py` | `data/splits/<experiment>.csv` |
| 1 | `s1_main_grid.py --model X` (first with `--dev`) | `data/predictions/s1_main_grid__X.jsonl` |
| 2 | `s2_stability.py --model X --granularity G --prompt-lang P` | `.../s2_stability__X.jsonl` |
| 3 | `s3_metadata_probe.py --model X` | `.../s3_metadata_probe__X.jsonl` |
| 4 | `s4_generalisation.py --model X --granularity G --prompt-lang P` | `.../s4_generalisation__X.jsonl` |
| 5 | `s5_l4_pilot.py --model X` | `.../s5_l4_pilot__X.jsonl` |
| eval | `evaluate.py --experiment <name>` | `data/results/<name>_*.csv` |
| S1 analysis | `analyze_s1_decomposition.py` | `data/results/s1_decomposition.csv` |

Shared code: `config.py` (paths, labels, model grid), `llm_io.py` (prompts, schemas, generation).

Models run in-process with Hugging Face transformers, in native precision, with JSON-schema
constrained decoding (lm-format-enforcer). Choose GPUs with CUDA_VISIBLE_DEVICES:

    CUDA_VISIBLE_DEVICES=0 python s1_main_grid.py --model olmo3-7b --dev       # 7B: one L40
    CUDA_VISIBLE_DEVICES=0,1 python s1_main_grid.py --model olmo3.1-32b --dev  # 32B: both L40s

Predictions are written per experiment and model (`<experiment>__<model>.jsonl`), so two
runs on two GPUs never share a file; `evaluate.py` reads all models of an experiment.
Install: `pip install -r requirements.txt`.
Tests without GPU: `test_pipeline.ipynb` (mock models on synthetic exports).

## Before the first real run

1. Put the six Label Studio JSON exports into `data/raw/` (names in `config.EXPORTS`).
2. Check `config.TASK_META_FIELDS` and `config.SOURCES`.
3. Write `prompts/codebook_<L1|L2|L3|L4>_<en|ru|tr>.md`: codebook v1.0 §1.3 + golden rule +
   the layer section. RU/TR versions: translated and back-checked by the annotators.
4. Have the annotators check the RU/TR sentences in `prompts/wrappers.json`.
5. Run `s1_main_grid.py --dev`, read the raw outputs, then freeze prompts (pre-registration).
