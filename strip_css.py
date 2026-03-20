import glob

files = glob.glob("pages/*.py") + ["app.py"]

bad_line_1 = '*:not(.material-symbols-rounded):not(.material-icons):not(.stIcon):not([class*="icon"]) { font-family: \'Tajawal\', sans-serif !important; }'
bad_line_2 = '*:not(.material-symbols-rounded):not(.material-icons):not(.stIcon):not([class*="icon"]) {\n        font-family: \'Tajawal\', sans-serif !important;\n    }'

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = content.replace(bad_line_1, '')
    new_content = new_content.replace(bad_line_2, '')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Stripped font override in {filepath}")
