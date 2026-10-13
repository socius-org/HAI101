"""Step 2: embed each unique abstract once with sentence-transformers, cached on disk by text hash."""
import hashlib
import json
from pathlib import Path

import numpy as np

DEFAULT_MODEL = "allenai/specter2_base"
FALLBACK_MODEL = "all-mpnet-base-v2"


def text_hash(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def load_model(name):
    from sentence_transformers import SentenceTransformer, models

    if "specter" in name.lower():
        # SPECTER models are plain HF checkpoints that expect CLS pooling, not the mean pooling
        # sentence-transformers would default to.
        transformer = models.Transformer(name, max_seq_length=512)
        pooling = models.Pooling(transformer.get_word_embedding_dimension(), pooling_mode="cls")
        return SentenceTransformer(modules=[transformer, pooling])
    return SentenceTransformer(name)


def embed_abstracts(abstracts, model_name=DEFAULT_MODEL, cache_dir="cache", batch_size=16):
    """Returns (matrix aligned with `abstracts`, model name actually used). Normalized rows."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    npy, meta_path = cache_dir / "embeddings.npy", cache_dir / "embeddings.json"

    cache = {}
    if npy.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        if meta.get("model") == model_name:
            cache = dict(zip(meta["hashes"], np.load(npy)))
            print(f"[embed] cache: {len(cache)} embeddings for {model_name}")

    hashes = [text_hash(a) for a in abstracts]
    todo = [a for a, h in zip(abstracts, hashes) if h not in cache]
    todo = list(dict.fromkeys(todo))
    used = model_name
    if todo:
        print(f"[embed] encoding {len(todo)} new abstracts with {model_name}")
        try:
            model = load_model(model_name)
        except Exception as e:  # model missing / download failed
            print(f"[embed] could not load {model_name} ({type(e).__name__}: {e}); using {FALLBACK_MODEL}")
            used = FALLBACK_MODEL
            model = load_model(used)
            if (meta_path.exists() and json.loads(meta_path.read_text()).get("model") == used):
                cache = dict(zip(json.loads(meta_path.read_text())["hashes"], np.load(npy)))
                todo = list(dict.fromkeys(a for a, h in zip(abstracts, hashes) if h not in cache))
            else:
                cache = {}
        if todo:
            vecs = model.encode(todo, batch_size=batch_size, normalize_embeddings=True,
                                show_progress_bar=True, convert_to_numpy=True)
            for a, v in zip(todo, vecs):
                cache[text_hash(a)] = v.astype(np.float32)
            keys = list(cache)
            np.save(npy, np.stack([cache[k] for k in keys]))
            meta_path.write_text(json.dumps({"model": used, "hashes": keys}))
            print(f"[embed] cache now holds {len(keys)} embeddings -> {npy}")
    return np.stack([cache[h] for h in hashes]), used
