import sys
import streamlit as st

st.title("Python Environment Check")

st.write("Python Executable:", sys.executable)
st.write("Python Version:", sys.version)

try:
    import mistralai
    st.write("Mistralai file:", getattr(mistralai, '__file__', 'No file'))
    st.write("Mistralai version:", getattr(mistralai, '__version__', 'No version'))
    from mistralai import Mistral
    st.success("SUCCESS: 'from mistralai import Mistral' worked!")
except ImportError as e:
    st.error(f"ImportError: {e}")
except Exception as e:
    st.error(f"Error: {e}")
