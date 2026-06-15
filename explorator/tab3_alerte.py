# =========================================================
# IDBDC/explorator/tab3_alerte.py
# VERSIUNE: 1.0
# STATUS: NOU
# DATA: 2026.06.14
# =========================================================
# ALERTE ACTIVE — Categoriile 1, 2, 3
# CAT 1: Temporale (8 alerte)
# CAT 2: Calitate date (10 alerte)
# CAT 3: Financiare (4 alerte)
# TOTAL: 22 alerte
# Praguri: 30 zile, 90 zile, 60% concentrare,
#          12 luni inactivitate, 5 înregistrări minime
# =========================================================

import datetime
import streamlit as st
import pandas as pd
from supabase import Client

# =========================================================
# CONFIGURARE TABELE
# =========================================================

TABELE_CU_DATE = [
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
    "base_proiecte_fdi",
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_nonue",
    "base_proiecte_see",
    "base_proiecte_structurale",
]

TABELE_PROPRIETATE = [
    "base_prop_industr",
]

TABELE_EVENIMENTE = [
    "base_evenimente_stiintifice",
]

TOATE_TABELELE_BASE = (
    TABELE_CU_DATE
    + TABELE_PROPRIETATE
    + TABELE_EVENIMENTE
)

TABELE_FINANCIARE_SIMPLE = [
    "base_contracte_cep",
    "base_contracte_terti",
    "base_contracte_speciale",
    "base_proiecte_fdi",
    "base_proiecte_internationale",
    "base_proiecte_interreg",
    "base_proiecte_nonue",
    "base_proiecte_see",
    "base_proiecte_structurale",
]

TABELE_FINANCIARE_PN = [
    "base_proiecte_pncdi",
    "base_proiecte_pnrr",
]

TABLE_LABELS = {
    "base_contracte_cep":           "Contracte CEP",
    "base_contracte_terti":         "Contracte TERȚI",
    "base_contracte_speciale":      "Contracte SPECIALE",
    "base_proiecte_fdi":            "Proiecte FDI",
    "base_proiecte_pncdi":          "Proiecte PNCDI",
    "base_proiecte_pnrr":           "Proiecte PNRR",
    "base_proiecte_internationale": "Proiecte Internaționale",
    "base_proiecte_interreg":       "Proiecte INTERREG",
    "base_proiecte_nonue":          "Proiecte NON-UE",
    "base_proiecte_see":            "Proiecte SEE",
    "base_proiecte_structurale":    "Proiecte Structurale",
    "base_evenimente_stiintifice":  "Evenimente Științifice",
    "base_prop_industr":            "Proprietate Industrială",
}

TITLE_FIELDS = [
    "titlul_proiect", "titlul_eveniment", "titlul_proprietatii",
    "obiectul_contractului", "denumire",
]

PRAG_ZILE_SCURT  = 30
PRAG_ZILE_LUNG   = 90
PRAG_CONCENTRARE = 0.60
PRAG_INACTIVITATE_LUNI = 12
PRAG_MIN_INREGISTRARI  = 5


# =========================================================
# HELPERS
# =========================================================

