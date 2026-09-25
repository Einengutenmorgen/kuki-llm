"""Building blocks shared by all experiment scripts: paragraphs, prompts, output
schemas, local generation with Hugging Face transformers and a resumable job runner.

Every experiment uses these functions, so prompts and decoding settings are
identical across experiments.
"""
import hashlib
import json
import random
import time
from functools import lru_cache
from itertools import product

import pandas as pd
import os
os.environ["Cuda_VISIBLE_DEVICES"] = "2" 
import torch
from lmformatenforcer import JsonSchemaParser
from lmformatenforcer.integrations.transformers import (
    build_token_enforcer_tokenizer_data, build_transformers_prefix_allowed_tokens_fn)
from transformers import AutoModelForCausalLM, AutoTokenizer

import config

MAX_NEW_TOKENS = 2048
KEY_FIELDS = ["experiment", "model", "article_id", "layer", "granularity",
              "prompt_lang", "metadata", "target", "sample"]


# ---------- data ----------

def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def paragraphs(content):
    """Split the content field into paragraphs (at blank lines) with character offsets.
    Empty blocks are skipped."""
    out, pos = [], 0
    for part in content.split("\n\n"):
        if part.strip():
            out.append({"start": pos, "end": pos + len(part), "text": part})
        pos += len(part) + 2
    return out


def load_split(name):
    """Articles of one split (see prep_01_make_splits.py) with the split columns attached."""
    articles = {a["article_id"]: a for a in read_jsonl(config.PREP_DIR / "articles.jsonl")}
    split = pd.read_csv(config.SPLIT_DIR / f"{name}.csv")
    return [{**articles[row["article_id"]], **row} for row in split.to_dict("records")]


# ---------- prompts ----------

@lru_cache
def load_codebook(layer, lang):
    """System prompt = the codebook text for one layer (general rules + layer section)."""
    path = config.PROMPT_DIR / f"codebook_{layer}_{lang}.md"
    if not path.exists():
        raise FileNotFoundError(f"{path} missing: paste the codebook v1.0 text for {layer} ({lang})")
    return path.read_text(encoding="utf-8")


@lru_cache
def load_wrappers():
    """Short task sentences around the article, one set per prompt language."""
    wrappers = json.loads((config.PROMPT_DIR / "wrappers.json").read_text(encoding="utf-8"))
    for lang, texts in wrappers.items():
        if any("TODO" in t for t in texts.values()):
            raise ValueError(f"wrappers.json: '{lang}' still contains TODO")
    return wrappers


def entity_names(article):
    return [e["display"] for e in article["entities"]]


def build_messages(article, layer, granularity, prompt_lang, target=None, meta=None):
    """Chat messages for one call. Order (codebook -> article -> target) keeps a long
    shared prefix across the paragraph calls of one article."""
    lang = article["lang"] if prompt_lang == "native" else "en"
    w = load_wrappers()[lang]
    paras = paragraphs(article["content"])
    full_article = "\n\n".join(f"[P{i}] {p['text']}" for i, p in enumerate(paras))

    parts = []
    if meta:
        parts.append(w["meta"].format(**meta))
    if granularity == "doc":
        parts += [w["task_doc"], full_article]
    elif granularity == "para":
        parts += [w["task_para"], f"[P{target}] {paras[target]['text']}"]
    elif granularity == "para_ctx":
        parts += [w["context_header"], full_article,
                  w["task_para_ctx"].format(i=target), f"[P{target}] {paras[target]['text']}"]
    else:
        raise ValueError(f"unknown granularity {granularity}")
    if layer == "L1":
        parts.append(w["entities_header"] + "\n" + "\n".join(entity_names(article)))
    parts.append(w["output"])

    return [{"role": "system", "content": load_codebook(layer, lang)},
            {"role": "user", "content": "\n\n".join(parts)}]


