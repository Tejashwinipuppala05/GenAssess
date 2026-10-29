p='src/rounds/routes.py'
s=open(p).read()
if "import os" not in s:
    s=s.replace("from __future__ import annotations","from __future__ import annotations\n\nimport os",1)
if "import json" not in s:
    s=s.replace("import os","import os\nimport json",1)
s=s.replace("_TECHNICAL_OPTION_ANSWERS: dict[str, int] = {}","_TECHNICAL_OPTION_ANSWERS: dict[str, int] = {}\n_TECHNICAL_OPTIONS_CACHE: dict[str, list[str]] = {}")
open(p,'w').write(s)
print('done')