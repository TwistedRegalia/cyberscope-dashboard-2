#!/usr/bin/env python3
"""
phase7_labeling.py — Snorkel Labeling Functions untuk E-ICTT v2.1 (Phase 7)

STATUS: PILOT (phishing + judi). Vektor lain (ewallet, malware, peretasan,
deepfake) menyusul setelah pilot precision divalidasi Ray.

Prinsip desain (sesuai keputusan metodologis):
  - Agregator: Snorkel LabelModel (utama) + formula confidence manual (baseline).
  - Tier 1/2/3 dari Pattern Library dipakai sebagai DISIPLIN DESAIN LF (LF mana
    yang dipercaya high-precision), BUKAN confidence hard-coded. LabelModel
    belajar akurasi tiap LF dari pola agreement.
  - Input LF = text_clean (bentuk informal dipertahankan: "gak","kasi","dapet").
    text_normalized dicadangkan untuk IndoBERT, BUKAN untuk regex LF.
  - Fix morfologi v1.1 (suffix klitik SUF) dibawa dari anchor_patterns.py.
  - PHISHING STRICT (Temuan #5): narasi korban generik HANYA vote phishing bila
    ada anchor kredensial/institusi/rekayasa-sosial. Penipuan jual-beli online
    -> diarahkan ke tidak_relevan (keputusan Ray), tidak mencemari phishing.

Referensi: docs/02_Pattern_Library.md, docs/00_Annotation_Guidelines_ICTT_v2.1.md
"""

import re
from snorkel.labeling import labeling_function

# ============================================================
# LABEL SPACE (6 vektor; urutan ID stabil)
# ============================================================
ABSTAIN   = -1
PHISHING  = 0
EWALLET   = 1
MALWARE   = 2
JUDI      = 3
PERETASAN = 4
DEEPFAKE  = 5

LABEL_NAMES = {
    PHISHING:  "phishing_rekayasa_sosial",
    EWALLET:   "penipuan_ewallet_qris",
    MALWARE:   "malware_apk",
    JUDI:      "judi_online_pinjol",
    PERETASAN: "peretasan_pencurian_identitas",
    DEEPFAKE:  "deepfake_penipuan_ai",
}

# Suffix klitik/imbuhan Indonesia (fix morfologi anchor v1.1)
SUF = r"(?:nya|ku|mu|lah|kah|in|an)?"

_F = re.IGNORECASE | re.UNICODE

def _txt(x):
    """Ambil text_clean sebagai string aman (LF input)."""
    t = getattr(x, "text_clean", "")
    return t if isinstance(t, str) else ""

# ============================================================
# ANCHOR HELPERS — dipakai sebagai GATE untuk strict-phishing
# ============================================================
# Anchor kredensial/institusi/rekayasa-sosial: pembeda phishing vs penipuan biasa
_RE_CRED   = re.compile(r"(?:otp|password|pass|pin|kode\s*(?:verif|otp|rahasia|sms)|sandi|kata\s*sandi)", _F)
_RE_INSTIT = re.compile(r"(?:ngaku|mengaku|atas\s*nama|catut)\W{0,25}(?:bank|bca|bri|bni|mandiri|cimb|btn|cs|shopee|tokped|tokopedia|gojek|grab|ovo|dana|gopay|pln|bpjs|pajak|kurir|jne|j&t)", _F)
_RE_LINK   = re.compile(r"(?:link|tautan|url|klik)\W{0,20}(?:mencurigakan|aneh|gak\s*jelas|phising|phishing|tipu|nipu|palsu|bohongan|verifikasi|verif|akun)", _F)
_RE_SOCENG = re.compile(rf"\brekayasa\s*sosial\b|\bsoceng{SUF}\b|\bsocial\s*engineering\b", _F)

def _has_phish_anchor(t):
    return bool(_RE_CRED.search(t) or _RE_INSTIT.search(t) or _RE_LINK.search(t) or _RE_SOCENG.search(t))

