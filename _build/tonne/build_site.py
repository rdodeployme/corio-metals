#!/usr/bin/env python3
"""Recycled Metals as a standalone site: same pages, no version bar. Output: recycled-metals-site/."""
import os, runpy
os.environ["RM_STANDALONE"] = "1"
runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "build.py"), run_name="__main__")
