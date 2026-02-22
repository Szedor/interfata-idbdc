import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

def import_data_module():
    st.header("🔄 Import Date în Neon (IDBDC)")
    st.info("Acest modul încarcă datele din laptopul tău direct în tabelul 'base_proiecte_internationale'.")

    # 1. Configurarea conexiunii (Asigură-te că ai DB_URL în .streamlit/secrets.toml)
    try:
        # Exemplu format: postgresql://user:password@host/neondb
        engine = create_engine(st.secrets["DB_URL"])
    except Exception as e:
        st.error(f"Eroare la configurarea conexiunii: {e}")
        return

    # 2. Selector de fișier (suportă CSV și Excel din laptop)
    uploaded_file = st.file_uploader(
        "Alege fișierul (CSV sau Excel) de pe laptop", 
        type=["csv", "xlsx"]
    )

    if uploaded_file is not None:
        try:
            # Detectăm tipul fișierului și îl citim
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Previzualizare pentru confirmare
            st.subheader("Previzualizare date")
            st.write(f"Am găsit {len(df)} rânduri în fișier.")
            st.dataframe(df.head(10)) 

            # 3. Butonul de execuție
            if st.button("🚀 Lansează Importul în Neon"):
                with st.spinner("Se procesează importul..."):
                    # Pasul A: Golește tabelul existent (Truncate) conform acordului nostru
                    with engine.begin() as conn:
                        conn.execute(text("TRUNCATE TABLE public.base_proiecte_internationale RESTART IDENTITY;"))
                    
                    # Pasul B: Curățare minimă (înlocuire NaN cu None pentru baze de date)
                    df = df.where(pd.notnull(df), None)

                    # Pasul C: Importul propriu-zis
                    # Utilizăm method='multi' pentru viteză la peste 1000 de rânduri
                    df.to_sql(
                        'base_proiecte_internationale', 
                        engine, 
                        schema='public', 
                        if_exists='append', 
                        index=False,
                        chunksize=500
                    )
                
                st.success(f"✅ Succes! {len(df)} rânduri au fost mutate în Neon.")
                st.balloons()

        except Exception as e:
            st.error(f"❌ A apărut o eroare la procesare: {e}")

# Apelarea funcției în aplicație
if __name__ == "__main__":
    import_data_module()
