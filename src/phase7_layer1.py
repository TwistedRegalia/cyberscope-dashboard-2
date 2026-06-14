#!/usr/bin/env python3
"""
phase7_layer1.py — Snorkel Layer 1 (Relevance Filter): relevan vs tidak_relevan

Arsitektur (keputusan Ray): binary LabelModel.
  - POSITIF (RELEVAN): reuse anchor v1.1 (anchor_patterns.PATTERNS) sbg 6 LF
    per-vektor. Sudah ter-refine, morfologi SUF fixed -> JANGAN bangun ulang.
    Overlap antar-LF positif (konten multi-vektor) memberi LabelModel pola
    agreement untuk belajar.
  - NEGATIF (TIDAK_RELEVAN): LF baru yang AKTIF menandai noise NO_HINT
    (emosional, off-topic pendek, cybersec generik, jual-beli fraud).
    Ini menjawab Temuan #4: keputusan relevansi = tugas Snorkel, bukan anchor.

Input LF = text_clean. Negatif di-gate pada absennya anchor agar tidak
menimbulkan konflik palsu pada baris yang sebenarnya relevan.

Ref: docs/00_Annotation_Guidelines_ICTT_v2.1.md Bagian 3 (Layer 1).
"""
import re
import sys
sys.path.insert(0, "src")
import anchor_patterns as ap
from snorkel.labeling import labeling_function

# Label space Layer 1
ABSTAIN       = -1
TIDAK_RELEVAN = 0
RELEVAN       = 1

_F = re.IGNORECASE | re.UNICODE

def _txt(x):
    t = getattr(x, "text_clean", "")
    return t if isinstance(t, str) else ""

# Precompile pattern per vektor dari anchor v1.1 (reuse)
_VEC_PATTERNS = {v: [re.compile(p, _F) for p in pats] for v, pats in ap.PATTERNS.items()}

def _vec_match(t, vec):
    return any(rx.search(t) for rx in _VEC_PATTERNS[vec])

def _has_any_anchor(t):
    return ap.has_anchor(t)

# ============================================================
# POSITIF — 6 LF relevansi per-vektor (vote RELEVAN)
# ============================================================
@labeling_function()
def lf_rel_phishing(x):
    return RELEVAN if _vec_match(_txt(x), "phishing_rekayasa_sosial") else ABSTAIN

@labeling_function()
def lf_rel_ewallet(x):
    return RELEVAN if _vec_match(_txt(x), "penipuan_ewallet_qris") else ABSTAIN

@labeling_function()
def lf_rel_malware(x):
    return RELEVAN if _vec_match(_txt(x), "malware_apk") else ABSTAIN

@labeling_function()
def lf_rel_judi(x):
    return RELEVAN if _vec_match(_txt(x), "judi_online_pinjol") else ABSTAIN

@labeling_function()
def lf_rel_peretasan(x):
    return RELEVAN if _vec_match(_txt(x), "peretasan_pencurian_identitas") else ABSTAIN

@labeling_function()
def lf_rel_deepfake(x):
    return RELEVAN if _vec_match(_txt(x), "deepfake_penipuan_ai") else ABSTAIN

# ============================================================
# NEGATIF — LF tidak_relevan (vote TIDAK_RELEVAN), di-gate pada no-anchor
# ============================================================
def _wc(t):
    return len(t.split())

# tr_emosional: reaksi/afirmasi murni tanpa substansi
_RE_EMOSI = re.compile(
    r"\b(?:ngeri|serem|seram|seram|kacau|gila|parah|anjir|anjay|anjg|wkwk+|wkawk|hadeh|"
    r"semangat|smangat|mantap|mantul|mantab|keren|bagus|amin|aamiin|amiin|sedih|kasian|"
    r"kasihan|miris|astaga|ya\s*ampun|gokil|wow|wah|hebat|salut|setuju|bener\s*bang|"
    r"pokonya|pokoknya|gas|gaskeun|lanjutkan|sabar|turut\s*berduka|innalillahi)\b", _F)