def _safe_text(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _first_nonempty(row: dict, fields: list) -> str:
    for f in fields:
        v = _safe_text(row.get(f))
        if v:
            return v
    return "—"


def _try_date(v):
    if v is None:
        return None
    try:
        return pd.to_datetime(str(v)[:10]).date()
    except Exception:
        return None


def _fetch(supabase: Client, table: str, cols: str = "*", limit: int = 5000) -> list:
    try:
        res = supabase.table(table).select(cols).limit(limit).execute()
        return res.data or []
    except Exception:
        return []


def _to_float(v) -> float:
    if v is None:
        return 0.0
    try:
        return float(str(v).replace(",", ".").strip())
    except Exception:
        return 0.0


def _fmt_date(d) -> str:
    if d is None:
        return "—"
    if hasattr(d, "strftime"):
        return d.strftime("%d.%m.%Y")
    return str(d)


# =========================================================
# STILURI ALERTE
# =========================================================

def _alert_box(titlu: str, count: int, culoare: str, icon: str, randuri: list,
               col_headers: list):
    """
    Afișează o alertă cu titlu, număr, tabel de înregistrări afectate.
    culoare: 'red' | 'orange' | 'yellow' | 'blue'
    """
    culori = {
        "red":    ("rgba(220,38,38,0.15)",  "rgba(220,38,38,0.60)",  "#fca5a5"),
        "orange": ("rgba(234,88,12,0.15)",  "rgba(234,88,12,0.60)",  "#fdba74"),
        "yellow": ("rgba(202,138,4,0.15)",  "rgba(202,138,4,0.60)",  "#fde047"),
        "blue":   ("rgba(37,99,235,0.15)",  "rgba(37,99,235,0.60)",  "#93c5fd"),
        "green":  ("rgba(22,163,74,0.15)",  "rgba(22,163,74,0.60)",  "#86efac"),
    }
    bg, border, text_accent = culori.get(culoare, culori["blue"])

    if count == 0:
        st.markdown(
            f"<div style='background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.30);"
            f"border-radius:10px;padding:8px 14px;margin-bottom:8px;'>"
            f"<span style='color:#86efac;font-weight:700;font-size:0.88rem;'>"
            f"✅ {titlu} — nicio înregistrare afectată</span></div>",
            unsafe_allow_html=True,
        )
        return

    with st.expander(f"{icon} {titlu}  —  {count} înregistrări", expanded=False):
        if randuri:
            df = pd.DataFrame(randuri, columns=col_headers)
            st.dataframe(df, use_container_width=True, hide_index=True,
                         height=min(40 + len(df) * 35, 400))


def _section_header(titlu: str, total_alerte: int):
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.20);"
        f"border-radius:12px;padding:10px 16px;margin:16px 0 8px 0;'>"
        f"<span style='color:#ffffff;font-weight:900;font-size:1.02rem;'>{titlu}</span>"
        f"<span style='color:rgba(255,255,255,0.55);font-size:0.86rem;margin-left:10px;'>"
        f"({total_alerte} verificări)</span>"
        f"</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# CATEGORIA 1 — ALERTE TEMPORALE
# =========================================================

