import streamlit as st
from supabase import create_client, Client
from motor_admin import porneste_motorul

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
st.set_page_config(page_title="IDBDC – Administrare", layout="wide")
_MAINTENANCE_PASSWORD = "seLAN$EAZAin2026"

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return
    st.markdown("""
        <style>.stApp { background: #0b1a2e !important; }</style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align:center;margin-top:3rem;'>
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
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1.5, 1, 1.5])
    with mid:
        pwd = st.text_input("Parola de acces:", type="password", key="_mw_pwd_c2")
        if st.button("Acces platformă", key="_mw_btn_c2", use_container_width=True):
            if pwd == _MAINTENANCE_PASSWORD:
                st.session_state["_mw_cleared"] = True
                st.rerun()
            else:
                st.error("Parolă incorectă.")
    st.stop()

_maintenance_gate()
# ─────────────────────────────────────────────────────────────────────────────


TITLE_LINE_1 = "🛠️ Administrare baze de date"
TITLE_LINE_2 = "Departamentul Cercetare Dezvoltare Inovare"


def _check_gate_password(supabase: Client, gate: str, password: str) -> bool:
    try:
        res = supabase.rpc(
            "idbdc_check_gate_password",
            {"p_gate": gate, "p_password": password},
        ).execute()
        return bool(res.data)
    except Exception:
        return False


def run():
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)

    st.markdown(
        """
        <style>

            .stApp { background-color: #003366 !important; }

            [data-testid="stSidebar"] {
                background-color: #0b2a52 !important;
                border-right: 2px solid rgba(255,255,255,0.20);
            }

            .stApp h1, .stApp h2, .stApp h3, .stApp h4,
            .stApp p, .stApp label, .stApp .stMarkdown,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: white !important;
            }

            input {
                color: #000000 !important;
                background-color: #ffffff !important;
            }

            div.stButton > button {
                border: 1px solid white !important;
                color: white !important;
                background-color: rgba(255,255,255,0.10) !important;
                width: 100%;
                font-size: 14px !important;
                font-weight: bold !important;
                height: 42px !important;
            }

            div.stButton > button:hover {
                background-color: white !important;
                color: #003366 !important;
            }

            [data-testid="stToolbar"] { visibility: hidden !important; height: 0px !important; }
            [data-testid="stHeader"]  { visibility: hidden !important; height: 0px !important; }
            [data-testid="stDecoration"] { visibility: hidden !important; height: 0px !important; }

            #MainMenu { visibility: hidden !important; }

            .admin-header {
                text-align: center;
                margin-bottom: 20px;
            }

            .admin-title-1 {
                font-size: 2.0rem;
                font-weight: 900;
                color: #ffffff;
                margin: 0;
            }

            .admin-title-2 {
                font-size: 1.7rem;
                font-weight: 800;
                color: #ffffff;
                margin: 4px 0 0 0;
                opacity: 0.95;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )

    if "autorizat_p1" not in st.session_state:
        st.session_state.autorizat_p1 = False

    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None

    if "operator_rol" not in st.session_state:
        st.session_state.operator_rol = None

    if "operator_filtru_categorie" not in st.session_state:
        st.session_state.operator_filtru_categorie = []

    if "operator_filtru_tipuri" not in st.session_state:
        st.session_state.operator_filtru_tipuri = []

    st.markdown(
        f"""
        <div class="admin-header">
            <div class="admin-title-1">{TITLE_LINE_1}</div>
            <div class="admin-title-2">{TITLE_LINE_2}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("## 🔐 Autentificare")

    if not st.session_state.autorizat_p1:

        st.sidebar.markdown("### Pas 1 — Parolă acces modul")

        parola_m = st.sidebar.text_input("Parola:", type="password", key="p1_pass")

        if st.sidebar.button("Autorizare acces"):

            if _check_gate_password(supabase, "admin", parola_m):
                st.session_state.autorizat_p1 = True
                st.rerun()

            else:
                st.sidebar.error("Parolă greșită sau poarta este dezactivată.")

        st.info("Introduceți parola în bara din stânga pentru a continua.")
        st.stop()

    if not st.session_state.operator_identificat:

        st.sidebar.markdown("### Pas 2 — Cod operator")

        cod_in = st.sidebar.text_input("Cod Identificare:", type="password", key="p2_cod_input")

        if cod_in:

            try:
                res_op = (
                    supabase
                    .table("com_operatori")
                    .select("nume_prenume, rol, filtru_categorie, filtru_proiect")
                    .eq("cod_operatori", cod_in)
                    .execute()
                )

                if res_op.data:

                    st.session_state.operator_identificat = res_op.data[0].get("nume_prenume")
                    st.session_state.operator_rol = (res_op.data[0].get("rol") or "OPERATOR").strip()

                    # Filtre acces — text CSV -> lista Python
                    raw_cat = res_op.data[0].get("filtru_categorie") or ""
                    raw_tip = res_op.data[0].get("filtru_proiect") or ""
                    st.session_state.operator_filtru_categorie = [x.strip() for x in raw_cat.split(",") if x.strip()]
                    st.session_state.operator_filtru_tipuri    = [x.strip() for x in raw_tip.split(",") if x.strip()]

                    st.rerun()

                else:
                    st.sidebar.error("Cod operator invalid.")

            except Exception as e:
                st.sidebar.error(f"Eroare la verificarea operatorului: {e}")

        st.info("Introduceți codul de operator în bara din stânga pentru a intra în modul.")
        st.stop()

    st.sidebar.success(
        f"Operator: {st.session_state.operator_identificat}"
    )

    if st.sidebar.button("Ieșire / Resetare"):
        st.session_state.clear()
        st.rerun()

    porneste_motorul(supabase)


if __name__ == "__main__":
    run()