def output_schema(layer, entities=None):
    """JSON schema enforced by guided decoding. Label identifiers are always the English
    codebook labels, so outputs are comparable across prompt languages."""
    if layer == "L1":
        key, item = "roles", {"type": "object", "required": ["entity", "role"], "properties": {
            "entity": {"type": "string", "enum": entities},
            "role": {"type": "string", "enum": config.ROLES}}}
    elif layer == "L2":
        key, item = "frames", {"type": "string", "enum": config.FRAMES}
    elif layer == "L3":
        key, item = "techniques", {"type": "object", "required": ["category", "paragraph", "quote"], "properties": {
            "category": {"type": "string", "enum": config.PERSUASION},
            "paragraph": {"type": "integer"},
            "quote": {"type": "string"}}}
    elif layer == "L4":
        key, item = "coded", {"type": "object", "required": ["paragraph", "quote", "insider_meaning"], "properties": {
            "paragraph": {"type": "integer"},
            "quote": {"type": "string"},
            "insider_meaning": {"type": "string"}}}
    else:
        raise ValueError(f"unknown layer {layer}")
    return {"type": "object", "required": [key], "properties": {key: {"type": "array", "items": item}}}


# ---------- jobs ----------

def make_jobs(experiment, articles, model, layers, granularities, prompt_langs,
              metadata_modes=("none",), n_samples=1, temperature=0.0):
    """One job = one LLM call. Paragraph granularities create one job per paragraph."""
    jobs = []
    for a, layer, gran, prompt_lang, meta in product(articles, layers, granularities, prompt_langs, metadata_modes):
        if layer == "L1" and not a["entities"]:
            continue  # no human-marked entities -> nothing to assign roles to
        if gran == "doc":
            targets = [None]
        else:
            targets = range(a["n_paragraphs"])
        for target, sample in product(targets, range(n_samples)):
            job = {"experiment": experiment, "model": model, "lang": a["lang"],
                   "article_id": a["article_id"], "layer": layer, "granularity": gran,
                   "prompt_lang": prompt_lang, "metadata": meta, "target": target,
                   "sample": sample, "temperature": temperature}
            job["key"] = "|".join(str(job[k]) for k in KEY_FIELDS)
            job["article"] = a
            jobs.append(job)
    return jobs


def mock_output(schema, key):
    """Random but schema-valid answer (deterministic per job) for pipeline tests."""
    rng = random.Random(key)
    field, spec = next(iter(schema["properties"].items()))
    item = spec["items"]

    def one():
        if "enum" in item:
            return rng.choice(item["enum"])
        return {name: rng.choice(p["enum"]) if "enum" in p else rng.randint(0, 4) if p["type"] == "integer" else "mock"
                for name, p in item["properties"].items()}

    return json.dumps({field: [one() for _ in range(rng.randint(0, 3))]})


def load_model(model):
    """Tokenizer, model and JSON-constraint data for one model alias. Native precision
    (dtype from the checkpoint); device_map='auto' spreads large models over all visible GPUs."""
    cfg = config.MODELS[model]
    if cfg["hf"] == "mock":
        return None
    if cfg["hf"].startswith("TODO"):
        raise ValueError(f"model '{model}' has no checkpoint id in config.MODELS")
    tokenizer = AutoTokenizer.from_pretrained(cfg["hf"])
    llm = AutoModelForCausalLM.from_pretrained(cfg["hf"], dtype="auto", device_map="auto")
    llm.eval()
    return {"tokenizer": tokenizer, "model": llm, "enforcer": build_token_enforcer_tokenizer_data(tokenizer)}

