#!/usr/bin/env python3
"""
phase6_preprocess.py — Phase 6 Preprocessing Pipeline (E-ICTT v2.1)

Transformasi teks bersih -> siap tokenisasi IndoBERT, dengan PRINSIP no-information-loss:
kolom `text` (original) dan SEMUA kolom existing dipertahankan; transformasi ditaruh di
kolom BARU.

Kolom baru (disisipkan setelah `text`):
  - text_clean       : case-folded + URL/mention/hashtag/emoji handling (untuk IndoBERT).
                       TIDAK buang stopword, TIDAK stemming (BERT butuh konteks penuh).
  - text_normalized  : text_clean + normalisasi slang ID (gw->saya, gak->tidak).
                       Slang cybercrime (gacor, rungkad, maxwin, dll) DIPERTAHANKAN.
  - text_stemmed     : text_normalized + stemming Sastrawi (kolom terpisah, untuk fitur
                       Tier-2 non-BERT). Tag & slang cybercrime dilindungi dari stemming.

Komponen (roadmap Bagian 8.2):
  1. Case folding                    -> lowercase
  2. URL/mention/hashtag             -> [URL] / [USER] / ekstrak kata hashtag
  3. Emoji                           -> emosi informatif jadi tag, decorative di-strip
  4. Slang normalization             -> kamus ID, slang cybercrime dipertahankan
  5. Stemming Sastrawi               -> kolom terpisah (opsional)
  6. Stopword                        -> TIDAK dibuang (hanya untuk Tier-2 nanti)

Cara pakai:
  python src/phase6_preprocess.py --preview 15      # dry-run before/after, tidak menulis
  python src/phase6_preprocess.py                    # full run -> data/preprocessed_dataset.csv

Output:
  - data/preprocessed_dataset.csv
  - data/slang_dictionary.csv      (reproducibility, roadmap deliverable 8.3)
"""

import argparse
import os
import re

import emoji
import pandas as pd
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

IN_CSV = os.path.join("data", "unified_dataset.csv")
OUT_CSV = os.path.join("data", "preprocessed_dataset.csv")
SLANG_CSV = os.path.join("data", "slang_dictionary.csv")


# ============================================================
# KAMUS & KONSTANTA
# ============================================================

# Slang umum Indonesia -> bentuk baku. (Hanya yang aman; tidak menyentuh istilah domain.)
SLANG_DICT = {
    "gw": "saya", "gue": "saya", "gua": "saya", "ane": "saya", "aq": "aku",
    "lu": "kamu", "lo": "kamu", "elu": "kamu", "loe": "kamu", "lw": "kamu",
    "gak": "tidak", "ga": "tidak", "gk": "tidak", "nggak": "tidak", "ngga": "tidak",
    "enggak": "tidak", "kaga": "tidak", "kagak": "tidak", "tdk": "tidak", "ndak": "tidak",
    "udh": "sudah", "udah": "sudah", "uda": "sudah", "dah": "sudah", "sdh": "sudah",
    "blm": "belum", "belom": "belum", "blom": "belum",
    "bgt": "sangat", "banget": "sangat", "bngt": "sangat",
    "dgn": "dengan", "yg": "yang", "dr": "dari", "utk": "untuk", "buat": "untuk",
    "krn": "karena", "karna": "karena", "krna": "karena",
    "aja": "saja", "doang": "saja", "klo": "kalau", "kalo": "kalau", "klau": "kalau",
    "gmn": "bagaimana", "gimana": "bagaimana", "gmna": "bagaimana",
    "knp": "kenapa", "knpa": "kenapa", "jd": "jadi", "jgn": "jangan",
    "dpt": "dapat", "org": "orang", "tp": "tetapi", "tpi": "tetapi", "tapi": "tetapi",
    "bs": "bisa", "trs": "terus", "msh": "masih", "emang": "memang", "emg": "memang",
    "bener": "benar", "bnr": "benar", "nih": "ini", "tuh": "itu",
    "kyk": "seperti", "kayak": "seperti", "kek": "seperti",
    "cuma": "hanya", "cmn": "hanya", "cman": "hanya",
    "skrg": "sekarang", "skg": "sekarang", "hrs": "harus", "lgi": "lagi",
    "pdhl": "padahal", "sm": "sama", "dpet": "dapat", "dapet": "dapat",
    "ngapain": "mengapa", "gpp": "tidak apa apa", "gapapa": "tidak apa apa",
    "bgs": "bagus", "trus": "terus",
    "tf": "transfer", "trf": "transfer", "abis": "habis", "rek": "rekening",
}
# Catatan: filler (sih/deh/dong/wkwk) sengaja TIDAK dihapus — itu pembuangan
# konteks, bukan normalisasi. text_clean tetap menyimpan semuanya untuk BERT.

