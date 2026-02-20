import streamlit as st
import psycopg2

st.set_page_config(page_title="Consola IDBDC", layout="wide")

def get_connection():
return psycopg2.connect(
host=st.secrets["postgres"]["host"],
database=st.secrets["postgres"]["database"],
user=st.secrets["postgres"]["user"],
password=st.secrets["postgres"]["password"],
port=st.secrets["postgres"]["port"]
)

if "auth_p1" not in st.session_state:
st.session_state["auth_p1"] = False

if not st.session_state["auth_p1"]:
st.title("🛡️ Acces Sistem")
pwd = st.text_input("Parolă Sistem:", type="password")
if st.button("Validare"):
if pwd == "EverDream2SZ":
st.session_state["auth_p1"] = True
st.rerun()
st.stop()

def get_op(cod):
if not cod: return None
try:
conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT nume_prenume FROM com_operatori WHERE TRIM(cod_acces) = %s", (cod.strip(),))
res = cur.fetchone()
cur.close()
conn.close()
return res[0] if res else None
except: return None

st.sidebar.title("👤 Identificare")
c_in = st.sidebar.text_input("Cod RESP:", type="password").upper()
nume_op = get_op(c_in)

if nume_op:
st.sidebar.success(f"Salut, {nume_op}!")
st.title(f"Atelier: {nume_op}")
st.write("Sursă date: base_proiecte_fdi")
else:
if c_in: st.sidebar.error("Cod invalid!")
else: st.info("Introdu codul RESP în sidebar.")
