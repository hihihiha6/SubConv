#!/usr/bin/env python3
# coding=utf-8

from subconv.app import app
from subconv.cli import main

if __name__ == "__main__":
    import os
    from pathlib import Path

    os.chdir(Path(__file__).resolve().parent)

    main()