# Jual-beli online fraud -> tidak_relevan (keputusan Ray). Penanda khas:
_RE_JUALBELI = re.compile(
    r"\b(?:beli|jual|jual\s*beli|jualbeli|order|pre\s*order|po\b|cod|wts|wtb|wtt|seller|olshop|toko\s*online|"
    r"barang|paket\s*gak\s*(?:sampai|dateng|nyampe)|gak\s*dikirim|tidak\s*dikirim|fiktif|fee\s*jasa|jasa\s*titip|jastip)\b",
    _F,
)
# tapi jual-beli + kredensial/OTP = bisa jadi phishing beneran -> jangan buang
def _is_jualbeli_fraud(t):
    return bool(_RE_JUALBELI.search(t)) and not _has_phish_anchor(t)

# Mancing/ikan -> guard untuk false-positive "fishing"
_RE_MANCING = re.compile(r"(?:laut|mancing|ikan|pancing|umpan|kail|sungai|kolam)", _F)

# Distress (etika riset, G4.2) — tetap label JUDI tapi di-flag
_RE_DISTRESS = re.compile(r"(?:bunuh\s*diri|mau\s*mati|pengen\s*mati|akhiri\s*hidup|depresi|stress\s*berat|gantung\s*diri)", _F)
def is_distress(t):
    return bool(_RE_DISTRESS.search(t) if isinstance(t, str) else False)

# ============================================================
# LAYER 2 — PHISHING LFs (STRICT)
# ============================================================
_RE_PHISH_EJAAN = re.compile(r"\b[pf][iy]+s+h+i*n+g+\b", _F)  # phishing/phising/pishing (wajib ada h)

@labeling_function()
def lf_phish_t1_ejaan(x):
    """Tier1 — variasi ejaan 'phishing' (guard mancing)."""
    t = _txt(x)
    if _RE_PHISH_EJAAN.search(t) and not _RE_MANCING.search(t):
        return PHISHING
    return ABSTAIN

_RE_PHISH_OTP = re.compile(r"(?:minta|kasih|kasi|kirim|share|berikan|sebut(?:kan)?|info(?:in)?)\W{0,20}(?:otp|kode\W{0,5}(?:verif|otp|rahasia|sms))", _F)

@labeling_function()
def lf_phish_t1_otp_modus(x):
    """Tier1 — modus minta OTP/kode verifikasi."""
    return PHISHING if _RE_PHISH_OTP.search(_txt(x)) else ABSTAIN

_RE_PHISH_TELP = re.compile(r"(?:telp(?:on)?|nelpon|ditelp(?:on)?|telepon|telpon|wa|chat|dm)\W{0,30}(?:ngaku|mengaku|katanya|bilang(?:nya)?|claim|atas\s*nama)\W{0,40}(?:bank|bca|bri|bni|mandiri|cimb|btn|cs|shopee|tokped|tokopedia|gojek|grab|ovo|dana|gopay|pln|bpjs|pajak|kurir|jne|j&t)", _F)

@labeling_function()
def lf_phish_t1_telpon_institusi(x):
    """Tier1 — trinity phishing: kontak + ngaku + institusi finansial/resmi."""
    return PHISHING if _RE_PHISH_TELP.search(_txt(x)) else ABSTAIN

@labeling_function()
def lf_phish_t1_link_curiga(x):
    """Tier1 — link/tautan mencurigakan/palsu/verifikasi akun."""
    return PHISHING if _RE_LINK.search(_txt(x)) else ABSTAIN

@labeling_function()
def lf_phish_t1_soceng(x):
    """Tier1 — istilah rekayasa sosial / soceng / social engineering eksplisit."""
    return PHISHING if _RE_SOCENG.search(_txt(x)) else ABSTAIN

