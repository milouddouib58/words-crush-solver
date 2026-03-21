from mistralai import Mistral
import streamlit as st
import os

st.title("Mistral Model Discovery")

try:
    api_key = st.secrets["MISTRAL_API_KEY"]
    client = Mistral(api_key=api_key)
    
    models = client.models.list()
    st.write("### Available Mistral Models:")
    for m in models.data:
        st.write(f"- `{m.id}`")
except Exception as e:
    st.error(f"Error listing models: {e}")
