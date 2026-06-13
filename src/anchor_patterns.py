#!/usr/bin/env python3
"""
anchor_patterns.py — Pattern library untuk relevance anchor detection
Versi ringkas dari Pattern Library E-ICTT v2.1 untuk Phase 5 (discovery filter).

Fungsi utama:
- has_anchor(text): True jika teks mengandung anchor ke salah satu 6 vektor
- detect_vector_hints(text): dict berisi vektor mana yang ter-trigger (untuk diagnostik)

Catatan: Ini adalah TIER DISCOVERY (longgar, high-recall) untuk filtering.
Pattern presisi tinggi untuk Snorkel labeling functions ada di modul terpisah (Phase 7).
"""

import re

# ============================================================
# PATTERN PER VEKTOR (Tier 1 + 2 + 3 digabung untuk discovery)
# Disusun dari Pattern Library Documentation E-ICTT v2.1
# ============================================================

PATTERNS = {
    "phishing_rekayasa_sosial": [
        r"\b[pf][iy]+s+h*i*n+g*\b",
        r"(?:minta|kasih|kirim|share|berikan|kasi)\W{0,20}(?:otp|kode\W{0,5}(?:verif|otp|rahasia|sms))",
        r"(?:telp(?:on)?|nelpon|ditelp(?:on)?|telepon|telpon)\W{0,30}(?:ngaku|mengaku|katanya|bilang|claim)",
        r"(?:link|tautan|url)\W{0,20}(?:mencurigakan|aneh|gak\s*jelas|phising|tipu|nipu|palsu|bohongan)",
        r"(?:klaim|dapat|menang|dapet)\W{0,15}(?:hadiah|kuota|pulsa|undian|voucher|cashback|reward)",
        r"(?:modus|trik|cara)\W{0,20}(?:penipu(?:an)?|scam|tipu|nipu|fraud)",
        r"\botp\b", r"\brekayasa\s*sosial\b", r"\bsoceng\b", r"\bsocial\s*engineering\b",
    ],
    "penipuan_ewallet_qris": [
        r"\bqris\b\W{0,15}(?:palsu|tempel|fake|bohongan|aspal|tipu|bodong)",
        r"(?:saldo|isi)\W{0,5}(?:ovo|dana|gopay|shopeepay|spaylater|linkaja)\W{0,30}(?:hilang|terkuras|raib|amblas|kuras|kosong|abis)",
        r"(?:salah\s*transfer|salah\s*kirim|kelebihan)\W{0,40}(?:scan|qr|qris)",
        r"(?:ovo|dana|gopay|shopeepay|linkaja)\W{0,30}(?:tipu|nipu|scam|penipu(?:an)?|bobol|hack)",
        r"\bqr(?:is)?\b\W{0,40}(?:parkir(?:an)?|kotak\s*amal|masjid|mushola)",
        r"\bqris\b", r"\be[\s-]*wallet\b", r"\bdompet\s*digital\b",
    ],
    "malware_apk": [
        r"\.?apk\b\W{0,30}(?:undangan|nikah|kurir|j[\s&]*t|jne|sicepat|paket|tilang|surat|kartu)",
        r"\.?apk\b\W{0,30}(?:penipu(?:an)?|tipu|nipu|scam|bahaya|virus|malware|trojan)",
        r"(?:kena|install|pasang|download|terkecoh)\W{0,15}(?:file\s*)?\.?apk\b",
        r"\.?apk\b\W{0,30}(?:wa|whatsapp|telegram|sms|dm|kirim(?:an)?)",
        r"\bsniffing\b", r"\bmalware\b", r"\.apk\b", r"\bapk\b",
    ],
    "judi_online_pinjol": [
        r"\b(?:gacor|maxwin|rungkad|anti[\s-]*rungkad|wd\s*lancar|jp[\s-]*gede)\b",
        r"\b(?:judi\s*online|judol|jdl|judi\s*slot|slot\s*online|casino\s*online|togel\s*online)\b",
        r"\bpinjol\b\W{0,15}(?:ilegal|gak\s*resmi|tidak\s*terdaftar|bodong|nakal|abal)",
        r"(?:diteror|teror|ancam(?:an)?|kasar|galak)\W{0,30}(?:pinjol|debt\s*collector|dc\b|penagih)",
        r"(?:pinjaman|pinjam|hutang|utang)\W{0,15}(?:online|app|aplikasi)",
        r"\bpinjol\b", r"\bjudol\b", r"\bslot\b", r"\bpinjaman\s*online\b", r"\bjudi\b",
    ],
    "peretasan_pencurian_identitas": [
        r"(?:akun)\W{0,20}(?:ig|instagram|wa|whatsapp|fb|facebook|twitter|tiktok|tt|telegram|tg)\W{0,30}(?:diretas|dihack|dibobol|dibajak|dicuri|hilang|kena\s*hack)",
        r"(?:kebocoran|bocor(?:an)?|leak(?:age)?)\W{0,30}(?:data|dukcapil|pdp|pribadi|nik|kk|ktp)",
        r"\b(?:bjorka|breach\s*forums?|raidforums?)\b",
        r"(?:sim[\s-]*swap|tukar\s*sim|nomor\s*diambil\s*alih|nomor\s*dibajak)",
        r"(?:curi|dicuri|pencurian|hilang)\W{0,20}(?:data|identitas|nik|ktp|kk)",
        r"\b(?:doxing|doxxing)\b",
        r"(?:diretas|dihack|dibajak|dibobol)", r"\bhack\b", r"\bretas\b", r"\bpencurian\s*identitas\b",
    ],
    "deepfake_penipuan_ai": [
        r"\b(?:deepfake|deep\s*fake)\b",
        r"(?:voice|suara)\W{0,15}(?:clon(?:e|ing)|cloned|tiruan|palsu\s*ai|generated|ai)",
        r"(?:suara|voice)\W{0,15}(?:mirip|sama|identik|kayak)\W{0,30}(?:anak|ortu|orang\s*tua|saudara|bapak|ibu|mama|papa)",
        r"(?:ai|chat\s*gpt|chatgpt|gemini)\W{0,30}(?:scam|tipu|nipu|penipu(?:an)?|fraud|generated)",
        r"(?:video|klip)\W{0,15}(?:jokowi|prabowo|sri\s*mulyani|menteri|presiden)\W{0,40}(?:promosi|endorse|investasi|crypto)",
        r"\bdeepfake\b", r"\bvoice\s*clon", r"\bai\s*voice\b",
    ],
}

