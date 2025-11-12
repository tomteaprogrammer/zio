#!/usr/bin/env python3
# long_paths_toggle.py
# Toggle Windows long path support by setting:
# HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled

import sys
import ctypes
import winreg

REG_PATH = r"SYSTEM\CurrentControlSet\Control\FileSystem"
VALUE_NAME = "LongPathsEnabled"

def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False

def elevate_and_rerun():
    # Relaunch this script with admin rights
    params = " ".join(f'"{a}"' for a in sys.argv[1:])
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, f'"{sys.argv[0]}" {params}', None, 1
    )
    sys.exit(0)

def _open_for_write(reg):
    # Try 64-bit view first (for 32-bit Python on 64-bit Windows), then fallback
    try:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
    except Exception:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_SET_VALUE)

def _open_for_query(reg):
    try:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_WOW64_64KEY)
    except Exception:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_QUERY_VALUE)

def set_long_paths(enabled: bool):
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        key = _open_for_write(reg)
    except FileNotFoundError:
        key = winreg.CreateKeyEx(reg, REG_PATH, 0, access=winreg.KEY_SET_VALUE)
    with key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_DWORD, 1 if enabled else 0)

def get_status() -> int:
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        with _open_for_query(reg) as key:
            val, _ = winreg.QueryValueEx(key, VALUE_NAME)
            return int(val)
    except FileNotFoundError:
        return 0

def usage():
    print("Usage: python long_paths_toggle.py [--enable | --disable | --status]")
    print("  --enable   Set LongPathsEnabled = 1")
    print("  --disable  Set LongPathsEnabled = 0")
    print("  --status   Show current value")

def main():
    if len(sys.argv) == 1 or sys.argv[1] in ("-h", "--help"):
        usage()
        return

    if not is_admin():
        elevate_and_rerun()

    cmd = sys.argv[1].lower()
    if cmd == "--enable":
        set_long_paths(True)
        print(rf"OK: HKLM\{REG_PATH}\{VALUE_NAME} set to 1 (enabled).")
    elif cmd == "--disable":
        set_long_paths(False)
        print(rf"OK: HKLM\{REG_PATH}\{VALUE_NAME} set to 0 (disabled).")
    elif cmd == "--status":
        v = get_status()
        print("ENABLED" if v == 1 else "DISABLED (or not set)")
    else:
        usage()

if __name__ == "__main__":
    main()