# Slang/istilah domain cybercrime yang BERMAKNA -> JANGAN dinormalisasi/di-stem.
CYBER_PRESERVE = {
    "gacor", "maxwin", "rungkad", "jackpot", "jp", "wd", "withdraw", "scatter",
    "zeus", "olympus", "mahjong", "gates", "depo", "deposit", "cuan", "wede",
    "judol", "judi", "slot", "togel", "pinjol", "soceng", "sniffing",
    "phising", "phishing", "deepfake", "otp", "qris", "apk", "malware", "trojan",
    "bjorka", "doxing", "doxxing", "galbay", "gestun", "carding", "fraud", "scam",
    "gopay", "ovo", "dana", "shopeepay", "linkaja", "spaylater", "ewallet",
}

# Emoji informatif -> tag emosi/semantik (relevan untuk diskursus scam).
EMOJI_TAG = {}
for ch in "😢😭😥😪😞😔🥺😟😓😿💔": EMOJI_TAG[ch] = "[EMOSI_SEDIH]"
for ch in "😡😠🤬👿💢😤": EMOJI_TAG[ch] = "[EMOSI_MARAH]"
for ch in "💸💰💵💴💶💷🤑🪙💳": EMOJI_TAG[ch] = "[EMOSI_UANG]"
for ch in "😱😨😰😳🫣😖😬": EMOJI_TAG[ch] = "[EMOSI_TAKUT]"
for ch in "⚠️🚨❗‼️": EMOJI_TAG[ch] = "[EMOSI_WASPADA]"

# Regex
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)", re.UNICODE)
WS_RE = re.compile(r"\s+")
TAG_RE = re.compile(r"\[(?:URL|USER|EMOSI_[A-Z]+)\]")
_slang_keys = sorted(SLANG_DICT.keys(), key=len, reverse=True)
SLANG_RE = re.compile(r"\b(" + "|".join(map(re.escape, _slang_keys)) + r")\b")

_stemmer = StemmerFactory().create_stemmer()
_stem_cache = {}


# ============================================================
# TAHAP TRANSFORMASI
# ============================================================

def clean_text(raw):
    """Case fold + URL/mention/hashtag + emoji. Output siap BERT (konteks penuh)."""
    t = str(raw).lower()
    t = URL_RE.sub(" [URL] ", t)
    t = MENTION_RE.sub(" [USER] ", t)
    t = HASHTAG_RE.sub(r" \1 ", t)          # #judol -> judol
    # Emoji informatif -> tag, sisanya (decorative) strip
    for ch, tag in EMOJI_TAG.items():
        if ch in t:
            t = t.replace(ch, f" {tag} ")
    t = emoji.replace_emoji(t, replace="")
    t = WS_RE.sub(" ", t).strip()
    return t


def normalize_slang(text_clean):
    """Slang ID -> baku. Tag (uppercase) & slang cybercrime tidak tersentuh."""
    out = SLANG_RE.sub(lambda m: SLANG_DICT[m.group(1)], text_clean)
    return WS_RE.sub(" ", out).strip()


def _stem_word(w):
    if w in _stem_cache:
        return _stem_cache[w]
    s = _stemmer.stem(w)
    _stem_cache[w] = s
    return s


def stem_text(text_normalized):
    """Stemming Sastrawi per-kata (cached). Tag & slang cybercrime dilindungi."""
    toks = text_normalized.split()
    out = []
    for tok in toks:
        if tok.startswith("[") or tok in CYBER_PRESERVE or not tok.isalpha():
            out.append(tok)
        else:
            out.append(_stem_word(tok))
    return " ".join(out)


def preprocess_value(raw):
    c = clean_text(raw)
    n = normalize_slang(c)
    s = stem_text(n)
    return c, n, s


# ============================================================
# PREVIEW (before/after, tanpa menulis)
# ============================================================