_RE_PHISH_HADIAH = re.compile(r"(?:klaim|dapat|dapet|menang|terpilih|selamat)\W{0,15}(?:hadiah|kuota|pulsa|undian|voucher|cashback|reward|saldo|grand\s*prize)\W{0,30}(?:link|klik|wa|whatsapp|sms|telegram|web)", _F)

@labeling_function()
def lf_phish_t2_hadiah_link(x):
    """Tier2 — iming-iming hadiah/kuota palsu + ajakan klik link/WA."""
    return PHISHING if _RE_PHISH_HADIAH.search(_txt(x)) else ABSTAIN

_RE_PHISH_UNDANGAN = re.compile(r"(?:undangan|invitation|nikah|menikah|surat|tagihan|resi)\W{0,20}(?:pdf|file|kirim|wa|whatsapp|telegram)", _F)

@labeling_function()
def lf_phish_t2_undangan_file(x):
    """Tier2 — modus undangan/surat/tagihan via file/WA. Guard: skip jika ada 'apk' (hierarki -> malware)."""
    t = _txt(x)
    if re.search(r"\bapk\b", t, _F):
        return ABSTAIN
    return PHISHING if _RE_PHISH_UNDANGAN.search(t) else ABSTAIN

_RE_PHISH_TRIGGER = re.compile(r"(?:penipu(?:an)?|modus|kena\s*tipu|ketipu|hati[\s-]*hati|waspada|awas|scam|nipu|hampir\s*kena)", _F)

@labeling_function()
def lf_phish_t2_anchor_gate(x):
    """Tier2 — GATE: vote phishing bila ada anchor phishing sejati
    (kredensial / ngaku-institusi / link-verif / soceng) BERSAMA trigger penipuan.
    Ini memulihkan recall phishing presisi-aman tanpa menyerap jual-beli
    (jual-beli tanpa anchor -> tidak punya _has_phish_anchor -> ABSTAIN)."""
    t = _txt(x)
    if _has_phish_anchor(t) and _RE_PHISH_TRIGGER.search(t):
        return PHISHING
    return ABSTAIN

_RE_PHISH_KORBAN = re.compile(r"(?:kena|hampir\s*kena|nyaris|ke)\W{0,12}(?:tipu|nipu|scam|tipu[\s-]*menipu)\W{0,40}(?:online|wa|whatsapp|sms|telp|telepon|link|email|dm)", _F)

@labeling_function()
def lf_phish_t3_korban_strict(x):
    """Tier3 STRICT (Temuan #5) — narasi korban + konteks digital,
    HANYA vote phishing bila ada anchor kredensial/institusi/soceng.
    Jika jual-beli fraud tanpa anchor -> ABSTAIN (diarahkan ke tidak_relevan)."""
    t = _txt(x)
    if not _RE_PHISH_KORBAN.search(t):
        return ABSTAIN
    if _is_jualbeli_fraud(t):
        return ABSTAIN
    if _has_phish_anchor(t):
        return PHISHING
    return ABSTAIN

# ============================================================
# LAYER 2 — JUDI/PINJOL LFs
# ============================================================
_RE_JUDI_SLANG = re.compile(r"\b(?:gacor|maxwin|max\s*win|rungkad|anti[\s-]*rungkad|wd\s*lancar|jp[\s-]*gede|scatter|cuan\s*slot|pragmatic|zeus|mahjong\s*ways)\b", _F)

@labeling_function()
def lf_judi_t1_slang(x):
    """Tier1 — slang judol domain-specific (gacor/maxwin/rungkad/scatter)."""
    return JUDI if _RE_JUDI_SLANG.search(_txt(x)) else ABSTAIN

_RE_JUDI_EKSPLISIT = re.compile(rf"\b(?:judi\s*online|judol{SUF}|jdl|judi\s*slot|slot\s*online|casino\s*online|togel{SUF}\s*online|togel{SUF}|sl[\*o]t\s*online)\b", _F)

@labeling_function()
def lf_judi_t1_eksplisit(x):
    """Tier1 — judi online/judol/slot online/togel eksplisit."""
    return JUDI if _RE_JUDI_EKSPLISIT.search(_txt(x)) else ABSTAIN

