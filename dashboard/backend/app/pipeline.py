"""Inference pipeline: preprocess -> Model A gate (fusion L1) -> Model B (fusion L2) -> classify().

Reuses the checkpoints + model classes verified in scripts/sanity_check.py (M0).
Not an HTTP layer (see app/main.py, M2) - just classify(text) -> dict matching
CLAUDE.md Sec 5 / docs/HANDOFF_FRONTEND.md Sec 4.1 ClassifyResponse.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from src.anchor_patterns import detect_vector_hints, has_anchor  # noqa: E402
from src.phase6_preprocess import clean_text  # noqa: E402
from src.phase9_model_a_layer1 import (  # noqa: E402
    LABEL2ID as A_LABEL2ID,
    make_model_class as make_model_a,
)
from src.phase9_model_b_layer2 import (  # noqa: E402
    LABEL2ID as B_LABEL2ID,
    make_model_class as make_model_b,
)

BERT_NAME = "indobenchmark/indobert-base-p1"
MAX_LEN = 128
W_NEURAL = 0.75
W_RULE = 0.25

LABEL_DISPLAY = {
    "phishing_rekayasa_sosial": "Phishing & Rekayasa Sosial",
    "penipuan_ewallet_qris": "Penipuan E-Wallet/QRIS",
    "malware_apk": "Malware APK",
    "judi_online_pinjol": "Judi Online & Pinjol",
    "peretasan_pencurian_identitas": "Peretasan & Pencurian Identitas",
    "deepfake_penipuan_ai": "Deepfake & Penipuan AI",
}

_state: dict = {"loaded": False}


def is_loaded() -> bool:
    return _state["loaded"]


def load_models() -> None:
    import torch
    from transformers import AutoTokenizer

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(BERT_NAME)

    model_a = make_model_a()()
    model_a.load_state_dict(
        torch.load(REPO_ROOT / "models" / "model_a_layer1_best.pt", map_location=device)
    )
    model_a.eval().to(device)

    model_b = make_model_b()()
    # Checkpoint's final layer is named `clf` (Kaggle training cell); the committed
    # src/phase9_model_b_layer2.py names it `classifier`. Shapes match exactly (see
    # M0 sanity check, scripts/sanity_check.py) - safe rename-only remap.
    state_dict_b = torch.load(
        REPO_ROOT / "models" / "model_b_layer2_best.pt", map_location=device
    )
    state_dict_b = {
        (k.replace("clf.", "classifier.", 1) if k.startswith("clf.") else k): v
        for k, v in state_dict_b.items()
    }
    model_b.load_state_dict(state_dict_b)
    model_b.eval().to(device)

    _state.update(
        device=device,
        tokenizer=tokenizer,
        model_a=model_a,
        model_b=model_b,
        loaded=True,
    )


def _softmax(model, tokenizer, device, text_clean: str):
    import torch

    enc = tokenizer(
        text_clean,
        truncation=True,
        padding="max_length",
        max_length=MAX_LEN,
        return_tensors="pt",
    )
    with torch.no_grad():
        logits = model(enc["input_ids"].to(device), enc["attention_mask"].to(device))
    return torch.softmax(logits, dim=1)[0].tolist()


def classify(text: str) -> dict:
    t0 = time.time()
    if not _state["loaded"]:
        load_models()

    device = _state["device"]
    tokenizer = _state["tokenizer"]
    text_clean = clean_text(text)

    # Layer 1: relevance gate, fused 0.75 neural : 0.25 rule-based (CLAUDE.md Sec 4)
    p_a = _softmax(_state["model_a"], tokenizer, device, text_clean)  # [p_tidak, p_relevan]
    anchor2 = [0.0, 1.0] if has_anchor(text_clean) else [0.0, 0.0]
    fused_l1 = [W_NEURAL * p_a[i] + W_RULE * anchor2[i] for i in range(2)]
    relevant = (0 if fused_l1[0] >= fused_l1[1] else 1) == A_LABEL2ID["relevan"]

    if not relevant:
        return {
            "relevant": False,
            "label": None,
            "label_display": None,
            "confidence": 0.0,
            "probabilities": {v: 0.0 for v in B_LABEL2ID},
            "latency_ms": int((time.time() - t0) * 1000),
        }

    # Layer 2: 6-vector classification, fused 0.75 neural : 0.25 anchor share
    p_b = _softmax(_state["model_b"], tokenizer, device, text_clean)
    hints = detect_vector_hints(text_clean)
    total_hints = sum(hints.values())
    anchor_share = {
        v: (hints.get(v, 0) / total_hints if total_hints else 0.0) for v in B_LABEL2ID
    }

    fused = {v: W_NEURAL * p_b[idx] + W_RULE * anchor_share[v] for v, idx in B_LABEL2ID.items()}
    total_fused = sum(fused.values()) or 1.0
    probabilities = {v: fused[v] / total_fused for v in fused}
    label = max(probabilities, key=probabilities.get)
    confidence = probabilities[label]

    return {
        "relevant": True,
        "label": label,
        "label_display": LABEL_DISPLAY[label],
        "confidence": confidence,
        "probabilities": probabilities,
        "latency_ms": int((time.time() - t0) * 1000),
    }
