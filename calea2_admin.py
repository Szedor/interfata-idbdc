import streamlit as st
from supabase import create_client, Client
from motor_admin import porneste_motorul


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

    # === STYLE (sidebar + ascundere toolbar Streamlit) ===
    st.markdown(
        """
        <style>
            /* Fundal aplicație */
            .stApp { background-color: #003366 !important; }

            /* Sidebar: culoare constantă */
            [data-testid="stSidebar"] {
                background-color: #0b2a52 !important;
                border-right: 2px solid rgba(255,255,255,0.20);
            }

            /* Text alb */
            .stApp h1, .stApp h2, .stApp h3, .stApp h4,
            .stApp p, .stApp label, .stApp .stMarkdown,
            [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
                color: white !important;
            }

            /* Input-uri clare */
            input {
                color: #000000 !important;
                background-color: #ffffff !important;
            }

            /* Butoane */
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

            /* ASCUNDE bara Streamlit (Share / GitHub / etc.) */
            [data-testid="stToolbar"] { visibility: hidden !important; height: 0px !important; }
            [data-testid="stHeader"]  { visibility: hidden !important; height: 0px !important; }
            [data-testid="stDecoration"] { visibility: hidden !important; height: 0px !important; }

            /* (opțional) ascunde meniul din dreapta sus, dacă apare */
            #MainMenu { visibility: hidden !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # === SESSION ===
    if "autorizat_p1" not in st.session_state:
        st.session_state.autorizat_p1 = False
    if "operator_identificat" not in st.session_state:
        st.session_state.operator_identificat = None
    if "operator_rol" not in st.session_state:
        st.session_state.operator_rol = None

    # === UI principal (titlu) ===
    st.markdown("<h2 style='text-align:center;'>🛠️ Consola de administrare IDBDC</h2>", unsafe_allow_html=True)

    # === Sidebar: autentificare completă (de la început) ===
    st.sidebar.markdown("## 🔐 Autentificare")

    # 1) Poarta
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

    # 2) Operator
    if not st.session_state.operator_identificat:
        st.sidebar.markdown("### Pas 2 — Cod operator")
        cod_in = st.sidebar.text_input("Cod Identificare:", type="password", key="p2_cod_input")

        if cod_in:
            try:
                res_op = (
                    supabase.table("com_operatori")
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

    # Operator logat
    st.sidebar.success(f"Operator: {st.session_state.operator_identificat} ({st.session_state.operator_rol})")
    if st.sidebar.button("Ieșire / Resetare"):
        st.session_state.clear()
        st.rerun()

    # pornește motorul Admin
    porneste_motorul(supabase)


if __name__ == "__main__":
    run()
