import streamlit as st
from config import Config

def check_maintenance():
if "authorized" not in st.session_state:
st.session_state.authorized = False

```
if not st.session_state.authorized:
    parola = st.text_input("Parola acces:", type="password")

    if parola:
        if parola == Config.MAINTENANCE_PASSWORD:
            st.session_state.authorized = True
            st.rerun()
        else:
            st.error("Parolă incorectă")
            st.stop()
    else:
        st.stop()
```
