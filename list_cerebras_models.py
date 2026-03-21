from cerebras.cloud.sdk import Cerebras
import streamlit as st
import re

st.title("Cerebras Model Discovery")

api_key = ""
try:
    with open(".streamlit/secrets.toml", "r") as f:
        content = f.read()
        match = re.search(r'CEREBRAS_API_KEY\s*=\s*"([^"]+)"', content)
        if match:
            api_key = match.group(1)
except:
    pass

if not api_key:
    st.error("CEREBRAS_API_KEY not found in secrets.toml")
else:
    try:
        client = Cerebras(api_key=api_key)
        models = client.models.list()
        st.write("### Available Models:")
        for m in models.data:
            st.write(f"- `{m.id}`")
    except Exception as e:
        st.error(f"Error: {e}")
