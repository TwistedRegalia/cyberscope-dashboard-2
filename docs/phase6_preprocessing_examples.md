# Phase 6 — Contoh Prapemrosesan (Data untuk Bab 3/4, Tabel 4.2)

Contoh **aktual** dari `data/preprocessed_dataset_v2.csv`, dikelompokkan per jenis transformasi untuk mengilustrasikan pipeline Phase 6 ([`src/phase6_preprocess.py`](../src/phase6_preprocess.py)). Ini basis empiris **Tabel 4.2** — dipilih agar setiap transformasi (URL/mention, slang, hashtag, emoji) terlihat nyata.

Kolom:
- **MENTAH** = `text` asli (apa adanya).
- **BERSIH** = `text_clean` — input utama IndoBERT (case-folded, URL→`[URL]`, @user→`[USER]`, emoji emosi→`[EMOSI_*]`, emoji dekoratif dibuang, hashtag→teks). Cyber slang dipertahankan.
- **NORML** = `text_normalized` — `text_clean` + slang→baku (gue→saya, yg→yang, tp→tetapi, ga/kaga→tidak, bgt→sangat), fitur Tier-2/baseline.

---

## 1. URL + mention (@user) — phishing_rekayasa_sosial

**MENTAH:** `Modus penipuan hack no wa tf nya melalui bank @danamon @HelloDanamon tolong di blokir dulu no rekeningnya 🙏🏻 https://t.co/5al2AApCJT`
**BERSIH:** `modus penipuan hack no wa tf nya melalui bank [USER] [USER] tolong di blokir dulu no rekeningnya [URL]`
**NORML:** `modus penipuan hack no wa transfer nya melalui bank [USER] [USER] tolong di blokir dulu no rekeningnya [URL]`
*(case folding · @mention→`[USER]` · URL→`[URL]` · emoji dekoratif 🙏🏻 dibuang · tf→transfer di NORML)*

**MENTAH:** `Ini tuh penipuan ga sih? Soalnya tadi ada kode otp masuk https://t.co/uiLlfFsPsh`
**BERSIH:** `ini tuh penipuan ga sih? soalnya tadi ada kode otp masuk [URL]`
**NORML:** `ini itu penipuan tidak sih? soalnya tadi ada kode otp masuk [URL]`

**MENTAH:** `@KapudS640 dan di moment order fiktif itu, ada modus penipuan juga sampe di chat lewat WA dan di telf WA pribadi mengatasnamakan shopee, berhubung saya sadar dan ga panik saya abaikan hehe`
**BERSIH:** `[USER] dan di moment order fiktif itu, ada modus penipuan juga sampe di chat lewat wa dan di telf wa pribadi mengatasnamakan shopee, berhubung saya sadar dan ga panik saya abaikan hehe`
**NORML:** `[USER] dan di moment order fiktif itu, ada modus penipuan juga sampe di chat lewat wa dan di telf wa pribadi mengatasnamakan shopee, berhubung saya sadar dan tidak panik saya abaikan hehe`

---

## 2. Normalisasi slang — phishing_rekayasa_sosial

**MENTAH:** `EH GUE KENA TIPU SAMA AKUN THRIF YG DAH JALAN AROUND 5 THNAN PADAHAL SEBELUMNYA DIA OKE LOH, TP SKRG RESI GUE GA DIKIRIM WA GA DIBALES DUIT KAGA DIREFUND, NAJIS BGT.`
**BERSIH:** `eh gue kena tipu sama akun thrif yg dah jalan around 5 thnan padahal sebelumnya dia oke loh, tp skrg resi gue ga dikirim wa ga dibales duit kaga direfund, najis bgt.`
**NORML:** `eh saya kena tipu sama akun thrif yang sudah jalan around 5 thnan padahal sebelumnya dia oke loh, tetapi sekarang resi saya tidak dikirim wa tidak dibales duit tidak direfund, najis sangat.`
*(gue→saya · yg→yang · dah→sudah · tp→tetapi · skrg→sekarang · ga/kaga→tidak · bgt→sangat)*

