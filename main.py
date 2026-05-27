#!/usr/bin/env python3
"""DeepSeek TUI - 终端 AI 编程助手"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.app import main

if __name__ == "__main__":
    main()
