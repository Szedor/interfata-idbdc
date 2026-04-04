```python
def _render_echipa_compact(rows: list, cod_ctx: str = "", supabase=None):
    if not rows:
        st.info("Nu există echipă înregistrată pentru această fișă.")
        return

    rows_sorted   = sorted(rows, key=lambda r: (0 if _is_persoana_contact(r) else 1, str(r.get("nume_prenume") or "")))
    persoane_cont = [r for r in rows_sorted if _is_persoana_contact(r)]
    membri        = [r for r in rows_sorted if not _is_persoana_contact(r)]

    if persoane_cont:
        st.markdown(
            "<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;'"
            "text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;'>"
            "⭐ Persoana de contact</div>",
            unsafe_allow_html=True,
        )
        for r in persoane_cont:
            nume     = str(r.get("nume_prenume") or "").strip()
            rol      = str(r.get("functia_specifica") or "").strip()
            dept_row = str(r.get("acronim_departament") or "").strip()

            contact = _get_contact_info(supabase, nume)

            # Dacă departamentul vine deja din rândul echipei,
            # nu îl mai adăugăm încă o dată din contact
            if dept_row:
                contact = [c for c in contact if not c.startswith("🏛")]
                contact = [f"🏛 {dept_row}"] + contact

            txt = ", ".join(p for p in [nume, rol] if p)

            contact_html = ""
            if contact:
                contact_html = (
                    "  <span style='font-weight:800;color:#ffffff;'>" +
                    "  ·  ".join(_html.escape(c) for c in contact) + "</span>"
                )

            st.markdown(
                f"<div style='padding:6px 12px;margin-bottom:3px;background:rgba(255,255,255,0.10);"
                f"border-radius:8px;border-left:3px solid rgba(255,220,80,0.70);'>"
                f"<span style='font-weight:800;color:#ffffff;'>⭐ {_html.escape(txt)}</span>"
                f"{contact_html}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if not membri:
        return

    st.markdown(
        f"<div style='color:rgba(255,255,255,0.50);font-size:0.76rem;font-weight:700;'"
        f"text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>"
        f"👥 Membrii echipei ({len(membri)})</div>",
        unsafe_allow_html=True,
    )

    PREVIEW = 6

    show_all_key = f"echipa_show_all_{cod_ctx or id(rows)}"
    if show_all_key not in st.session_state:
        st.session_state[show_all_key] = False

    membri_display = membri if st.session_state[show_all_key] else membri[:PREVIEW]

    if st.session_state[show_all_key] and len(membri) > PREVIEW:
        filtru = st.text_input(
            "Cauta",
            value="",
            key=f"echipa_filter_{cod_ctx or id(rows)}",
            placeholder="Filtrează după nume...",
            label_visibility="collapsed",
        ).strip().lower()

        if filtru:
            membri_display = [
                r for r in membri
                if filtru in str(r.get("nume_prenume") or "").lower()
            ]

    def _fmt_membru(r):
        nume = str(r.get("nume_prenume") or "").strip()
        rol  = str(r.get("functia_specifica") or "").strip()

        if nume and rol:
            return f"{_html.escape(nume)} ({_html.escape(rol)})"

        return _html.escape(nume or rol)

    inline_text = "  ·  ".join(
        _fmt_membru(r) for r in membri_display if _fmt_membru(r)
    )

    st.markdown(
        f"<div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.12);"
        f"border-radius:10px;padding:10px 14px;line-height:1.9;font-size:0.88rem;"
        f"color:rgba(255,255,255,0.88);'>{inline_text}</div>",
        unsafe_allow_html=True,
    )

    if len(membri) > PREVIEW:
        if st.session_state[show_all_key]:
            if st.button(
                "▲ Restrânge lista",
                key=f"echipa_collapse_{cod_ctx or id(rows)}",
                use_container_width=False,
            ):
                st.session_state[show_all_key] = False
                st.rerun()
        else:
            ramasi = len(membri) - PREVIEW
            if st.button(
                f"▼ Arată toți cei {len(membri)} membri  (+{ramasi} ascunși)",
                key=f"echipa_expand_{cod_ctx or id(rows)}",
                use_container_width=False,
            ):
                st.session_state[show_all_key] = True
                st.rerun()
```