def pick_preview_rows(df, n=15):
    """Pilih baris beragam agar tiap komponen transformasi terlihat."""
    picks, seen = [], set()

    def add(mask, k):
        for idx in df[mask].index:
            if idx not in seen:
                seen.add(idx)
                picks.append(idx)
                k -= 1
                if k == 0:
                    break

    txt = df["text"].astype(str)
    add(txt.str.contains(r"https?://|t\.co", case=False, regex=True, na=False), 2)
    add(txt.str.contains("@", regex=False, na=False), 2)
    add(txt.str.contains("#", regex=False, na=False), 2)
    add(txt.apply(lambda x: emoji.emoji_count(x) > 0), 3)
    add(txt.str.contains(r"\b(?:gw|gue|gak|bgt|udah|aja|kalo|emang)\b",
                         case=False, regex=True, na=False), 3)
    add(txt.str.contains(r"\b(?:gacor|maxwin|pinjol|judol|rungkad|scatter)\b",
                         case=False, regex=True, na=False), 2)
    # sisanya random
    rest = [i for i in df.sample(frac=1, random_state=11).index if i not in seen]
    for i in rest:
        if len(picks) >= n:
            break
        picks.append(i)
    return picks[:n]


def run_preview(df, n):
    idxs = pick_preview_rows(df, n)
    print(f"=== PREVIEW {len(idxs)} baris (before/after) — TIDAK menulis file ===\n")
    for k, i in enumerate(idxs, 1):
        raw = str(df.at[i, "text"])
        c, nm, s = preprocess_value(raw)
        oneline = lambda x: WS_RE.sub(" ", x.replace("\n", " ").replace("\r", " "))
        print(f"[{k}] uid={df.at[i, 'unified_id']}  hint={df.at[i, 'vector_hint'] or 'NO_HINT'}")
        print(f"    text       : {oneline(raw)[:160]}")
        print(f"    clean      : {c[:160]}")
        print(f"    normalized : {nm[:160]}")
        print(f"    stemmed    : {s[:160]}")
        print()


# ============================================================
# MAIN
# ============================================================

def save_slang_dict():
    rows = [{"slang": k, "baku": v if v else "(dihapus)"} for k, v in SLANG_DICT.items()]
    pd.DataFrame(rows).to_csv(SLANG_CSV, index=False, lineterminator="\n")


def run_full(df, out_csv=OUT_CSV, write_slang=True):
    print(f"[full] memproses {len(df):,} baris ...")
    cleans, norms, stems = [], [], []
    for i, raw in enumerate(df["text"].astype(str)):
        c, n, s = preprocess_value(raw)
        cleans.append(c); norms.append(n); stems.append(s)
        if (i + 1) % 10000 == 0:
            print(f"      {i + 1:,} / {len(df):,}")

    # Sisipkan kolom baru tepat setelah `text` (kolom existing tetap, urutan terjaga)
    pos = df.columns.get_loc("text") + 1
    df.insert(pos, "text_clean", cleans)
    df.insert(pos + 1, "text_normalized", norms)
    df.insert(pos + 2, "text_stemmed", stems)

    df.to_csv(out_csv, index=False, lineterminator="\n")
    if write_slang:
        save_slang_dict()
        print(f"Kamus slang: {SLANG_CSV} ({len(SLANG_DICT)} entri)")
    print(f"\nSelesai. Output: {out_csv} ({len(df):,} baris, {len(df.columns)} kolom)")
    print(f"Kolom: {list(df.columns)}")


def main():
    ap = argparse.ArgumentParser(description="Phase 6 Preprocessing")
    ap.add_argument("--preview", type=int, default=0,
                    help="Tampilkan N baris before/after lalu berhenti (tidak menulis)")
    ap.add_argument("--input", default=IN_CSV, help=f"CSV input (default: {IN_CSV})")
    ap.add_argument("--output", default=OUT_CSV, help=f"CSV output (default: {OUT_CSV})")
    args = ap.parse_args()

    # Baca semua kolom sebagai string -> kolom existing byte-stable di output.
    df = pd.read_csv(args.input, dtype=str, keep_default_na=False)
    assert "text" in df.columns

    if args.preview > 0:
        run_preview(df, args.preview)
    else:
        # Slang dict hanya ditulis pada run default (jangan sentuh artefak v1 saat v2).
        run_full(df, out_csv=args.output, write_slang=(args.output == OUT_CSV))


if __name__ == "__main__":
    main()