def _alerte_cat1(supabase: Client) -> int:
    azi = datetime.date.today()
    prag30 = azi + datetime.timedelta(days=PRAG_ZILE_SCURT)
    prag90 = azi + datetime.timedelta(days=PRAG_ZILE_LUNG)
    total_afectate = 0

    _section_header("📅 CATEGORIA 1 — Alerte Temporale", 8)

    # ── A1: Expiră în 30 de zile ──────────────────────────────────────
    randuri_a1 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,data_sfarsit,status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            ds = _try_date(r.get("data_sfarsit"))
            if ds and azi <= ds <= prag30:
                randuri_a1.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                    _fmt_date(ds),
                    (ds - azi).days,
                    _safe_text(r.get("status_contract_proiect")),
                ])
    randuri_a1.sort(key=lambda x: x[4])
    total_afectate += len(randuri_a1)
    _alert_box(
        f"Expiră în {PRAG_ZILE_SCURT} de zile", len(randuri_a1), "red", "🔴",
        randuri_a1,
        ["COD", "TITLU / OBIECT", "CATEGORIE", "DATA EXPIRARE", "ZILE RĂMASE", "STATUS"],
    )

    # ── A2: Expiră în 90 de zile (exclus cele din 30) ─────────────────
    randuri_a2 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,data_sfarsit,status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            ds = _try_date(r.get("data_sfarsit"))
            if ds and prag30 < ds <= prag90:
                randuri_a2.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                    _fmt_date(ds),
                    (ds - azi).days,
                    _safe_text(r.get("status_contract_proiect")),
                ])
    randuri_a2.sort(key=lambda x: x[4])
    total_afectate += len(randuri_a2)
    _alert_box(
        f"Expiră în {PRAG_ZILE_LUNG} de zile", len(randuri_a2), "orange", "🟠",
        randuri_a2,
        ["COD", "TITLU / OBIECT", "CATEGORIE", "DATA EXPIRARE", "ZILE RĂMASE", "STATUS"],
    )

    # ── A3: Expirate dar status încă activ ────────────────────────────
    STATUS_ACTIVE = {"activ", "active", "in derulare", "în derulare",
                     "implementare", "in implementare", "în implementare"}
    randuri_a3 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,data_sfarsit,status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            ds = _try_date(r.get("data_sfarsit"))
            status = _safe_text(r.get("status_contract_proiect")).lower()
            if ds and ds < azi and status in STATUS_ACTIVE:
                randuri_a3.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                    _fmt_date(ds),
                    (azi - ds).days,
                    _safe_text(r.get("status_contract_proiect")),
                ])
    randuri_a3.sort(key=lambda x: x[4], reverse=True)
    total_afectate += len(randuri_a3)
    _alert_box(
        "Expirate cu status încă activ", len(randuri_a3), "red", "🔴",
        randuri_a3,
        ["COD", "TITLU / OBIECT", "CATEGORIE", "DATA EXPIRARE", "ZILE DEPĂȘITE", "STATUS"],
    )

    # ── A4: Data început în trecut fără status actualizat ─────────────
    STATUS_NEACTUALIZATE = {"depus", "în evaluare", "in evaluare",
                            "selectat", "pre-contractare", "aprobat"}
    randuri_a4 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "data_inceput,status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            di = _try_date(r.get("data_inceput"))
            status = _safe_text(r.get("status_contract_proiect")).lower()
            if di and di < azi and status in STATUS_NEACTUALIZATE:
                randuri_a4.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                    _fmt_date(di),
                    _safe_text(r.get("status_contract_proiect")),
                ])
    total_afectate += len(randuri_a4)
    _alert_box(
        "Data început depășită — status neactualizat", len(randuri_a4), "orange", "🟠",
        randuri_a4,
        ["COD", "TITLU / OBIECT", "CATEGORIE", "DATA ÎNCEPUT", "STATUS CURENT"],
    )

    # ── A5: Durată depășită față de date ──────────────────────────────
    randuri_a5 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "data_inceput,data_sfarsit,durata")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            di = _try_date(r.get("data_inceput"))
            ds = _try_date(r.get("data_sfarsit"))
            durata = r.get("durata")
            if di and ds and durata:
                try:
                    durata_int = int(float(durata))
                    luni_reale = (ds.year - di.year) * 12 + (ds.month - di.month)
                    if abs(luni_reale - durata_int) > 2:
                        randuri_a5.append([
                            _safe_text(r.get("cod_identificare")),
                            _first_nonempty(r, TITLE_FIELDS),
                            label,
                            str(durata_int),
                            str(luni_reale),
                            str(abs(luni_reale - durata_int)),
                        ])
                except Exception:
                    pass
    total_afectate += len(randuri_a5)
    _alert_box(
        "Durată înregistrată ≠ durată calculată (diferență > 2 luni)", len(randuri_a5),
        "yellow", "🟡", randuri_a5,
        ["COD", "TITLU / OBIECT", "CATEGORIE",
         "DURATĂ ÎNREG. (luni)", "DURATĂ CALC. (luni)", "DIFERENȚĂ"],
    )

    # ── A6: Evenimente în următoarele 30 de zile ──────────────────────
    randuri_a6 = []
    rows_ev = _fetch(supabase, "base_evenimente_stiintifice",
                     "cod_identificare,titlul_eveniment,data_inceput,loc_desfasurare,natura_eveniment")
    for r in rows_ev:
        di = _try_date(r.get("data_inceput"))
        if di and azi <= di <= prag30:
            randuri_a6.append([
                _safe_text(r.get("cod_identificare")),
                _safe_text(r.get("titlul_eveniment")),
                _fmt_date(di),
                (di - azi).days,
                _safe_text(r.get("loc_desfasurare")),
                _safe_text(r.get("natura_eveniment")),
            ])
    randuri_a6.sort(key=lambda x: x[3])
    total_afectate += len(randuri_a6)
    _alert_box(
        f"Evenimente programate în {PRAG_ZILE_SCURT} de zile", len(randuri_a6),
        "blue", "🔵", randuri_a6,
        ["COD", "TITLU EVENIMENT", "DATA", "ZILE PÂNĂ LA", "LOC", "NATURA"],
    )

    # ── A7: Proprietate industrială — valabilitate expirată ────────────
    randuri_a7 = []
    rows_pi = _fetch(supabase, "base_prop_industr",
                     "cod_identificare,titlul_proprietatii,acronim_prop_industr,"
                     "data_sfarsit_valabilitate")
    for r in rows_pi:
        ds = _try_date(r.get("data_sfarsit_valabilitate"))
        if ds and ds < azi:
            randuri_a7.append([
                _safe_text(r.get("cod_identificare")),
                _safe_text(r.get("titlul_proprietatii")),
                _safe_text(r.get("acronim_prop_industr")),
                _fmt_date(ds),
                (azi - ds).days,
            ])
    randuri_a7.sort(key=lambda x: x[4], reverse=True)
    total_afectate += len(randuri_a7)
    _alert_box(
        "Proprietate industrială — valabilitate expirată", len(randuri_a7),
        "orange", "🟠", randuri_a7,
        ["COD / NR. CERERE", "TITLU", "TIP", "DATA EXPIRARE", "ZILE DEPĂȘITE"],
    )

    # ── A8: Proprietate industrială — expiră în 90 de zile ────────────
    randuri_a8 = []
    for r in rows_pi:
        ds = _try_date(r.get("data_sfarsit_valabilitate"))
        if ds and azi <= ds <= prag90:
            randuri_a8.append([
                _safe_text(r.get("cod_identificare")),
                _safe_text(r.get("titlul_proprietatii")),
                _safe_text(r.get("acronim_prop_industr")),
                _fmt_date(ds),
                (ds - azi).days,
            ])
    randuri_a8.sort(key=lambda x: x[4])
    total_afectate += len(randuri_a8)
    _alert_box(
        f"Proprietate industrială — expiră în {PRAG_ZILE_LUNG} de zile", len(randuri_a8),
        "yellow", "🟡", randuri_a8,
        ["COD / NR. CERERE", "TITLU", "TIP", "DATA EXPIRARE", "ZILE RĂMASE"],
    )

    return total_afectate


