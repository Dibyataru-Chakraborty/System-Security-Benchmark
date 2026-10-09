"""
Risk Nexus - Enterprise CIS Security Benchmark Hardening & Compliance Suite
Created By Dibyataru Chakraborty
"""
import os
import sys
import ctypes
from src.server import start_server

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def main():
    if sys.platform == "win32" and not is_admin():
        print("[!] Notice: Running without Administrator privileges.")
        print("    Registry scanning works for read-accessible hives.")
        print("    For full remediation & write permissions, run as Administrator.")
    
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    start_server(port=port, host=host, debug=False, open_browser=True)

if __name__ == "__main__":
    main()
