import streamlit as st

def run():
    # Stilizare vizuală pentru poarta Brainstorming
    st.markdown("""
        <style>
            .brainstorm-header {
                background-color: #2E7D32;
                padding: 20px;
                border-radius: 10px;
                color: white;
                text-align: center;
                margin-bottom: 25px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="brainstorm-header"><h1>🧠 Brainstorming AI - IDBDC</h1><p>Consultantul tău inteligent pentru cercetare</p></div>', unsafe_allow_html=True)

    # Verificare acces (folosim aceeași logică de securitate ca la Explorator)
    if "auth_brainstorm" not in st.session_state:
        st.session_state.auth_brainstorm = False

    if not st.session_state.auth_brainstorm:
        _, col_ce, _ = st.columns([1, 1, 1])
        with col_ce:
            st.subheader("🛡️ Acces Securizat")
            p = st.text_input("Introdu parola de acces:", type="password", key="pass_brain")
            if st.button("Deblochează Poarta"):
                if p == "EverDream2SZ":
                    st.session_state.auth_brainstorm = True
                    st.rerun()
                else:
                    st.error("Parolă incorectă.")
        st.stop()

    # Conținutul interfeței de Brainstorming (Interfață preliminară)
    st.info("Această secțiune va servi drept spațiu de dialog AI pentru analiza bazelor de date de cercetare.")
    
    chat_input = st.chat_input("Cu ce te pot ajuta astăzi în legătură cu proiectele IDBDC?")
    
    if chat_input:
        with st.chat_message("user"):
            st.write(chat_input)
        
        with st.chat_message("assistant"):
            st.write(f"Am recepționat mesajul tău: '{chat_input}'. Momentan suntem în faza de configurare a motorului de analiză.")

if __name__ == "__main__":
    run()
