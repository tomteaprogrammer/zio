#!/usr/bin/env python3
# copypaste.py — Manage Windows "Enable Win32 long paths" setting via menu.
# Registry key: HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\LongPathsEnabled
# Requirements: Python 3 on Windows. Uses only standard library.

import sys
import os
import ctypes
import platform
import winreg

REG_PATH = r"SYSTEM\CurrentControlSet\Control\FileSystem"
VALUE_NAME = "LongPathsEnabled"

# ----- Admin helpers -----
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

# ----- Registry helpers -----
def _open_for_write(reg):
    try:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_SET_VALUE | winreg.KEY_WOW64_64KEY)
    except Exception:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_SET_VALUE)

def _open_for_query(reg):
    try:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_QUERY_VALUE | winreg.KEY_WOW64_64KEY)
    except Exception:
        return winreg.OpenKey(reg, REG_PATH, 0, winreg.KEY_QUERY_VALUE)

def get_status() -> int:
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        with _open_for_query(reg) as key:
            val, _ = winreg.QueryValueEx(key, VALUE_NAME)
            return int(val)
    except FileNotFoundError:
        return 0
    except OSError:
        return 0

def set_long_paths(enabled: bool) -> None:
    reg = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    try:
        key = _open_for_write(reg)
    except FileNotFoundError:
        key = winreg.CreateKeyEx(reg, REG_PATH, 0, access=winreg.KEY_SET_VALUE)
    with key:
        winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_DWORD, 1 if enabled else 0)

# ----- UI -----
def clear():
    os.system("cls")

def status_text(v: int) -> str:
    return "ENABLED (1)" if v == 1 else "DISABLED or not set (0)"

def menu():
    while True:
        clear()
        print("Windows Long Paths Manager")
        print("--------------------------")
        print(f"Current status: {status_text(get_status())}")
        print()
        print("1) Enable long paths")
        print("2) Disable long paths")
        print("3) Show status")
        print("4) Exit")
        choice = input("\nSelect an option [1-4]: ").strip()

        if choice == "1":
            try:
                set_long_paths(True)
                print("\nSet LongPathsEnabled = 1 (enabled).")
            except PermissionError:
                print("\nAdmin required. Relaunching as administrator...")
                elevate_and_rerun()
            except OSError as e:
                print(f"\nFailed: {e}")
            input("\nPress Enter to continue...")

        elif choice == "2":
            try:
                set_long_paths(False)
                print("\nSet LongPathsEnabled = 0 (disabled).")
            except PermissionError:
                print("\nAdmin required. Relaunching as administrator...")
                elevate_and_rerun()
            except OSError as e:
                print(f"\nFailed: {e}")
            input("\nPress Enter to continue...")

        elif choice == "3":
            print(f"\nStatus: {status_text(get_status())}")
            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\nExiting.")
            return
        else:
            print("\nInvalid selection.")
            input("\nPress Enter to continue...")

def main():
    if platform.system() != "Windows":
        print("This script is for Windows.")
        sys.exit(1)

    # Elevate once at start so all actions work in one window.
    if not is_admin():
        elevate_and_rerun()

    menu()

if __name__ == "__main__":
    main()
