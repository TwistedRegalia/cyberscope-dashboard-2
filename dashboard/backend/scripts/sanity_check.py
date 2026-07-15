"""M0 sanity check (CLAUDE.md Sec 10) - reproduce Model A & Model B macro-F1 on their test splits.

Loads each checkpoint via the original model classes in src/, evaluates on
data/splits/layer{1,2}_test.csv using the src/ evaluate() functions unchanged,
and gates on macro-F1 vs the targets measured at training time (A ~0.968, B ~0.977).
If the gate fails, something is misaligned (layer attribute names, LABEL2ID order,
max_len) and no downstream pipeline work should proceed.

Usage:
    python scripts/sanity_check.py [--device cpu|cuda] [--batch-size 16]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

TARGETS = {"a": 0.968, "b": 0.977}
TOLERANCE = 0.005

DIAGNOSTIC_HINT = """
GAGAL sanity check -- kemungkinan penyebab (CLAUDE.md Sec 10):
  - nama atribut layer tidak selaras (bert / bigru / bilstm / classifier)
  - urutan LABEL2ID salah (lihat ID2LABEL di src/phase9_model_{a,b}_layer{1,2}.py)
  - max_len bukan 128
Jangan lanjut ke M1 sebelum ini diperbaiki.
""".strip()


def run_model_a(device: str, batch_size: int) -> dict:
    from src.phase9_model_a_layer1 import make_model_class, build_dataset, evaluate
    import pandas as pd
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    ckpt = REPO_ROOT / "models" / "model_a_layer1_best.pt"
    test_csv = REPO_ROOT / "data" / "splits" / "layer1_test.csv"

    tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
    model = make_model_class()()
    model.load_state_dict(torch.load(ckpt, map_location=device))
    model.eval().to(device)

    df = pd.read_csv(test_csv)
    ds = build_dataset(df, tokenizer, max_len=128)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)

    return evaluate(model, loader, device)


def run_model_b(device: str, batch_size: int) -> dict:
    from src.phase9_model_b_layer2 import make_model_class, build_dataset, evaluate
    import pandas as pd
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer

    ckpt = REPO_ROOT / "models" / "model_b_layer2_best.pt"
    test_csv = REPO_ROOT / "data" / "splits" / "layer2_test.csv"

    tokenizer = AutoTokenizer.from_pretrained("indobenchmark/indobert-base-p1")
    model = make_model_class()()

    # Checkpoint was trained via the Kaggle cell with the final layer named
    # `clf`; the committed src/phase9_model_b_layer2.py names it `classifier`.
    # All other 215 keys (bert/bigru/bilstm/dropout) match exactly and the
    # clf/classifier weight+bias shapes match exactly (6,256)/(6,) -> pure
    # rename, safe to remap. See M0 sanity check finding (2026-07-15).
    state_dict = torch.load(ckpt, map_location=device)
    state_dict = {
        (k.replace("clf.", "classifier.", 1) if k.startswith("clf.") else k): v
        for k, v in state_dict.items()
    }
    model.load_state_dict(state_dict)
    model.eval().to(device)

    df = pd.read_csv(test_csv)
    ds = build_dataset(df, tokenizer, max_len=128)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False)

    return evaluate(model, loader, device)


def main() -> None:
    parser = argparse.ArgumentParser(description="M0 sanity check - CLAUDE.md Sec 10")
    parser.add_argument("--device", default=None, help="cpu|cuda (default: auto-detect)")
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    import torch

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device}")

    runners = (
        ("a", "Model A (Layer 1)", run_model_a),
        ("b", "Model B (Layer 2)", run_model_b),
    )

    overall_pass = True
    for key, label, runner in runners:
        print(f"\n=== {label} ===")
        t0 = time.time()
        metrics = runner(device, args.batch_size)
        elapsed = time.time() - t0
        macro_f1 = metrics["macro_f1"]
        target = TARGETS[key]
        passed = abs(macro_f1 - target) <= TOLERANCE
        overall_pass = overall_pass and passed

        print(f"accuracy       = {metrics['accuracy']:.4f}")
        print(f"macro_f1       = {macro_f1:.4f}  (target {target:.3f} +/- {TOLERANCE})")
        if "recall_relevan" in metrics:
            print(f"recall_relevan = {metrics['recall_relevan']:.4f}")
        if "report" in metrics:
            print(metrics["report"])
        print(f"elapsed        = {elapsed:.1f}s")
        print(f"verdict        = {'PASS' if passed else 'FAIL'}")

    print("\n" + "=" * 40)
    if overall_pass:
        print("GERBANG M0: PASS -- checkpoint + arsitektur selaras, aman lanjut ke M1.")
        sys.exit(0)
    else:
        print("GERBANG M0: FAIL")
        print(DIAGNOSTIC_HINT)
        sys.exit(1)


if __name__ == "__main__":
    main()
