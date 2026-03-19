import streamlit as st
from supabase import create_client, Client
from motor_admin import porneste_motorul

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
_MAINTENANCE_PASSWORD = "seLAN$EAZAin2026"

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return
    st.markdown("""
        <style>
        .stApp { background: #0b2a52 !important; }
        </style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='display:flex;justify-content:center;align-items:center;
                    min-height:80vh;'>
          <div style='background:rgba(255,255,255,0.07);border:2px solid rgba(255,255,255,0.25);
                      border-radius:20px;padding:40px 48px;max-width:680px;width:100%;
                      box-shadow:0 20px 60px rgba(0,0,0,0.40);text-align:center;'>

            <div style='font-size:2.8rem;margin-bottom:0.5rem;'>&#9888;&#65039;</div>

            <div style='color:#ffffff;font-size:1.55rem;font-weight:900;
                        letter-spacing:0.06em;margin-bottom:1.2rem;'>
              IMPORTANT !
            </div>

            <div style='color:rgba(255,255,255,0.90);font-size:0.97rem;
                        line-height:1.75;text-align:justify;margin-bottom:1.4rem;'>
              Platforma <strong>IDBDC-UPT</strong>
              (<em>Interogare &#8212; Dezvoltare Baze de Date Cercetare &#8211; UPT</em>)
              a intrat &#238;n testarea final&#259; a celor aproape <strong>6.000 de linii de cod</strong>,
              din <strong>11 fi&#351;iere principale Python</strong>, dintre care 5 fi&#351;iere sunt
              dedicate modulelor AI, <strong>93 de func&#355;ii &#351;i algoritmi defini&#355;i</strong>,
              <strong>24 de tabele de baze de date</strong> cu
              <strong>122 de c&#226;mpuri de date distincte</strong>, precum &#351;i a securit&#259;&#355;ii
              asigurate prin <strong>5 niveluri de autentificare</strong>.<br><br>
              Dup&#259; finalizarea procesului de testare final&#259; se va trece la &#238;nc&#259;rcarea cu
              date reale, at&#226;t curente c&#226;t &#351;i istorice. Pentru aceast&#259; etap&#259; va fi vizibil
              permanent un <strong>grafic de progres anual</strong> pentru fiecare categorie
              &#8212; contracte &#351;i proiecte pe tipuri, evenimente &#351;tiin&#355;ifice &#351;i proprietate
              industrial&#259; &#8212; dar &#351;i o <strong>num&#259;r&#259;toare invers&#259;</strong> p&#226;n&#259; la
              deschiderea accesului.
            </div>

            <div style='color:rgba(255,255,255,0.45);font-size:0.80rem;
                        margin-bottom:1.2rem;font-style:italic;'>
              Acces temporar restric&#355;ionat &#183; Introduce&#355;i parola pentru a continua
            </div>

          </div>
        </div>
    """, unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        pwd = st.text_input("Parola de acces:", type="password", key="_mw_pwd_c2")
        if st.button("Acces platform&#259;", key="_mw_btn_c2", use_container_width=True):
            if pwd == _MAINTENANCE_PASSWORD:
                st.session_state["_mw_cleared"] = True
                st.rerun()
            else:
                st.error("Parol&#259; incorect&#259;.")
    st.stop()

_maintenance_gate()# ─────────────────────────────────────────────────────────────────────────────


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
                    .select("nume_prenume, rol")
                    .eq("cod_operatori", cod_in)
                    .execute()
                )

                if res_op.data:

                    st.session_state.operator_identificat = res_op.data[0].get("nume_prenume")
                    st.session_state.operator_rol = (res_op.data[0].get("rol") or "OPERATOR").strip()

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