@labeling_function()
def lf_tr_emosional(x):
    """tr_emosional — reaksi/afirmasi pendek tanpa anchor vektor."""
    t = _txt(x)
    if _wc(t) <= 8 and _RE_EMOSI.search(t) and not _has_any_anchor(t):
        return TIDAK_RELEVAN
    return ABSTAIN

# tr_offtopic_pendek: sangat pendek, sapaan/afirmasi, tanpa anchor
_RE_SAPAAN = re.compile(r"\b(?:pagi|halo|hai|hello|assalamualaikum|p\b|izin|nyimak|hadir|absen|first|pertamax|up\b|naikin|sundul)\b", _F)

@labeling_function()
def lf_tr_offtopic_pendek(x):
    """tr_offtopic — komentar sangat pendek (<=4 kata) sapaan/nyimak, no anchor."""
    t = _txt(x)
    if _wc(t) <= 4 and not _has_any_anchor(t):
        if _RE_SAPAAN.search(t) or _RE_EMOSI.search(t):
            return TIDAK_RELEVAN
    return ABSTAIN

# tr_generik_siber: cybersec generik tanpa anchor vektor spesifik
_RE_GENERIK_SIBER = re.compile(
    r"(?:jaga|lindungi|amankan|hati[\s-]*hati\s*(?:dengan|sama)?\s*)?(?:data\s*pribadi|keamanan\s*(?:digital|siber|online)|privasi)\b", _F)

@labeling_function()
def lf_tr_generik_siber(x):
    """tr_generik_siber — himbauan keamanan generik tanpa anchor vektor (mis. 'ayo jaga data pribadi')."""
    t = _txt(x)
    if _RE_GENERIK_SIBER.search(t) and not _has_any_anchor(t):
        return TIDAK_RELEVAN
    return ABSTAIN

# tr_jualbeli: penipuan jual-beli online -> tidak_relevan (keputusan Ray),
# kecuali ada anchor phishing sejati (OTP/kredensial/ngaku-institusi/link-verif).
_RE_JUALBELI = re.compile(
    r"\b(?:beli|jual|jual\s*beli|jualbeli|order(?:an)?|pre\s*order|\bpo\b|cod|wts|wtb|wtt|seller|olshop|"
    r"toko\s*online|thrift|thrif|second|seken|preloved|tiket|reservasi|booking|jastip|jasa\s*titip|"
    r"barang\s*(?:gak|ga|tidak|belum)\s*(?:sampai|dateng|nyampe|dikirim|datang)|resi\s*(?:palsu|fiktif|gak))\b", _F)
_RE_PHISH_ANCHOR = re.compile(
    r"(?:otp|password|\bpin\b|kode\s*(?:verif|otp|rahasia)|sandi|ngaku\W{0,20}(?:bank|bca|bri|cs|shopee|dana|ovo)|"
    r"link\W{0,15}(?:verif|palsu|phising|phishing|mencurigakan))", _F)

@labeling_function()
def lf_tr_jualbeli(x):
    """tr_jualbeli — penipuan transaksi jual-beli online tanpa anchor phishing -> tidak_relevan."""
    t = _txt(x)
    if _RE_JUALBELI.search(t) and not _RE_PHISH_ANCHOR.search(t):
        # tapi jangan buang kalau ada anchor vektor LAIN yang kuat (mis. judol/pinjol/apk)
        if not _has_any_anchor(t):
            return TIDAK_RELEVAN
    return ABSTAIN

POSITIVE_LFS = [lf_rel_phishing, lf_rel_ewallet, lf_rel_malware,
                lf_rel_judi, lf_rel_peretasan, lf_rel_deepfake]
NEGATIVE_LFS = [lf_tr_emosional, lf_tr_offtopic_pendek, lf_tr_generik_siber, lf_tr_jualbeli]
LAYER1_LFS = POSITIVE_LFS + NEGATIVE_LFS
