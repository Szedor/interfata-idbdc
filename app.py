import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. MOTORUL (DISPECERUL)
# ==========================================
st.set_page_config(page_title="IDBDC UPT", layout="wide")
query_params = st.query_params
calea_activa = query_params.get("pagina", "explorator")

# (Presupunem conectarea Supabase deja configurată în st.secrets)

# ==========================================
# CALEA 1: EXPLORATOR DE DATE
# ==========================================
if calea_activa == "explorator":
    st.markdown("<h1 style='text-align: center;'>🔍 Explorator de date</h1>", unsafe_allow_html=True)
    st.write("---")

    # GRID SELECȚIE PRINCIPALĂ
    c1, c2, c3 = st.columns(3)
    with c1:
        # 1. Categoria (Sursa: nom_categorie)
        cat_selectata = st.selectbox("1. Categoria de informații:", ["---", "Contracte & Proiecte"])

    with c2:
        # 2. Tipul (Sursa: nom_contracte_proiecte)
        tip_ales = "---"
        if cat_selectata == "Contracte & Proiecte":
            tip_ales = st.selectbox("2. Tipul de contract / proiect:", ["---", "FDI", "PNRR", "ORIZONT"])

    # CELE 9 CASETE PENTRU CONTRACTE & PROIECTE
    if cat_selectata == "Contracte & Proiecte" and tip_ales != "---":
        st.write("---")
        st.markdown(f"#### 🛠️ Configurare Filtre: {tip_ales}")
        
        f1, f2, f3 = st.columns(3)
        
        with f1:
            # 3. ID (Sursa: cod_identificare)
            id_proiect = st.text_input("3. ID proiect / Nr. contract")
            # 4. Acronim (Sursa: acronim_proiect)
            acronim = st.text_input("4. Acronim proiect")
            # 5. Titlu (Sursa: titlul_proiect)
            titlu = st.text_input("5. Titlul proiectului / Obiect contract")

        with f2:
            # 6. Director (Sursa: com_echipe_proiecte unde reprezinta_idbdc='DA')
            director = st.selectbox("6. Director proiect / Responsabil", ["---", "Popescu Ion", "Ionescu Maria"])
            # 7. An implementare (Logic: an_referinta sau intervale)
            an_introdus = st.number_input("7. Anul de implementare", min_value=2000, max_value=2030, value=2024)

        with f3:
            # 8. Rol (Sursa: rol_upt)
            rol = st.multiselect("8. Rolul UPT", ["Coordonator", "Partener"])
            # 9. Status (Sursa: status_contract_proiect)
            status = st.multiselect("9. Statusul proiectului", ["În derulare", "Finalizat"])

        # BUTON ACTIVARE INTEROGARE
        if st.button("Lansează Interogarea", use_container_width=True):
            st.success(f"Sistemul caută acum în tabelele base_proiecte_{tip_ales.lower()}...")
            # Aici intervine logica de filtrare bazată pe an (an_referinta sau interval date)

# ==========================================
# CALEA 2: ADMIN (IZOLATĂ)
# ==========================================
elif calea_activa == "admin":
    st.info("Secțiune protejată. Reveniți la Explorator pentru testarea filtrelor.")