_RE_PINJOL_ILEGAL = re.compile(rf"\bpinjol{SUF}\W{{0,15}}(?:ilegal|gak\s*resmi|tidak\s*terdaftar|bodong|nakal|abal[\s-]*abal|abal)", _F)

@labeling_function()
def lf_judi_t1_pinjol_ilegal(x):
    """Tier1 — pinjol ilegal/bodong/abal-abal."""
    return JUDI if _RE_PINJOL_ILEGAL.search(_txt(x)) else ABSTAIN

_RE_PINJOL_TEROR = re.compile(rf"(?:diteror|teror|ancam(?:an)?|kasar|galak|sebar\s*data)\W{{0,30}}(?:pinjol{SUF}|debt\s*collector|dc\b|penagih|galbay)", _F)

@labeling_function()
def lf_judi_t1_teror_pinjol(x):
    """Tier1 — penagihan pinjol kasar/teror/sebar data."""
    return JUDI if _RE_PINJOL_TEROR.search(_txt(x)) else ABSTAIN

_RE_JUDI_BARE = re.compile(rf"\b(?:judol{SUF}|pinjol{SUF}|galbay|gestun|joki\s*pinjol|pinjaman\s*online)\b", _F)

@labeling_function()
def lf_judi_t1_bare(x):
    """Tier1 — anchor domain bare (judol/pinjol/galbay/gestun) dgn fix morfologi SUF.
    Catatan: 'slot' bare TIDAK di sini (ambigu: slot waktu/kosong)."""
    return JUDI if _RE_JUDI_BARE.search(_txt(x)) else ABSTAIN

_RE_JUDI_PINJAMAN = re.compile(r"(?:pinjaman|pinjam|hutang|utang)\W{0,15}(?:online|app|aplikasi)\W{0,30}(?:bunga|tinggi|cekik|gila|merampok|teror|nagih)", _F)

@labeling_function()
def lf_judi_t2_pinjaman_bunga(x):
    """Tier2 — pinjaman online bunga cekik/teror."""
    return JUDI if _RE_JUDI_PINJAMAN.search(_txt(x)) else ABSTAIN

_RE_JUDI_SLOT_PROMO = re.compile(r"\bsl[\*o]t\b\W{0,30}(?:bonus|new\s*member|deposit|depo|link|daftar|bio|register|dana\s*kaget)", _F)

@labeling_function()
def lf_judi_t2_slot_promo(x):
    """Tier2 — slot + bahasa promosi (bonus/new member/link bio/deposit)."""
    return JUDI if _RE_JUDI_SLOT_PROMO.search(_txt(x)) else ABSTAIN

_RE_JUDI_MODAL = re.compile(r"(?:modal|depo(?:sit)?)\W{0,15}(?:rb|ribu|recehan|kecil|jt|juta)\W{0,40}(?:jadi|menang|wd|withdraw|cuan)\W{0,15}(?:jt|juta|m\b|miliar|gede|banyak)", _F)

@labeling_function()
def lf_judi_t3_modal_hasil(x):
    """Tier3 — promosi 'modal kecil hasil besar' khas judol."""
    return JUDI if _RE_JUDI_MODAL.search(_txt(x)) else ABSTAIN

# ============================================================
# LAYER 2 — EWALLET/QRIS LFs
# ============================================================
_RE_EW_QRIS_PALSU = re.compile(rf"\bqris{SUF}\b\W{{0,15}}(?:palsu|tempel|fake|bohongan|aspal|tipu|bodong)", _F)
@labeling_function()
def lf_ewallet_t1_qris_palsu(x):
    """Tier1 — QRIS palsu/tempel/aspal eksplisit."""
    return EWALLET if _RE_EW_QRIS_PALSU.search(_txt(x)) else ABSTAIN

