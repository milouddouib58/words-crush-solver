import google.generativeai as genai
import streamlit as st

api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

st.title("Gemini Model Discovery")

try:
    models = genai.list_models()
    st.write("### Available Models:")
    for m in models:
        st.write(f"- `{m.name}` | {m.display_name} | {m.supported_generation_methods}")
except Exception as e:
    st.error(f"Error listing models: {e}")
