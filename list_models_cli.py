import google.generativeai as genai
import os
import re

api_key = ""
try:
    with open(".streamlit/secrets.toml", "r") as f:
        content = f.read()
        match = re.search(r'GEMINI_API_KEY\s*=\s*"([^"]+)"', content)
        if match:
            api_key = match.group(1)
except:
    pass

if not api_key:
    # No key found
    print("ERROR: Could not find GEMINI_API_KEY in secrets.toml")
else:
    genai.configure(api_key=api_key)
    print("AVAILABLE_MODELS_START")
    for m in genai.list_models():
        print(m.name)
    print("AVAILABLE_MODELS_END")
