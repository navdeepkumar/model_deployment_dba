"""
Executes Full_Code_SuperKart_Model_Deployment_Notebook.ipynb end-to-end using the
project's isolated virtual environment kernel, EXCEPT for the cells that call the
live (placeholder) Codespace-forwarded backend URL, which are intentionally left
un-executed (they are already validated locally in the "Local Smoke Test" section).

Run with:  .venv\\Scripts\\python.exe execute_notebook.py
"""
import sys
import time

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

NOTEBOOK_PATH = "Full_Code_SuperKart_Model_Deployment_Notebook.ipynb"
SKIP_MARKER = "# This cell calls the live Codespace backend URL and is skipped"

nb = nbformat.read(NOTEBOOK_PATH, as_version=4)

client = NotebookClient(
    nb,
    timeout=1800,
    kernel_name="superkart-venv",
    resources={"metadata": {"path": "."}},
    allow_errors=False,
)

start = time.time()
executed, skipped = 0, 0

with client.setup_kernel():
    for index, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        if SKIP_MARKER in cell.source:
            skipped += 1
            print(f"[{index:3d}] SKIPPED (live-URL cell): {cell.source.splitlines()[-1][:80]}")
            continue
        preview = cell.source.strip().splitlines()[0][:80] if cell.source.strip() else "(empty)"
        print(f"[{index:3d}] Executing: {preview}")
        try:
            client.execute_cell(cell, index)
        except CellExecutionError as exc:
            print(f"\n!!! ERROR in cell {index} !!!")
            print(cell.source)
            print(str(exc))
            nbformat.write(nb, NOTEBOOK_PATH)
            sys.exit(1)
        executed += 1

nbformat.write(nb, NOTEBOOK_PATH)
elapsed = time.time() - start
print(f"\nDone. Executed {executed} code cells, skipped {skipped} live-URL cells, in {elapsed:.1f}s.")
