import streamlit as st
import pandas as pd

# Configurare pagină
st.set_page_config(page_title="Consola Responsabili IDBDC", layout="wide")

# 1. Titlul oficial al aplicației [cite: 335]
st.title("🛡️ Consola Responsabili IDBDC")

# --- BARIERA 1: PAROLA DE SITE (Interfața intermediară) ---
if "autentificat_site" not in st.session_state:
    st.session_state["autentificat_site"] = False

if not st.session_state["autentificat_site"]:
    st.subheader("Acces Restricționat")
    # Noua parolă stabilită: EverDream2SZ
    parola_introdusa = st.text_input("Introduceți parola de acces:", type="password")
    
    if st.button("Verifică Parola"):
        if parola_introdusa == "EverDream2SZ":
            st.session_state["autentificat_site"] = True
            st.success("Acces Autorizat")
            st.rerun()
        elif parola_introdusa != "":
            st.error("Parolă incorectă!")
    st.stop() # Oprește execuția până la introducerea parolei corecte

# --- BARIERA 2: MENIU SPECIALIST (Cei 9 Privilegiați)  ---
st.sidebar.title("Meniu Specialist")

# Câmpul de intrare conform Protocolului
cod_identificare = st.sidebar.text_input("Introduceți Cod Identificare Responsabil")

# Mesajul de stare dinamic sub casetă
if not cod_identificare:
    st.sidebar.write("Așteptare cod responsabil...")
    st.info("Vă rugăm să introduceți codul de identificare în meniul din stânga pentru a activa funcțiile CRUD.")
    st.stop()
else:
    # Aici verificăm dacă codul este în lista celor 9 (Exemplu: SZEKELY) [cite: 415, 335]
    lista_specialisti = ["SZEKELY", "ID_RESP_2", "ID_RESP_3"] # De completat cu lista reală
    
    if cod_identificare in lista_specialisti:
        st.sidebar.success(f"Autorizat: Responsabil {cod_identificare}")
    else:
        st.sidebar.error("Cod Neautorizat!")
        st.stop()

# --- FILTRARE ÎN CASCADĂ (Pasul 4 și 5) [cite: 579] ---
# 1. Selecție Categorie (nom_categorie)
categorie = st.selectbox("Selectați Categoria:", ["Contracte & Proiecte", "Proprietate Intelectuală", "Evenimente"])

if categorie == "Contracte & Proiecte":
    # 2. Selecție Tabel (Cele 8 baze cu cod_identificare unitar) [cite: 674, 336]
    tabel_selectat = st.selectbox("Selectați Baza de Date pentru Intervenție:", 
                                  ["base_proiecte_internationale", 
                                   "base_proiecte_fdi", 
                                   "base_proiecte_pnrr", 
                                   "base_proiecte_pncdi", 
                                   "base_contracte_terti", 
                                   "base_proiecte_interreg", 
                                   "base_proiecte_noneu", 
                                   "base_contracte_cep"])
    
    st.write(f"### Se încarcă datele pentru: {tabel_selectat}")
    # Aici urmează logica de afișare a tabelului și butoanele CRUD (Creion ✏️, Coș 🗑️) [cite: 538, 541]