_RE_EW_SALDO = re.compile(r"(?:saldo|isi)\W{0,8}(?:ovo|dana|gopay|shopeepay|spaylater|linkaja|jenius)\W{0,30}(?:hilang|terkuras|raib|amblas|kuras|kosong|abis|berkurang|kesedot|ludes)", _F)
@labeling_function()
def lf_ewallet_t1_saldo_platform(x):
    """Tier1 — saldo e-wallet (platform eksplisit) hilang/terkuras."""
    return EWALLET if _RE_EW_SALDO.search(_txt(x)) else ABSTAIN

_RE_EW_SCANBALIK = re.compile(r"(?:salah\s*transfer|salah\s*kirim|kelebihan)\W{0,40}(?:scan|qr|qris)\W{0,20}(?:balik|kembali|refund)", _F)
@labeling_function()
def lf_ewallet_t1_scan_balik(x):
    """Tier1 — modus reverse-scan (salah transfer minta scan QR balik)."""
    return EWALLET if _RE_EW_SCANBALIK.search(_txt(x)) else ABSTAIN

_RE_EW_TIPU = re.compile(r"(?:ovo|dana|gopay|shopeepay|linkaja|jenius)\W{0,30}(?:tipu|nipu|scam|penipu(?:an)?|bobol|hack)", _F)
@labeling_function()
def lf_ewallet_t2_platform_tipu(x):
    """Tier2 — platform e-wallet + penipuan generik."""
    return EWALLET if _RE_EW_TIPU.search(_txt(x)) else ABSTAIN

_RE_EW_QR_LOKASI = re.compile(r"\bqr(?:is)?\b\W{0,40}(?:parkir(?:an)?|kotak\s*amal|masjid|mushola|pom\s*bensin|toilet|donasi)", _F)
@labeling_function()
def lf_ewallet_t2_qr_lokasi_publik(x):
    """Tier2 — QR(IS) di lokasi publik (indikator kuat QRIS palsu)."""
    return EWALLET if _RE_EW_QR_LOKASI.search(_txt(x)) else ABSTAIN

_RE_EW_PROMO = re.compile(r"(?:cashback|promo|diskon|topup|top[\s-]*up|tukar\s*saldo)\W{0,30}(?:ovo|dana|gopay|shopeepay|linkaja|e[\s-]*wallet|dompet\s*digital)\W{0,30}(?:palsu|bohong|tipu|fake|murah)", _F)
@labeling_function()
def lf_ewallet_t3_promo_palsu(x):
    """Tier3 — cashback/promo/topup e-wallet palsu."""
    return EWALLET if _RE_EW_PROMO.search(_txt(x)) else ABSTAIN

# ============================================================
# LAYER 2 — MALWARE/APK LFs
# ============================================================
_RE_MW_MODUS = re.compile(r"\.?apk\b\W{0,30}(?:undangan|nikah|kurir|j[\s&]*t|jne|sicepat|paket|tilang|surat|kartu|pos)", _F)
@labeling_function()
def lf_malware_t1_apk_modus(x):
    """Tier1 — APK + modus khas ID (undangan/kurir/tilang/paket)."""
    return MALWARE if _RE_MW_MODUS.search(_txt(x)) else ABSTAIN

_RE_MW_BAHAYA = re.compile(r"\.?apk\b\W{0,30}(?:penipu(?:an)?|tipu|nipu|scam|bahaya|virus|malware|trojan|berbahaya)", _F)
@labeling_function()
def lf_malware_t1_apk_bahaya(x):
    """Tier1 — APK + penipuan/virus/malware eksplisit."""
    return MALWARE if _RE_MW_BAHAYA.search(_txt(x)) else ABSTAIN

_RE_MW_KENA = re.compile(r"(?:kena|install|pasang|download|terkecoh|klik)\W{0,15}(?:file\s*)?\.?apk\b", _F)
@labeling_function()
def lf_malware_t1_kena_apk(x):
    """Tier1 — kena/install/download/klik APK."""
    return MALWARE if _RE_MW_KENA.search(_txt(x)) else ABSTAIN

