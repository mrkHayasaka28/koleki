"""
Shared display utilities for all workers.
Compact 2-column layout support.
"""

import os
import sys
import time

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    BRIGHT_GREEN = "\033[38;5;46m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    GRAY = "\033[90m"
    PHOSPHOR = "\033[38;5;154m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Compact worker display — no big boxes
def worker_header_compact(name, icon):
    print(f"\n{C.CYAN}┌─ {icon} {name}{C.RESET}")

def worker_footer_compact():
    pass  # No footer in compact mode

def worker_log_compact(msg, status="ok"):
    colors = {
        "ok": C.GREEN,
        "warn": C.YELLOW,
        "err": C.RED,
        "info": C.DIM,
    }
    c = colors.get(status, C.RESET)
    print(f"{c}│ {msg}{C.RESET}")

def worker_header(name, icon):
    print(f"\n{C.CYAN}╔══ {icon} {name} {'═' * 35}╗{C.RESET}")

def worker_footer():
    print(f"{C.CYAN}╚{'═' * 50}╝{C.RESET}")

def worker_log(msg, status="ok"):
    colors = {
        "ok": C.GREEN,
        "warn": C.YELLOW,
        "err": C.RED,
        "info": C.DIM,
    }
    c = colors.get(status, C.RESET)
    print(f"{c}  [{status.upper()}]{C.RESET} {msg}")

def divider(char="─", width=60):
    print(f"{C.DIM}{char * width}{C.RESET}")

# 2-column layout helper
class ColumnBuffer:
    """Buffer output for side-by-side display"""
    def __init__(self):
        self.lines = []
    
    def add(self, text):
        self.lines.append(text)
    
    def render(self, other_buffer, spacing=4):
        """Print two buffers side by side"""
        max_lines = max(len(self.lines), len(other_buffer.lines))
        for i in range(max_lines):
            left = self.lines[i] if i < len(self.lines) else ""
            right = other_buffer.lines[i] if i < len(other_buffer.lines) else ""
            # Pad left to 50 chars
            print(f"{left:<50}{' ' * spacing}{right}")