# Compile semua pattern sekali (performance)
COMPILED = {
    vec: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in pats]
    for vec, pats in PATTERNS.items()
}

# Flatten untuk cek anchor cepat (any vektor)
ALL_COMPILED = [pat for pats in COMPILED.values() for pat in pats]


def has_anchor(text):
    """True jika teks mengandung minimal satu anchor vektor."""
    if not isinstance(text, str):
        return False
    for pat in ALL_COMPILED:
        if pat.search(text):
            return True
    return False


def detect_vector_hints(text):
    """
    Mengembalikan dict {vektor: jumlah_match} untuk diagnostik.
    Berguna untuk estimasi distribusi kasar sebelum Snorkel.
    """
    if not isinstance(text, str):
        return {}
    hints = {}
    for vec, pats in COMPILED.items():
        count = sum(1 for pat in pats if pat.search(text))
        if count > 0:
            hints[vec] = count
    return hints


def top_vector_hint(text):
    """
    Mengembalikan vektor dengan match terbanyak (crude pre-label).
    CATATAN: Ini BUKAN label final. Hanya untuk estimasi distribusi.
    Label final ditentukan Snorkel (Phase 7) dengan hierarki prioritas.
    """
    hints = detect_vector_hints(text)
    if not hints:
        return None
    # Hierarki prioritas tie-break (sesuai E-ICTT v2.1 Bagian 5.2)
    priority = [
        "malware_apk",
        "deepfake_penipuan_ai",
        "penipuan_ewallet_qris",
        "phishing_rekayasa_sosial",
        "peretasan_pencurian_identitas",
        "judi_online_pinjol",
    ]
    max_count = max(hints.values())
    candidates = [v for v, c in hints.items() if c == max_count]
    if len(candidates) == 1:
        return candidates[0]
    # Tie-break dengan prioritas
    for p in priority:
        if p in candidates:
            return p
    return candidates[0]


if __name__ == '__main__':
    # Quick self-test
    tests = [
        "Tadi ditelpon ngaku dari BCA minta OTP, untung gak dikasih",
        "Saldo OVO saya amblas setelah scan QRIS di parkiran",
        "Bapak kena APK undangan nikah, rekening terkuras",
        "Slot gacor maxwin, link di bio",
        "Akun IG saya diretas dipake nipu followers",
        "Mama hampir transfer karena suara AI mirip anak",
        "lucu banget videonya wkwk",  # harusnya no anchor
    ]
    for t in tests:
        print(f"Anchor: {has_anchor(t)} | Top: {top_vector_hint(t)} | {t[:50]}")
