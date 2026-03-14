import streamlit as st
from supabase import create_client, Client
from motor_admin import porneste_motorul

# ── MAINTENANCE LOCK ──────────────────────────────────────────────────────────
_MAINTENANCE_PASSWORD = "MW-2024-1147"

# ── DATA ȚINTĂ LANSARE — modificați doar această linie ────────────────────────
import datetime as _dt
_LAUNCH_DATE = _dt.datetime(2026, 3, 25, 9, 0, 0)   # an, lună, zi, oră, min, sec
# ─────────────────────────────────────────────────────────────────────────────

def _maintenance_gate():
    if st.session_state.get("_mw_cleared"):
        return

    now   = _dt.datetime.now()
    delta = _LAUNCH_DATE - now
    total_secs = max(int(delta.total_seconds()), 0)
    days    = total_secs // 86400
    hours   = (total_secs % 86400) // 3600
    minutes = (total_secs % 3600) // 60
    seconds = total_secs % 60

    st.markdown("""
        <style>
        .stApp { background: #06111f !important; }
        button[kind="primary"], .stButton > button {
            background: #1a4a8a !important;
            color: #fff !important;
            border: none !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div style='text-align:center; margin-top:2.5rem; font-family:sans-serif;'>

            <div style='font-size:2.8rem; margin-bottom:0.3rem;'>🔬</div>
            <div style='color:#e8f0ff; font-size:1.25rem; font-weight:700;
                        letter-spacing:0.04em; margin-bottom:0.2rem;'>
                IDBDC — UPT
            </div>
            <div style='color:#7fa8d8; font-size:0.82rem; margin-bottom:2rem;
                        letter-spacing:0.06em; text-transform:uppercase;'>
                Departamentul Cercetare · Dezvoltare · Inovare
            </div>

            <div style='background:rgba(26,74,138,0.18); border:1px solid rgba(100,160,255,0.25);
                        border-radius:16px; padding:24px 32px;
                        max-width:520px; margin:0 auto 2.2rem auto; line-height:1.7;'>
                <div style='color:#c8deff; font-size:1.0rem; font-weight:600; margin-bottom:0.6rem;'>
                    ⚙️ Platformă în pregătire finală
                </div>
                <div style='color:rgba(200,222,255,0.75); font-size:0.88rem;'>
                    Echipa IDBDC finalizează încărcarea bazelor de date și ultimele ajustări.<br>
                    Platforma va fi disponibilă integral la data afișată mai jos.<br><br>
                    <span style='color:#90c0ff;'>
                        Vă mulțumim pentru răbdare!
                    </span>
                </div>
            </div>

            <div style='display:flex; justify-content:center; gap:16px; margin-bottom:2rem;
                        flex-wrap:wrap;'>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-days' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{days:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Zile</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-hours' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{hours:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Ore</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-min' style='color:#60aaff; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{minutes:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Minute</div>
                </div>
                <div style='background:rgba(255,255,255,0.06); border:1px solid rgba(100,160,255,0.20);
                            border-radius:12px; padding:14px 20px; min-width:78px;'>
                    <div id='cd-sec' style='color:#f0c060; font-size:2.2rem; font-weight:800;
                                line-height:1;'>{seconds:02d}</div>
                    <div style='color:#7fa8d8; font-size:0.70rem; letter-spacing:0.08em;
                                margin-top:4px; text-transform:uppercase;'>Secunde</div>
                </div>
            </div>

            <div style='color:rgba(140,180,255,0.55); font-size:0.78rem; margin-bottom:2rem;'>
                Data estimată lansare:
                <strong style='color:rgba(160,200,255,0.80);'>
                    {_LAUNCH_DATE.strftime("%d %B %Y, ora %H:%M")}
                </strong>
            </div>

        </div>

        <script>
        (function() {{
            var target = new Date("{_LAUNCH_DATE.strftime('%Y-%m-%dT%H:%M:%S')}").getTime();
            function tick() {{
                var now  = Date.now();
                var diff = Math.max(0, Math.floor((target - now) / 1000));
                var d = Math.floor(diff / 86400);
                var h = Math.floor((diff % 86400) / 3600);
                var m = Math.floor((diff % 3600) / 60);
                var s = diff % 60;
                var pad = function(n) {{ return n < 10 ? '0' + n : '' + n; }};
                var el;
                if ((el = document.getElementById('cd-days')))  el.textContent = pad(d);
                if ((el = document.getElementById('cd-hours'))) el.textContent = pad(h);
                if ((el = document.getElementById('cd-min')))   el.textContent = pad(m);
                if ((el = document.getElementById('cd-sec')))   el.textContent = pad(s);
            }}
            setInterval(tick, 1000);
            tick();
        }})();
        </script>
    """, unsafe_allow_html=True)

    pwd = st.text_input("Cod acces anticipat:", type="password", key="_mw_pwd_c2")
    if st.button("Autorizare acces", key="_mw_btn_c2"):
        if pwd == _MAINTENANCE_PASSWORD:
            st.session_state["_mw_cleared"] = True
            st.rerun()
        else:
            st.error("Cod incorect.")
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