_RE_MW_SUMBER = re.compile(r"\.?apk\b\W{0,30}(?:wa|whatsapp|telegram|sms|dm|kirim(?:an)?)", _F)
@labeling_function()
def lf_malware_t2_apk_sumber(x):
    """Tier2 — APK dari sumber messaging (WA/Telegram/SMS)."""
    return MALWARE if _RE_MW_SUMBER.search(_txt(x)) else ABSTAIN

_RE_MW_BANKDRAIN = re.compile(r"(?:m[\s-]*banking|mobile\s*banking|saldo\s*bank)\W{0,30}(?:terkuras|kuras|amblas|hilang|raib|abis|bobol)", _F)
@labeling_function()
def lf_malware_t2_bank_drained(x):
    """Tier2 — m-banking/saldo bank terkuras. Gate: hanya jika 'apk' ada di teks (hierarki malware>peretasan)."""
    t = _txt(x)
    if re.search(r"\bapk\b", t, _F) and _RE_MW_BANKDRAIN.search(t):
        return MALWARE
    return ABSTAIN

# ============================================================
# LAYER 2 — PERETASAN/PENCURIAN IDENTITAS LFs
# ============================================================
_RE_PR_AKUN = re.compile(r"(?:akun)\W{0,20}(?:ig|instagram|wa|whatsapp|fb|facebook|twitter|tiktok|tt|telegram|tg|email|gmail)\W{0,30}(?:diretas|dihack|dibobol|dibajak|dicuri|kena\s*hack|di\s*take\s*over)", _F)
@labeling_function()
def lf_peretasan_t1_akun_diretas(x):
    """Tier1 — akun sosmed/email diretas/dibajak/dibobol."""
    return PERETASAN if _RE_PR_AKUN.search(_txt(x)) else ABSTAIN

_RE_PR_BOCOR = re.compile(r"(?:kebocoran|bocor(?:an)?|leak(?:age|ed)?)\W{0,30}(?:data|dukcapil|pdp|pribadi|nik|kk|ktp|bpjs)", _F)
@labeling_function()
def lf_peretasan_t1_kebocoran_data(x):
    """Tier1 — kebocoran data skala besar (dukcapil/NIK/KTP)."""
    return PERETASAN if _RE_PR_BOCOR.search(_txt(x)) else ABSTAIN

_RE_PR_KASUS = re.compile(r"\b(?:bjorka|breach\s*forums?|raidforums?)\b", _F)
@labeling_function()
def lf_peretasan_t1_kasus(x):
    """Tier1 — entitas/kasus peretasan spesifik (Bjorka/BreachForums)."""
    return PERETASAN if _RE_PR_KASUS.search(_txt(x)) else ABSTAIN

_RE_PR_SIMSWAP = re.compile(r"(?:sim[\s-]*swap|tukar\s*sim|nomor\s*diambil\s*alih|nomor\s*dibajak)", _F)
@labeling_function()
def lf_peretasan_t1_simswap(x):
    """Tier1 — SIM swap / nomor dibajak."""
    return PERETASAN if _RE_PR_SIMSWAP.search(_txt(x)) else ABSTAIN

_RE_PR_CURI = re.compile(r"(?:curi|dicuri|pencurian)\W{0,20}(?:data|identitas|nik|ktp|kk|foto\s*ktp)", _F)
@labeling_function()
def lf_peretasan_t2_curi_data(x):
    """Tier2 — pencurian data/identitas pribadi."""
    return PERETASAN if _RE_PR_CURI.search(_txt(x)) else ABSTAIN

