import glob, re

replacement = '*:not(.material-symbols-rounded):not(.material-icons):not(.stIcon):not([class*="icon"]) { font-family: \'Tajawal\', sans-serif !important; }'

for filepath in glob.glob("pages/*.py") + ["app.py"]:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = re.sub(r'\*\s*\{\s*font-family:\s*\'Tajawal\',\s*sans-serif\s*!important;\s*\}', replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
