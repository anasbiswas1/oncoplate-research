"""Validate notebook JSON and compile each pure-Python code cell without executing GPUs/downloads."""
import ast,json
from pathlib import Path
import nbformat
repo=Path(__file__).resolve().parents[1];count=0;cells=0
for path in sorted((repo/"notebooks").glob("*.ipynb")):
    nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
    for i,c in enumerate(nb.cells):
        if c.cell_type=="code":ast.parse(c.source,filename=f"{path.name}:cell{i}");cells+=1
    count+=1
print(json.dumps({"notebooks":count,"compiled_code_cells":cells,"status":"passed"}))