_RE_PR_DOX = re.compile(r"\b(?:doxing|doxxing|dox(?:x)?ed)\b|(?:sebar(?:kan)?|disebar)\W{0,20}(?:identitas|alamat|nomor|data\s*pribadi)", _F)
@labeling_function()
def lf_peretasan_t2_doxing(x):
    """Tier2 — doxing / sebar identitas-alamat-data."""
    return PERETASAN if _RE_PR_DOX.search(_txt(x)) else ABSTAIN

_RE_PR_JASAHACK = re.compile(r"(?:jasa)\W{0,15}(?:pulihkan|kembalikan|recover|hack|bobol)\W{0,15}(?:akun|ig|wa|fb)", _F)
@labeling_function()
def lf_peretasan_t3_jasa_hack(x):
    """Tier3 — jasa pulihkan/hack akun (eufemisme pelaku, R4)."""
    return PERETASAN if _RE_PR_JASAHACK.search(_txt(x)) else ABSTAIN

# ============================================================
# LAYER 2 — DEEPFAKE/AI LFs
# ============================================================
_RE_DF_DEEPFAKE = re.compile(r"\b(?:deepfake|deep\s*fake|deep[\s-]*faked)\b", _F)
@labeling_function()
def lf_deepfake_t1_eksplisit(x):
    """Tier1 — deepfake eksplisit."""
    return DEEPFAKE if _RE_DF_DEEPFAKE.search(_txt(x)) else ABSTAIN

_RE_DF_VOICE = re.compile(r"(?:voice|suara)\W{0,15}(?:clon(?:e|ing)|cloned|tiruan|palsu\s*ai|generated\s*ai|ai)", _F)
@labeling_function()
def lf_deepfake_t1_voice_clone(x):
    """Tier1 — voice cloning / suara AI."""
    return DEEPFAKE if _RE_DF_VOICE.search(_txt(x)) else ABSTAIN

_RE_DF_KELUARGA = re.compile(r"(?:suara|voice)\W{0,15}(?:mirip|sama|identik|kayak|persis)\W{0,30}(?:anak|ortu|orang\s*tua|saudara|bapak|ibu|mama|papa|ponakan|cucu)\W{0,40}(?:minta|transfer|kirim|urgent|tf)", _F)
@labeling_function()
def lf_deepfake_t1_suara_keluarga(x):
    """Tier1 — modus voice-clone keluarga minta transfer."""
    return DEEPFAKE if _RE_DF_KELUARGA.search(_txt(x)) else ABSTAIN

_RE_DF_AICONTENT = re.compile(r"(?:ai|chat\s*gpt|chatgpt|gemini|llm)\W{0,30}(?:scam|tipu|nipu|penipu(?:an)?|fraud|generated)\W{0,30}(?:konten|content|gambar|foto|video|teks)", _F)
@labeling_function()
def lf_deepfake_t2_ai_content_scam(x):
    """Tier2 — konten AI-generated untuk penipuan."""
    return DEEPFAKE if _RE_DF_AICONTENT.search(_txt(x)) else ABSTAIN

_RE_DF_TOKOH = re.compile(r"(?:video|klip)\W{0,15}(?:jokowi|prabowo|sri\s*mulyani|erick\s*thohir|ridwan\s*kamil|anies|gibran)\W{0,40}(?:promosi|endorse|investasi|crypto|trading|bagi[\s-]*bagi)", _F)
@labeling_function()
def lf_deepfake_t2_tokoh_publik(x):
    """Tier2 — deepfake tokoh publik untuk promosi scam investasi."""
    return DEEPFAKE if _RE_DF_TOKOH.search(_txt(x)) else ABSTAIN

