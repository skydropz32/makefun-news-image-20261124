#!/usr/bin/env python3
"""news-image-20261124 entry (Python 3.13, standard library only).

The front-page image is the entry.png beside this file, drawn by render.py
on the build machine; this program copies it to /output/entry.png. The copy
pattern is the kit starter's: the grader's container is python:3.13-slim
with no Pillow installed, so the program itself uses only the standard
library and the image ships pre-rendered in the repository.

Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

shutil.copyfile(HERE / "entry.png", OUT_DIR / "entry.png")