def generate(backend, cfg, messages, schema, job):
    """One constrained generation. Returns (text, finish_reason, tokens_in, tokens_out, error)."""
    tokenizer, llm = backend["tokenizer"], backend["model"]
    encoded = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt",
                                            return_dict=True, **cfg.get("template_kwargs", {}))
    # Keep only what generate() needs (some tokenizers also return token_type_ids, e.g. OLMo).
    inputs = {k: encoded[k].to(llm.device) for k in ("input_ids", "attention_mask")}
    n_in = inputs["input_ids"].shape[1]
    if n_in + MAX_NEW_TOKENS > llm.config.max_position_embeddings:
        return None, None, n_in, 0, "prompt too long for the context window"

    # Decoding is set explicitly, so model-specific defaults in generation_config
    # (e.g. top_p, top_k, repetition_penalty) cannot differ between models.
    decoding = {"do_sample": False, "repetition_penalty": 1.0}
    if job["temperature"] > 0:
        decoding.update(do_sample=True, temperature=job["temperature"], top_p=1.0, top_k=0)
    torch.manual_seed(config.SEED + job["sample"])
    allowed = build_transformers_prefix_allowed_tokens_fn(backend["enforcer"], JsonSchemaParser(schema))
    try:
        with torch.no_grad():
            out = llm.generate(**inputs, max_new_tokens=MAX_NEW_TOKENS, prefix_allowed_tokens_fn=allowed,
                               pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id, **decoding)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        return None, None, n_in, 0, "out of GPU memory"
    new_tokens = out[0, n_in:]
    finish = "length" if len(new_tokens) >= MAX_NEW_TOKENS else "stop"
    return tokenizer.decode(new_tokens, skip_special_tokens=True), finish, n_in, len(new_tokens), None


def call_llm(backend, job):
    """Run one job and return a flat record (the input article is not stored).

    - answer is not valid JSON (e.g. cut off at MAX_NEW_TOKENS): parse_ok=False -> 'no label'
    - prompt longer than the context window, or out of GPU memory: not generated, stored in
      'error' -> 'no label'. Both fail the same way on a retry, so they are not retried.
    """
    a, layer = job["article"], job["layer"]
    cfg = config.MODELS[job["model"]]
    meta = (a.get("meta") or {}).get(job["metadata"])
    messages = build_messages(a, layer, job["granularity"], job["prompt_lang"], job["target"], meta)
    schema = output_schema(layer, entity_names(a) if layer == "L1" else None)
    if cfg.get("merge_system"):  # some chat templates (e.g. Gemma 2) reject a system role
        messages = [{"role": "user", "content": messages[0]["content"] + "\n\n" + messages[1]["content"]}]

    start = time.time()
    if cfg["hf"] == "mock":
        raw, finish, n_in, n_out, error = mock_output(schema, job["key"]), "stop", None, None, None
    else:
        raw, finish, n_in, n_out, error = generate(backend, cfg, messages, schema, job)

    try:
        parsed = json.loads(raw) if raw else None
    except json.JSONDecodeError:
        parsed = None

    record = {k: v for k, v in job.items() if k != "article"}
    record.update(
        prompt_sha=hashlib.sha1(json.dumps(messages, ensure_ascii=False).encode()).hexdigest()[:12],
        raw=raw, parsed=parsed, parse_ok=parsed is not None, finish_reason=finish, error=error,
        tokens_in=n_in, tokens_out=n_out, seconds=round(time.time() - start, 2))
    return record


def run_jobs(jobs, experiment, model):
    """Run all jobs of one model that are not yet in its output file, one after another,
    appending one JSON line per call. Re-running the same command resumes.
    One file per experiment and model, so two runs on two GPUs never write to the same file."""
    out_path = config.PRED_DIR / f"{experiment}__{model}.jsonl"
    done = set()
    if out_path.exists():
        done = {json.loads(line)["key"] for line in out_path.open(encoding="utf-8")}
    todo = [j for j in jobs if j["key"] not in done]
    print(f"{out_path.name}: {len(jobs)} jobs, {len(jobs) - len(todo)} already done, {len(todo)} to run")
    if not todo:
        return

    backend = load_model(model)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as f:
        for n, job in enumerate(todo, 1):
            f.write(json.dumps(call_llm(backend, job), ensure_ascii=False) + "\n")
            f.flush()
            if n % 100 == 0:
                print(f"  {n}/{len(todo)}")
