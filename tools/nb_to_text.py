"""Print a notebook's cells and their plain-text outputs, for reading in a terminal or text file.

Used by run.sh after it executes a notebook. Tables appear as aligned text (pandas' plain-text
form) instead of HTML.

Usage: python tools/nb_to_text.py <executed_notebook.ipynb>
"""

import json
import re
import sys

ANSI_CODES = re.compile(r"\x1b\[[0-9;]*m")  # colour codes that Jupyter adds to error tracebacks


def text_of(output):
    """Return the plain-text form of one cell output."""
    kind = output["output_type"]
    if kind == "stream":  # print() output
        return "".join(output["text"])
    if kind in ("execute_result", "display_data"):  # a cell's last value, e.g. a DataFrame
        return "".join(output.get("data", {}).get("text/plain", ""))
    if kind == "error":
        return ANSI_CODES.sub("", "\n".join(output["traceback"]))
    return ""


def main(path):
    with open(path, encoding="utf-8") as f:
        notebook = json.load(f)
    for cell in notebook["cells"]:
        source = "".join(cell["source"]).rstrip()
        if cell["cell_type"] == "markdown":
            print(f"{source}\n")
        elif cell["cell_type"] == "code":
            print(f"[code]\n{source}")
            outputs = [text_of(o).rstrip() for o in cell.get("outputs", [])]
            outputs = [o for o in outputs if o]
            if outputs:
                print("[output]\n" + "\n".join(outputs))
            print()


if __name__ == "__main__":
    main(sys.argv[1])
