# =========================================================
# IDBDC/domenii/proiecte_pnrr/financiar.py
# VERSIUNE: 2.0
# STATUS: RESTRUCTURAT
# DATA: 2026.06.02
# =========================================================
# Structură:
#   - Selectbox VALUTA compact
#   - Zona 1: VALOARE TOTALA + COFINANTARE TOTALA
#   - Zona 2: tabel anual (5 rânduri inițial, extendabil)
#   - Validare live: suma anuală = total
# Tabelă: com_date_financiare_pn
# Cheie compusă: cod_identificare + an_referinta
# =========================================================

import streamlit as st
import pandas as pd


VALUTE         = ["LEI", "EUR", "USD"]
NR_ANI_INIT    = 5


def render(supabase, cod_introdus, is_new, date_existente):

    # ── Citire date existente ──────────────────────────────────────────
    if is_new or not date_existente:
        rows_ex = []
    else:
        rows_ex = date_existente if isinstance(date_existente, list) else [date_existente]

    def _sf(val):
        if val is None or val == "":
            return 0.0
        try:
            return float(val)
        except (TypeError, ValueError):
            return 0.0

    # Valuta și totaluri din primul rând (toate rândurile au aceleași totaluri)
    valuta_ex       = "LEI"
    total_val_ex    = 0.0
    total_cofin_ex  = 0.0
    if rows_ex:
        valuta_ex      = rows_ex[0].get("valuta") or "LEI"
        if valuta_ex not in VALUTE:
            valuta_ex = "LEI"
        total_val_ex   = _sf(rows_ex[0].get("valoare_totala_contract"))
        total_cofin_ex = _sf(rows_ex[0].get("cofinantare_totala_contract"))

    # ── VALUTA — compact ──────────────────────────────────────────────
    col_v, col_empty = st.columns([1, 3])
    with col_v:
        valuta = st.selectbox(
            "🔖 VALUTA",
            options=VALUTE,
            index=VALUTE.index(valuta_ex),
            key=f"pnrr_valuta_{cod_introdus}",
        )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── ZONA 1: Valori totale ─────────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;"
        "font-weight:700;text-transform:uppercase;letter-spacing:0.05em;"
        "margin-bottom:6px;'>① Valori totale contract</div>",
        unsafe_allow_html=True,
    )

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        valoare_totala = st.number_input(
            f"VALOARE TOTALA ({valuta})",
            min_value=0.0,
            value=total_val_ex,
            format="%.2f",
            key=f"pnrr_val_total_{cod_introdus}",
        )
    with col_t2:
        cofin_totala = st.number_input(
            f"COFINANTARE TOTALA ({valuta})",
            min_value=0.0,
            value=total_cofin_ex,
            format="%.2f",
            key=f"pnrr_cofin_total_{cod_introdus}",
        )

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── ZONA 2: Valori anuale ─────────────────────────────────────────
    st.markdown(
        "<div style='color:rgba(255,255,255,0.70);font-size:0.88rem;"
        "font-weight:700;text-transform:uppercase;letter-spacing:0.05em;"
        "margin-bottom:6px;'>② Valori anuale</div>",
        unsafe_allow_html=True,
    )

    # Inițializare date anuale
    key_ani = f"pnrr_ani_data_{cod_introdus}"
    if key_ani not in st.session_state:
        if rows_ex:
            st.session_state[key_ani] = [
                {
                    "AN": int(r.get("an_referinta") or 0),
                    "VALOARE AN": _sf(r.get("valoare_contract_an_referinta")),
                    "COFINANTARE AN": _sf(r.get("cofinantare_contract_an_referinta")),
                }
                for r in rows_ex if r.get("an_referinta")
            ]
            # Completăm până la NR_ANI_INIT dacă e mai puțin
            while len(st.session_state[key_ani]) < NR_ANI_INIT:
                st.session_state[key_ani].append(
                    {"AN": 0, "VALOARE AN": 0.0, "COFINANTARE AN": 0.0}
                )
        else:
            st.session_state[key_ani] = [
                {"AN": 0, "VALOARE AN": 0.0, "COFINANTARE AN": 0.0}
                for _ in range(NR_ANI_INIT)
            ]

    df_ani = pd.DataFrame(st.session_state[key_ani])

    col_cfg_ani = {
        "AN": st.column_config.NumberColumn(
            "🔢 AN REFERINTA",
            format="%d",
            min_value=1990,
            max_value=2100,
            required=False,
        ),
        "VALOARE AN": st.column_config.NumberColumn(
            f"VALOARE AN ({valuta})",
            format="%,.2f",
            min_value=0.0,
        ),
        "COFINANTARE AN": st.column_config.NumberColumn(
            f"COFINANTARE AN ({valuta})",
            format="%,.2f",
            min_value=0.0,
        ),
    }

    df_edit = st.data_editor(
        df_ani,
        column_config=col_cfg_ani,
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=f"pnrr_ani_editor_{cod_introdus}",
    )

    # Buton adăugare an
    if st.button("➕ Adaugă an", key=f"pnrr_add_an_{cod_introdus}"):
        # Sincronizăm datele curente din editor
        rows_curente = []
        for _, row in df_edit.iterrows():
            rows_curente.append({
                "AN": int(row["AN"]) if row["AN"] and not pd.isna(row["AN"]) else 0,
                "VALOARE AN": float(row["VALOARE AN"] or 0),
                "COFINANTARE AN": float(row["COFINANTARE AN"] or 0),
            })
        rows_curente.append({"AN": 0, "VALOARE AN": 0.0, "COFINANTARE AN": 0.0})
        st.session_state[key_ani] = rows_curente
        if f"pnrr_ani_editor_{cod_introdus}" in st.session_state:
            del st.session_state[f"pnrr_ani_editor_{cod_introdus}"]
        st.rerun()

    # ── ZONA 3: Validare live ─────────────────────────────────────────
    suma_val_ani   = float(df_edit["VALOARE AN"].fillna(0).sum())
    suma_cofin_ani = float(df_edit["COFINANTARE AN"].fillna(0).sum())

    diff_val   = round(abs(valoare_totala - suma_val_ani), 2)
    diff_cofin = round(abs(cofin_totala - suma_cofin_ani), 2)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Construim mesajul de validare
    ok_val   = diff_val == 0.0
    ok_cofin = diff_cofin == 0.0

    if ok_val and ok_cofin:
        st.markdown(
            "<div style='background:rgba(34,197,94,0.12);border:1px solid rgba(34,197,94,0.45);"
            "border-radius:10px;padding:9px 14px;'>"
            "<span style='color:#4ade80;font-weight:700;font-size:0.92rem;'>"
            "✅ Valorile anuale corespund valorilor totale."
            "</span></div>",
            unsafe_allow_html=True,
        )
    else:
        linii = []
        if not ok_val:
            linii.append(
                f"Valoare: suma anuală <b>{suma_val_ani:,.2f}</b> ≠ "
                f"total <b>{valoare_totala:,.2f}</b> "
                f"(diferență: <b>{diff_val:,.2f} {valuta}</b>)"
            )
        if not ok_cofin:
            linii.append(
                f"Cofinanțare: suma anuală <b>{suma_cofin_ani:,.2f}</b> ≠ "
                f"total <b>{cofin_totala:,.2f}</b> "
                f"(diferență: <b>{diff_cofin:,.2f} {valuta}</b>)"
            )
        mesaj = "<br>".join(linii)
        st.markdown(
            f"<div style='background:rgba(255,180,0,0.12);border:1px solid rgba(255,180,0,0.55);"
            f"border-radius:10px;padding:9px 14px;'>"
            f"<span style='color:#fbbf24;font-weight:700;font-size:0.92rem;'>"
            f"⚠️ Atenție — neconcordanță între valorile anuale și totaluri:<br>{mesaj}"
            f"</span></div>",
            unsafe_allow_html=True,
        )

    # ── Construire rezultat pentru salvare ────────────────────────────
    rezultat = []
    for _, row in df_edit.iterrows():
        an = row.get("AN")
        try:
            an_int = int(an) if an and not pd.isna(an) else 0
        except (TypeError, ValueError):
            an_int = 0
        if an_int == 0:
            continue
        rezultat.append({
            "cod_identificare":                  cod_introdus,
            "valuta":                            valuta,
            "an_referinta":                      an_int,
            "valoare_contract_an_referinta":     float(row["VALOARE AN"] or 0),
            "cofinantare_contract_an_referinta": float(row["COFINANTARE AN"] or 0),
            "valoare_totala_contract":           valoare_totala,
            "cofinantare_totala_contract":       cofin_totala,
        })

    return rezultat