# ============================================================
# REGISTRY LENGKAP (6 vektor)
# ============================================================
LFS_BY_VECTOR = {
    PHISHING: [lf_phish_t1_ejaan, lf_phish_t1_otp_modus, lf_phish_t1_telpon_institusi,
               lf_phish_t1_link_curiga, lf_phish_t1_soceng, lf_phish_t2_hadiah_link,
               lf_phish_t2_undangan_file, lf_phish_t2_anchor_gate, lf_phish_t3_korban_strict],
    JUDI:     [lf_judi_t1_slang, lf_judi_t1_eksplisit, lf_judi_t1_pinjol_ilegal,
               lf_judi_t1_teror_pinjol, lf_judi_t1_bare, lf_judi_t2_pinjaman_bunga,
               lf_judi_t2_slot_promo, lf_judi_t3_modal_hasil],
    EWALLET:  [lf_ewallet_t1_qris_palsu, lf_ewallet_t1_saldo_platform, lf_ewallet_t1_scan_balik,
               lf_ewallet_t2_platform_tipu, lf_ewallet_t2_qr_lokasi_publik, lf_ewallet_t3_promo_palsu],
    MALWARE:  [lf_malware_t1_apk_modus, lf_malware_t1_apk_bahaya, lf_malware_t1_kena_apk,
               lf_malware_t2_apk_sumber, lf_malware_t2_bank_drained],
    PERETASAN:[lf_peretasan_t1_akun_diretas, lf_peretasan_t1_kebocoran_data, lf_peretasan_t1_kasus,
               lf_peretasan_t1_simswap, lf_peretasan_t2_curi_data, lf_peretasan_t2_doxing,
               lf_peretasan_t3_jasa_hack],
    DEEPFAKE: [lf_deepfake_t1_eksplisit, lf_deepfake_t1_voice_clone, lf_deepfake_t1_suara_keluarga,
               lf_deepfake_t2_ai_content_scam, lf_deepfake_t2_tokoh_publik],
}
ALL_LFS = [lf for lfs in LFS_BY_VECTOR.values() for lf in lfs]

# ============================================================
# TIER-3 DISCOVERY LFs (reuse anchor v1.1, high-recall/medium-precision)
# Tujuan: (a) pulihkan recall kelas tipis, (b) beri overlap antar-LF agar
# per-vektor LabelModel bisa belajar akurasi. Confidence rendah (Tier-3);
# LabelModel + threshold yang memangkas presisi.
# ============================================================
import anchor_patterns as _ap
_ANCHOR_RX = {v: [re.compile(p, _F) for p in pats] for v, pats in _ap.PATTERNS.items()}

def _anchor_fire(t, vec_name):
    return any(rx.search(t) for rx in _ANCHOR_RX[vec_name])

@labeling_function()
def lf_phish_t3_discovery(x):
    return PHISHING if _anchor_fire(_txt(x), "phishing_rekayasa_sosial") else ABSTAIN

@labeling_function()
def lf_ewallet_t3_discovery(x):
    return EWALLET if _anchor_fire(_txt(x), "penipuan_ewallet_qris") else ABSTAIN

@labeling_function()
def lf_malware_t3_discovery(x):
    return MALWARE if _anchor_fire(_txt(x), "malware_apk") else ABSTAIN

@labeling_function()
def lf_judi_t3_discovery(x):
    return JUDI if _anchor_fire(_txt(x), "judi_online_pinjol") else ABSTAIN

@labeling_function()
def lf_peretasan_t3_discovery(x):
    return PERETASAN if _anchor_fire(_txt(x), "peretasan_pencurian_identitas") else ABSTAIN

@labeling_function()
def lf_deepfake_t3_discovery(x):
    return DEEPFAKE if _anchor_fire(_txt(x), "deepfake_penipuan_ai") else ABSTAIN

_DISCOVERY_LFS = {
    PHISHING: lf_phish_t3_discovery, EWALLET: lf_ewallet_t3_discovery,
    MALWARE: lf_malware_t3_discovery, JUDI: lf_judi_t3_discovery,
    PERETASAN: lf_peretasan_t3_discovery, DEEPFAKE: lf_deepfake_t3_discovery,
}
for _v, _lf in _DISCOVERY_LFS.items():
    LFS_BY_VECTOR[_v].append(_lf)
ALL_LFS = [lf for lfs in LFS_BY_VECTOR.values() for lf in lfs]
