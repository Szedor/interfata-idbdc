from config import Config

# =========================================================
# !! FISIER BETONAT — NU SE MODIFICA !!
# Mesajul de maintenance comun pentru toate caile IDBDC.
# Ultima versiune validata: 24.03.2026
# =========================================================

_MAINTENANCE_PASSWORD = Config.MAINTENANCE_PASSWORD

_MAINTENANCE_STYLE = """
    <style>
        .stApp { background: #0b1a2e !important; }
        .stButton > button { background: rgba(255,255,255,0.96) !important; color: #0b1f3a !important; -webkit-text-fill-color: #0b1f3a !important; opacity: 1 !important; }
        .stButton > button p { color: #0b1f3a !important; -webkit-text-fill-color: #0b1f3a !important; }
    </style>
"""

_MAINTENANCE_HTML = """
    <div style='text-align:center;margin-top:1rem;'>
        <div style='font-size:2.2rem;'>&#9888;&#65039;</div>
        <div style='color:#ffffff;font-size:1.10rem;font-weight:900;
                    letter-spacing:0.06em;margin:0.5rem 0;'>
            IMPORTANT !
        </div>
        <div style='background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.28);
                    border-radius:12px;padding:16px 24px;
                    color:rgba(255,255,255,0.88);font-size:0.88rem;
                    max-width:560px;margin:0 auto 1.5rem auto;line-height:1.70;'>
            <span style='color:#ffdd88;'>
            Platforma <b>IDBDC-UPT</b>
            (<i>Interogare — Dezvoltare Baze de Date Cercetare – UPT</i>)
            a intrat în testarea finală a celor aproape <b>6.000 de linii de cod</b>,
            din <b>11 fișiere principale Python</b>, dintre care 5 fișiere sunt
            dedicate modulelor AI, <b>93 de funcții și algoritmi definiți</b>,
            <b>24 de tabele de baze de date</b> cu <b>122 de câmpuri de date distincte</b>,
            precum și a securității asigurate prin <b>5 niveluri de autentificare</b>.
            </span><br><br>
            <span style='color:rgba(255,255,255,0.82);'>
            După finalizarea procesului de testare finală se va trece la încărcarea
            cu date reale, atât curente cât și istorice. Pentru această etapă
            va fi vizibil permanent un <b>grafic de progres anual</b> pentru fiecare categorie
            — contracte și proiecte pe tipuri, evenimente științifice și
            proprietate industrială — dar și o <b>numărătoare inversă</b>
            până la deschiderea accesului.
            </span>
        </div>
    </div>
"""


def maintenance_gate(st, pwd_key: str, btn_key: str):
    """
    Afișează ecranul de maintenance și blochează accesul până la introducerea parolei.
    st       — modulul streamlit
    pwd_key  — cheie unică pentru widget-ul de parolă (ex: '_mw_pwd_c1')
    btn_key  — cheie unică pentru butonul de acces (ex: '_mw_btn_c1')
    Cheia de stare este derivată din btn_key pentru a fi unică per cale.
    """
    _cleared_key = f"_mw_cleared_{btn_key}"
    if st.session_state.get(_cleared_key):
        return
    st.markdown(_MAINTENANCE_STYLE, unsafe_allow_html=True)
    st.markdown(_MAINTENANCE_HTML, unsafe_allow_html=True)
    _, mid, _ = st.columns([1.5, 1, 1.5])
    with mid:
        pwd = st.text_input("Parola de acces:", type="password", key=pwd_key)
        if st.button("Acces platformă", key=btn_key, use_container_width=True):
            if pwd == _MAINTENANCE_PASSWORD:
                st.session_state[_cleared_key] = True
                st.rerun()
            else:
                st.error("Parolă incorectă.")
    st.stop()
