import streamlit as st
import os

st.title("Secret verification")

st.write("Current Dir:", os.getcwd())

if ".streamlit" in os.listdir("."):
    st.success("found .streamlit folder")
    if "secrets.toml" in os.listdir(".streamlit"):
        st.success("found secrets.toml file")
else:
    st.error("cannot find .streamlit folder")

try:
    if "GEMINI_API_KEY" in st.secrets:
        st.success(f"GEMINI key detected! (starts with {st.secrets['GEMINI_API_KEY'][:5]}...)")
    else:
        st.error("GEMINI key NOT in st.secrets")

    if "MISTRAL_API_KEY" in st.secrets:
        st.success(f"MISTRAL key detected! (starts with {st.secrets['MISTRAL_API_KEY'][:5]}...)")
    else:
        st.error("MISTRAL key NOT in st.secrets")
        
    import mistralai
    st.success("Mistral library IS installed")
except Exception as e:
    st.error(f"Error checking AI status: {e}")
