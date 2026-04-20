def _render_sectiune_tabel(section_label: str, rows: list, table: str = None,
                           tabela_baza_ctx: str = None):
    if not rows:
        return
    priority_set = {c: i for i, c in enumerate(CARD_PRIORITY)}
    is_contract_ctx = (tabela_baza_ctx or table or "") in _TABELE_CONTRACTE
    extra_hidden = _COLS_EXCLUDE_CONTRACTE if is_contract_ctx else set()
    all_items = []
    for row in rows:
        visible_cols = [
            c for c in row.keys()
            if c not in COLS_HIDDEN_FISA
            and c not in extra_hidden
            and row[c] is not None
            and str(row[c]).strip() not in ("", "None", "nan")
        ]
        # Noua ordine pentru secțiunea Generale (identică cu administrare)
        COL_ORDER_GENERALE = [
            "denumire_categorie", "acronim_tip_contract", "cod_identificare",
            "data_contract", "obiectul_contractului", "denumire_beneficiar",
            "data_inceput", "data_sfarsit", "durata",
            "status_contract_proiect", "observatii"
        ]
        COL_ORDER_FINANCIAR = [
            "cod_identificare", "valuta",
            "valoare_contract_cep_terti_speciale",
            "valoare_anuala_contract", "valoare_totala_contract",
            "cofinantare_anuala_contract", "cofinantare_totala_contract",
            "suma_solicitata_fdi", "cofinantare_upt_fdi",
            "cost_total_proiect", "cost_proiect_upt",
            "contributie_ue_total_proiect", "contributie_ue_proiect_upt",
        ]
        if table == "com_aspecte_tehnice":
            ordered = [c for c in TEHNIC_COL_ORDER if c in visible_cols]
            rest = [c for c in visible_cols if c not in TEHNIC_COL_ORDER]
            visible_cols = ordered + rest
        elif table == "com_date_financiare":
            ordered = [c for c in COL_ORDER_FINANCIAR if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_FINANCIAR]
            visible_cols = ordered + rest
        else:
            ordered = [c for c in COL_ORDER_GENERALE if c in visible_cols]
            rest = [c for c in visible_cols if c not in COL_ORDER_GENERALE]
            visible_cols = ordered + rest
        for c in visible_cols:
            raw_val = row[c]
            try:
                float(str(raw_val).replace(",", ".").strip())
                is_num = True
            except (ValueError, TypeError):
                is_num = False
            val_str = _fmt_numeric(raw_val, c) if is_num else str(raw_val)
            all_items.append((_col_label(c, table), _html.escape(val_str)))
    if not all_items:
        st.info(f"Nu există câmpuri completate pentru secțiunea {section_label}.")
        return
    rows_html = ""
    for i, (label, value) in enumerate(all_items):
        sec_cell = ""
        if i == 0:
            sec_cell = (
                f"<td rowspan='{len(all_items)}' style='vertical-align:top;padding:6px 10px 6px 0;width:10%;'>"
                f"<span style='color:rgba(255,255,255,0.45);font-size:0.74rem;font-weight:800;"
                f"text-transform:uppercase;letter-spacing:0.07em;white-space:nowrap;'>"
                f"{_html.escape(section_label)}</span>"
                f""
                f""
            )
        rows_html += (
            f"<tr>"
            f"{sec_cell}"
            f"<td style='padding:3px 12px 3px 0;width:23%;vertical-align:top;'>"
            f"<span style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:0.04em;'>{label}</span>"
            f""
            f""
            f"<td style='padding:3px 0 3px 0;width:67%;vertical-align:top;'>"
            f"<span style='color:#ffffff;font-size:0.95rem;font-weight:700;'>{value}</span>"
            f""
            f""
            f"</tr>"
        )
    st.markdown(
        f"<table style='width:100%;border-collapse:collapse;margin-bottom:0;'>{rows_html}</table>",
        unsafe_allow_html=True,
    )