# =========================================================
# CATEGORIA 2 — ALERTE CALITATE DATE
# =========================================================

def _alerte_cat2(supabase: Client) -> int:
    total_afectate = 0

    _section_header("🔍 CATEGORIA 2 — Alerte Calitate Date", 10)

    # ── A9: Fără dată de început ───────────────────────────────────────
    randuri_a9 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,data_inceput")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            if not _try_date(r.get("data_inceput")):
                randuri_a9.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                ])
    total_afectate += len(randuri_a9)
    _alert_box(
        "Fără dată de început", len(randuri_a9), "yellow", "🟡",
        randuri_a9, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A10: Fără dată de sfârșit ──────────────────────────────────────
    randuri_a10 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,data_sfarsit")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            if not _try_date(r.get("data_sfarsit")):
                randuri_a10.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                ])
    total_afectate += len(randuri_a10)
    _alert_box(
        "Fără dată de sfârșit", len(randuri_a10), "yellow", "🟡",
        randuri_a10, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A11: Fără status ───────────────────────────────────────────────
    randuri_a11 = []
    for t in TABELE_CU_DATE:
        rows = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            if not _safe_text(r.get("status_contract_proiect")):
                randuri_a11.append([
                    _safe_text(r.get("cod_identificare")),
                    _first_nonempty(r, TITLE_FIELDS),
                    label,
                ])
    total_afectate += len(randuri_a11)
    _alert_box(
        "Fără status completat", len(randuri_a11), "yellow", "🟡",
        randuri_a11, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A12: Fără titlu / obiect ───────────────────────────────────────
    randuri_a12 = []
    for t in TOATE_TABELELE_BASE:
        rows = _fetch(supabase, t,
                      "cod_identificare,titlul_proiect,obiectul_contractului,"
                      "titlul_eveniment,titlul_proprietatii")
        label = TABLE_LABELS.get(t, t)
        for r in rows:
            if not _first_nonempty(r, TITLE_FIELDS).replace("—", "").strip():
                randuri_a12.append([
                    _safe_text(r.get("cod_identificare")),
                    label,
                ])
    total_afectate += len(randuri_a12)
    _alert_box(
        "Fără titlu / obiect completat", len(randuri_a12), "orange", "🟠",
        randuri_a12, ["COD", "CATEGORIE"],
    )

    # ── A13: Fără echipă asociată ──────────────────────────────────────
    randuri_a13 = []
    for t in TABELE_CU_DATE + TABELE_PROPRIETATE:
        rows_base = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului,"
                           "titlul_proprietatii")
        label = TABLE_LABELS.get(t, t)
        for r in rows_base:
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_ech = supabase.table("com_echipe_proiect") \
                    .select("cod_identificare") \
                    .eq("cod_identificare", cod).limit(1).execute()
                if not res_ech.data:
                    randuri_a13.append([
                        cod,
                        _first_nonempty(r, TITLE_FIELDS),
                        label,
                    ])
            except Exception:
                pass
    total_afectate += len(randuri_a13)
    _alert_box(
        "Fără echipă asociată", len(randuri_a13), "yellow", "🟡",
        randuri_a13, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A14: Fără date financiare ──────────────────────────────────────
    randuri_a14 = []
    for t in TABELE_CU_DATE:
        rows_base = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului")
        label = TABLE_LABELS.get(t, t)
        fin_table = "com_date_financiare_pn" if t in TABELE_FINANCIARE_PN \
            else "com_date_financiare"
        for r in rows_base:
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_fin = supabase.table(fin_table) \
                    .select("cod_identificare") \
                    .eq("cod_identificare", cod).limit(1).execute()
                if not res_fin.data:
                    randuri_a14.append([
                        cod,
                        _first_nonempty(r, TITLE_FIELDS),
                        label,
                    ])
            except Exception:
                pass
    total_afectate += len(randuri_a14)
    _alert_box(
        "Fără date financiare completate", len(randuri_a14), "yellow", "🟡",
        randuri_a14, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A15: Valoare financiară zero dar status activ ──────────────────
    STATUS_ACTIVE = {"activ", "active", "in derulare", "în derulare",
                     "implementare", "in implementare", "în implementare"}
    CAMPURI_VALOARE = [
        "valoare_contract_cep_terti_speciale", "valoare_totala_contract",
        "suma_aprobata_mec", "cost_total_proiect", "costuri_totale_proiect",
        "grant_aprobat", "buget_upt",
    ]
    randuri_a15 = []
    for t in TABELE_FINANCIARE_SIMPLE:
        rows_base = _fetch(supabase, t,
                           "cod_identificare,titlul_proiect,obiectul_contractului,"
                           "status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows_base:
            status = _safe_text(r.get("status_contract_proiect")).lower()
            if status not in STATUS_ACTIVE:
                continue
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_fin = supabase.table("com_date_financiare") \
                    .select(",".join(CAMPURI_VALOARE)) \
                    .eq("cod_identificare", cod).limit(1).execute()
                if res_fin.data:
                    row_fin = res_fin.data[0]
                    toate_zero = all(
                        _to_float(row_fin.get(c)) == 0.0
                        for c in CAMPURI_VALOARE if c in row_fin
                    )
                    if toate_zero:
                        randuri_a15.append([
                            cod,
                            _first_nonempty(r, TITLE_FIELDS),
                            label,
                            _safe_text(r.get("status_contract_proiect")),
                        ])
            except Exception:
                pass
    total_afectate += len(randuri_a15)
    _alert_box(
        "Valoare financiară zero — status activ", len(randuri_a15), "orange", "🟠",
        randuri_a15, ["COD", "TITLU / OBIECT", "CATEGORIE", "STATUS"],
    )

    # ── A16: Proiecte fără persoană de contact ─────────────────────────
    randuri_a16 = []
    for t in TABELE_CU_DATE:
        rows_base = _fetch(supabase, t, "cod_identificare,titlul_proiect,obiectul_contractului")
        label = TABLE_LABELS.get(t, t)
        for r in rows_base:
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_ech = supabase.table("com_echipe_proiect") \
                    .select("persoana_contact") \
                    .eq("cod_identificare", cod).execute()
                if res_ech.data:
                    are_contact = any(
                        str(m.get("persoana_contact", "")).upper()
                        in ("TRUE", "1", "DA")
                        for m in res_ech.data
                    )
                    if not are_contact:
                        randuri_a16.append([
                            cod,
                            _first_nonempty(r, TITLE_FIELDS),
                            label,
                        ])
            except Exception:
                pass
    total_afectate += len(randuri_a16)
    _alert_box(
        "Fără persoană de contact desemnată", len(randuri_a16), "yellow", "🟡",
        randuri_a16, ["COD", "TITLU / OBIECT", "CATEGORIE"],
    )

    # ── A17: Coduri duplicate ──────────────────────────────────────────
    randuri_a17 = []
    toate_coduri = []
    for t in TOATE_TABELELE_BASE:
        rows = _fetch(supabase, t, "cod_identificare")
        for r in rows:
            cod = _safe_text(r.get("cod_identificare"))
            if cod:
                toate_coduri.append((cod, TABLE_LABELS.get(t, t)))

    from collections import Counter
    count_coduri = Counter(c for c, _ in toate_coduri)
    duplicate = {c for c, n in count_coduri.items() if n > 1}
    for cod, label in toate_coduri:
        if cod in duplicate:
            randuri_a17.append([cod, label])

    total_afectate += len(duplicate)
    _alert_box(
        "Coduri duplicate între tabele", len(duplicate), "red", "🔴",
        randuri_a17, ["COD DUPLICAT", "CATEGORIE"],
    )

    # ── A18: Proprietate industrială fără inventatori ──────────────────
    randuri_a18 = []
    rows_pi = _fetch(supabase, "base_prop_industr",
                     "cod_identificare,titlul_proprietatii,acronim_prop_industr")
    for r in rows_pi:
        cod = _safe_text(r.get("cod_identificare"))
        if not cod:
            continue
        try:
            res_ech = supabase.table("com_echipe_proiect") \
                .select("cod_identificare") \
                .eq("cod_identificare", cod).limit(1).execute()
            if not res_ech.data:
                randuri_a18.append([
                    cod,
                    _safe_text(r.get("titlul_proprietatii")),
                    _safe_text(r.get("acronim_prop_industr")),
                ])
        except Exception:
            pass
    total_afectate += len(randuri_a18)
    _alert_box(
        "Proprietate industrială fără inventatori în echipă", len(randuri_a18),
        "yellow", "🟡", randuri_a18,
        ["COD / NR. CERERE", "TITLU", "TIP"],
    )

    return total_afectate


# =========================================================
# CATEGORIA 3 — ALERTE FINANCIARE
# =========================================================

def _alerte_cat3(supabase: Client) -> int:
    total_afectate = 0

    _section_header("💰 CATEGORIA 3 — Alerte Financiare", 4)

    # ── A19: PNCDI/PNRR — sumă anuală ≠ sumă totală ───────────────────
    randuri_a19 = []
    for t in TABELE_FINANCIARE_PN:
        label = TABLE_LABELS.get(t, t)
        try:
            res = supabase.table("com_date_financiare_pn") \
                .select("cod_identificare,an_referinta,valoare_contract_an_referinta,"
                        "cofinantare_contract_an_referinta,valoare_totala_contract,"
                        "cofinantare_totala_contract") \
                .limit(5000).execute()
            rows = res.data or []
        except Exception:
            rows = []

        from itertools import groupby
        rows_sorted = sorted(rows, key=lambda r: _safe_text(r.get("cod_identificare")))
        for cod, grup in groupby(rows_sorted,
                                 key=lambda r: _safe_text(r.get("cod_identificare"))):
            grup_list = list(grup)
            suma_ani = sum(_to_float(r.get("valoare_contract_an_referinta")) for r in grup_list)
            cofin_ani = sum(_to_float(r.get("cofinantare_contract_an_referinta")) for r in grup_list)
            total_val = _to_float(grup_list[0].get("valoare_totala_contract"))
            total_cof = _to_float(grup_list[0].get("cofinantare_totala_contract"))
            diff_val = round(abs(suma_ani - total_val), 2)
            diff_cof = round(abs(cofin_ani - total_cof), 2)
            if diff_val > 0.01 or diff_cof > 0.01:
                randuri_a19.append([
                    cod,
                    label,
                    f"{suma_ani:,.2f}",
                    f"{total_val:,.2f}",
                    f"{diff_val:,.2f}",
                    f"{cofin_ani:,.2f}",
                    f"{total_cof:,.2f}",
                    f"{diff_cof:,.2f}",
                ])
    total_afectate += len(randuri_a19)
    _alert_box(
        "PNCDI/PNRR — Sumă anuală ≠ Sumă totală", len(randuri_a19), "red", "🔴",
        randuri_a19,
        ["COD", "CATEGORIE", "SUMA ANI", "TOTAL VAL.", "DIFF VAL.",
         "COFIN ANI", "TOTAL COFIN.", "DIFF COFIN."],
    )

    # ── A20: Valoare zero dar status activ (toate categoriile) ─────────
    # (similar A15 dar și pentru PNCDI/PNRR)
    STATUS_ACTIVE = {"activ", "active", "in derulare", "în derulare",
                     "implementare", "in implementare", "în implementare"}
    randuri_a20 = []
    for t in TABELE_FINANCIARE_PN:
        rows_base = _fetch(supabase, t,
                           "cod_identificare,titlul_proiect,status_contract_proiect")
        label = TABLE_LABELS.get(t, t)
        for r in rows_base:
            status = _safe_text(r.get("status_contract_proiect")).lower()
            if status not in STATUS_ACTIVE:
                continue
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_fin = supabase.table("com_date_financiare_pn") \
                    .select("valoare_totala_contract") \
                    .eq("cod_identificare", cod).limit(1).execute()
                if not res_fin.data or _to_float(
                        res_fin.data[0].get("valoare_totala_contract")) == 0.0:
                    randuri_a20.append([
                        cod,
                        _first_nonempty(r, TITLE_FIELDS),
                        label,
                        _safe_text(r.get("status_contract_proiect")),
                    ])
            except Exception:
                pass
    total_afectate += len(randuri_a20)
    _alert_box(
        "PNCDI/PNRR — Valoare totală zero cu status activ", len(randuri_a20),
        "orange", "🟠", randuri_a20,
        ["COD", "TITLU", "CATEGORIE", "STATUS"],
    )

    # ── A21: Cofinanțare lipsă pentru tipuri care o cer ───────────────
    TIPURI_CU_COFINANTARE = {
        "base_proiecte_pncdi", "base_proiecte_pnrr",
        "base_proiecte_internationale", "base_proiecte_interreg",
        "base_proiecte_see", "base_proiecte_structurale",
    }
    randuri_a21 = []
    for t in TIPURI_CU_COFINANTARE:
        label = TABLE_LABELS.get(t, t)
        rows_base = _fetch(supabase, t,
                           "cod_identificare,titlul_proiect,status_contract_proiect")
        fin_table = "com_date_financiare_pn" if t in TABELE_FINANCIARE_PN \
            else "com_date_financiare"
        cofin_field = "cofinantare_totala_contract" if t in TABELE_FINANCIARE_PN \
            else "cofinantare_upt_fdi"
        for r in rows_base:
            cod = _safe_text(r.get("cod_identificare"))
            if not cod:
                continue
            try:
                res_fin = supabase.table(fin_table) \
                    .select(cofin_field) \
                    .eq("cod_identificare", cod).limit(1).execute()
                if res_fin.data:
                    val = _to_float(res_fin.data[0].get(cofin_field))
                    if val == 0.0:
                        randuri_a21.append([
                            cod,
                            _first_nonempty(r, TITLE_FIELDS),
                            label,
                        ])
            except Exception:
                pass
    total_afectate += len(randuri_a21)
    _alert_box(
        "Cofinanțare lipsă pentru tipuri care o cer", len(randuri_a21),
        "yellow", "🟡", randuri_a21,
        ["COD", "TITLU", "CATEGORIE"],
    )

    # ── A22: Concentrare financiară — o categorie > 60% din total ─────
    valori_per_categorie = {}
    total_global = 0.0

    for t in TABELE_FINANCIARE_SIMPLE:
        label = TABLE_LABELS.get(t, t)
        try:
            res = supabase.table("com_date_financiare") \
                .select("cod_identificare,valoare_contract_cep_terti_speciale,"
                        "valoare_totala_contract,suma_aprobata_mec,"
                        "cost_total_proiect,costuri_totale_proiect,"
                        "grant_aprobat,buget_upt") \
                .limit(5000).execute()
            rows_fin = res.data or []
        except Exception:
            rows_fin = []

        rows_base = _fetch(supabase, t, "cod_identificare")
        coduri_tabela = {_safe_text(r.get("cod_identificare")) for r in rows_base}

        val_cat = 0.0
        for rf in rows_fin:
            cod = _safe_text(rf.get("cod_identificare"))
            if cod not in coduri_tabela:
                continue
            for camp in ["valoare_contract_cep_terti_speciale", "valoare_totala_contract",
                         "suma_aprobata_mec", "cost_total_proiect",
                         "costuri_totale_proiect", "grant_aprobat", "buget_upt"]:
                v = _to_float(rf.get(camp))
                if v > 0:
                    val_cat += v
                    break
        valori_per_categorie[label] = val_cat
        total_global += val_cat

    randuri_a22 = []
    if total_global > 0:
        for label, val in valori_per_categorie.items():
            pct = val / total_global
            if pct > PRAG_CONCENTRARE:
                randuri_a22.append([
                    label,
                    f"{val:,.2f}",
                    f"{pct * 100:.1f}%",
                    f"{total_global:,.2f}",
                ])

    total_afectate += len(randuri_a22)
    _alert_box(
        f"Concentrare financiară — o categorie depășește {int(PRAG_CONCENTRARE * 100)}% din total",
        len(randuri_a22), "orange", "🟠", randuri_a22,
        ["CATEGORIE", "VALOARE", "PROCENT", "TOTAL GLOBAL"],
    )

    return total_afectate


# =========================================================
# RENDER PRINCIPAL
# =========================================================

def render_tab3_alerte(supabase: Client) -> int:
    """
    Randează toate alertele și returnează numărul total
    de înregistrări afectate (pentru badge-ul din Tab3).
    """
    st.markdown(
        "<div style='color:rgba(255,255,255,0.88);font-size:1.02rem;font-weight:600;"
        "margin-bottom:0.85rem;'>Verificare automată a bazei de date pentru termene,"
        " calitate date și situații financiare critice."
        " Fiecare alertă poate fi expandată pentru detalii.</div>",
        unsafe_allow_html=True,
    )

    if not st.button("🔔 Calculează alertele", key="btn_calc_alerte",
                     use_container_width=False):
        st.info("Apăsați butonul de mai sus pentru a calcula alertele.", icon="ℹ️")
        return 0

    total = 0
    with st.spinner("Se verifică baza de date..."):
        total += _alerte_cat1(supabase)
        total += _alerte_cat2(supabase)
        total += _alerte_cat3(supabase)

    st.divider()
    culoare_total = "🔴" if total > 20 else "🟠" if total > 5 else "🟢"
    st.markdown(
        f"<div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.25);"
        f"border-radius:12px;padding:12px 20px;text-align:center;'>"
        f"<span style='color:#ffffff;font-weight:900;font-size:1.10rem;'>"
        f"{culoare_total} Total înregistrări afectate: <b>{total}</b></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    return total