**MENTAH:** `korban sama2 ketipu tb2 jd temen 😔😔 semua org bisa jd temen kecuali yg nipu https://t.co/9Md2GnZ0Ba`
**BERSIH:** `korban sama2 ketipu tb2 jd temen [EMOSI_SEDIH] [EMOSI_SEDIH] semua org bisa jd temen kecuali yg nipu [URL]`
**NORML:** `korban sama2 ketipu tb2 jadi temen [EMOSI_SEDIH] [EMOSI_SEDIH] semua orang bisa jadi temen kecuali yang nipu [URL]`
*(emoji emosi 😔→`[EMOSI_SEDIH]` · jd→jadi · org→orang)*

---

## 3. Hashtag → teks — penipuan_ewallet_qris

**MENTAH:** `Yuk ikuti kuisnya! Cek di bawah ini ya 👇 t. QRIS GoPay Himalayan Butterscotch #InfoKuis #GiveawayIndonesia #ZonaUang #ZonaJajan #giveaway #HuaweiWatchFit5Pro #google`
**BERSIH:** `yuk ikuti kuisnya! cek di bawah ini ya t. qris gopay himalayan butterscotch infokuis giveawayindonesia zonauang zonajajan giveaway huaweiwatchfit5pro google`
*(hashtag `#` dilepas, kata dipertahankan · emoji 👇 dibuang)*

**MENTAH:** `penipu di hastag #zonauang guys hati”, aku udah pay tp diblock sm dia nama qrisnya : rainbow-distributo nomernya : 0877‑1339‑2300 https://t.co/7L5SUPDas1`
**BERSIH:** `penipu di hastag zonauang guys hati”, aku udah pay tp diblock sm dia nama qrisnya : rainbow-distributo nomernya : 0877‑1339‑2300 [URL]`
**NORML:** `penipu di hastag zonauang guys hati”, aku sudah pay tetapi diblock sama dia nama qrisnya : rainbow-distributo nomernya : 0877‑1339‑2300 [URL]`
*(#zonauang→zonauang · udah→sudah · tp→tetapi · sm→sama · URL→`[URL]`)*

---

## 4. Emoji emosi → tag, dekoratif dibuang — phishing_rekayasa_sosial

**MENTAH:** `-ness ti ati guyss sama no wa ini +62 858-1777-2151 aku habis kena tipu tiket btw, ternyata korbannya udh bnyak😭😭😭`
**BERSIH:** `-ness ti ati guyss sama no wa ini +62 858-1777-2151 aku habis kena tipu tiket btw, ternyata korbannya udh bnyak [EMOSI_SEDIH] [EMOSI_SEDIH] [EMOSI_SEDIH]`
**NORML:** `-ness ti ati guyss sama no wa ini +62 858-1777-2151 aku habis kena tipu tiket btw, ternyata korbannya sudah bnyak [EMOSI_SEDIH] [EMOSI_SEDIH] [EMOSI_SEDIH]`
*(😭→`[EMOSI_SEDIH]` per emoji · udh→sudah)*

**MENTAH:** `💚 sender hapus wa, tapi sebelumnya uda di cadangkan, pas download lagi malah ga ada akun google yang merasa 'dicadangkan' jadi semua isi wa nya hilang, ada yang tau gimana ini pulihkannya?😭`
**BERSIH:** `sender hapus wa, tapi sebelumnya uda di cadangkan, pas download lagi malah ga ada akun google yang merasa 'dicadangkan' jadi semua isi wa nya hilang, ada yang tau gimana ini pulihkannya? [EMOSI_SEDIH]`
**NORML:** `sender hapus wa, tetapi sebelumnya sudah di cadangkan, pas download lagi malah tidak ada akun google yang merasa 'dicadangkan' jadi semua isi wa nya hilang, ada yang tau bagaimana ini pulihkannya? [EMOSI_SEDIH]`
*(emoji dekoratif 💚 dibuang di awal · emoji emosi 😭→`[EMOSI_SEDIH]` · tapi→tetapi · uda→sudah · ga→tidak · gimana→bagaimana)*

---

**Catatan:** `text_stemmed` (Sastrawi) tersedia terpisah namun **tidak** dipakai sebagai input IndoBERT (risiko over-stemming, mis. "sebelumnya"→"belum") — lihat CONTEXT.md §8. Cyber slang bermakna (`pinjol`, `gacor`, `maxwin`, `qris`) sengaja dipertahankan, tidak dinormalisasi.
