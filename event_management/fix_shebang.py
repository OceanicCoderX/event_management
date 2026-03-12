import os
import sys

cgi_dir = "cgi-bin"
python_ex = sys.executable

for filename in os.listdir(cgi_dir):
    if filename.endswith(".py"):
        filepath = os.path.join(cgi_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if len(lines) > 0 and lines[0].startswith("#!"):
            lines[0] = f"#!{python_ex}\n"
            with open(filepath, "w", encoding="utf-8", newline='\n') as f:
                f.writelines(lines)
print("Shebangs updated.")
