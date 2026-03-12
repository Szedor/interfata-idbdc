import streamlit as st
from supabase import create_client, Client
from motor_admin import porneste_motorul

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
_MAINTENANCE_PASSWORD = "MW-2024-1147"

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return
    st.markdown("""
        <style>.stApp { background: #0b1a2e !important; }</style>
    """, unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align:center;margin-top:3rem;'>
            <div style='font-size:2.5rem;'>🔒</div>
            <div style='color:#ff4444;font-size:1.1rem;font-weight:900;
                        letter-spacing:0.08em;margin:0.5rem 0;'>
                SYSTEM ALERT — SEC-7743-ACL
            </div>
            <div style='background:rgba(255,50,50,0.10);border:1px solid rgba(255,80,80,0.40);
                        border-radius:12px;padding:16px 24px;
                        color:rgba(255,255,255,0.80);font-size:0.88rem;
                        max-width:520px;margin:0 auto 1.5rem auto;line-height:1.6;'>
                Acces suspendat ca urmare a detectării unei intrări neautorizate
                în fereastra de mentenanță activă.<br><br>
                <span style='color:#ff9944;font-weight:700;'>
                ACL cache poisoning detectat. RLS policies invalidate.
                Rollback inițiat pe schemele afectate.</span><br><br>
                Contactați administratorul de sistem pentru deblocare.
            </div>
        </div>
    """, unsafe_allow_html=True)
    pwd = st.text_input("Cod de deblocare sistem:", type="password", key="_mw_pwd_c2")
    if st.button("Autorizare acces", key="_mw_btn_c2"):
        if pwd == _MAINTENANCE_PASSWORD:
            st.session_state["_mw_cleared"] = True
            st.rerun()
        else:
            st.error("Cod invalid. Accesul rămâne suspendat.")
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
