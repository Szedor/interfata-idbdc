import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURARE & PARSARE LINK (DISPECERUL)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")

# Citim din link ce pagină vrea utilizatorul (implicit: explorator)
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# Stil Vizual (Albastru UPT)
st.markdown("""
<style>
    .stApp { background-color: #003366; }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label, .stApp .stMarkdown { color: white !important; }
</style>
""", unsafe_allow_html=True)

# Conectare Supabase
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE (Public/Vizitator)
# Link: ...app.py?pagina=explorator
# ==========================================
if calea_activa == "explorator":
    st.markdown("# 🔍 Explorator de Date IDBDC")
    st.write("Vizualizare și interogare date publice de cercetare.")
    
    # i) Alege categoria
    try:
        res_cat = supabase.table("nom_categorie").select("denumire_categorie").execute()
        cat_selectata = st.selectbox("Alege categoria de informații:", ["---"] + [item["denumire_categorie"] for item in res_cat.data])

        if cat_selectata == "Contracte & Proiecte":
            res_tip = supabase.table("nom_contracte_proiecte").select("acronim_contracte_proiecte").execute()
            tip_ales = st.selectbox("i1.1) Alege tipul de contract sau proiect:", ["---"] + [item["acronim_contracte_proiecte"] for item in res_tip.data])

            if tip_ales != "---":
                # Aici vine logica ta de filtrare (An, ID, Director, Departament)
                st.info(f"Se încarcă datele pentru {tip_ales}...")
                # ... codul de filtrare discutat ...
    except Exception as e:
        st.error("Eroare la conectarea bazei de date.")

# ==========================================
# CALEA 2: CONSOLA DE ADMINISTRARE (Specialist)
# Link: ...app.py?pagina=admin
# ==========================================
elif calea_activa == "admin":
    # Aici avem bariera de securitate (Porțile 1 și 2)
    if 'autorizat_p1' not in st.session_state: st.session_state.autorizat_p1 = False
    
    if not st.session_state.autorizat_p1:
        st.markdown("# 🛡️ Consola de Administrare")
        # Logica de parolă master
        parola = st.text_input("Introduceți parola de sistem:", type="password")
        if st.button("Acces"):
            if parola == "EverDream2SZ":
                st.session_state.autorizat_p1 = True
                st.rerun()
        st.stop()

    st.markdown("# 🛠️ Panou Administrare (CRUD)")
    st.write("Gestionare baze de date (Adăugare/Editare).")

# ==========================================
# CALEA 3: BRAINSTORMING AI (Profesor)
# Link: ...app.py?pagina=ai
# ==========================================
elif calea_activa == "ai":
    st.markdown("# 🧠 Brainstorming AI pentru Cercetare")
    st.write("Modul dedicat generării de idei și analizei predictive.")
    # Logica AI viitoare
