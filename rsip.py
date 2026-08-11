#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

from core.config import load_config, save_interval
from core.ip_checker import get_tor_ip
from core.tor_manager import TorManager

APP_NAME = "RsiP"
VERSION = "1.0"
BRAND = "RsServ"
TELEGRAM = "@RsServ"
GITHUB = "https://github.com/RsServ"

BASE_DIR = Path(__file__).resolve().parent
PID_FILE = Path("/tmp/rsip.pid")


def banner() -> None:
    import shutil
    import subprocess

    print()
    if shutil.which("figlet"):
        try:
            result = subprocess.run(
                ["figlet", "-f", "Bloody", "RsServ"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                print(result.stdout.rstrip())
            else:
                _fallback_banner()
        except Exception:
            _fallback_banner()
    else:
        _fallback_banner()

    print("  RsiP v1.0  |  IP TOOL")
    print(f"  Telegram : {TELEGRAM}")
    print(f"  GitHub   : {GITHUB}")
    print()


def _fallback_banner() -> None:
    print(r"""
  ____       ____                  _
 |  _ \ ___ / ___|  ___ _ ____   _(_) ___ ___
 | |_) / __| |  _  / _ \ '__\ \ / / |/ __/ __|
 |  _ <\__ \ |_| ||  __/ |   \ V /| | (__\__ \
 |_| \_\___/\____(_)___|_|    \_/ |_|\___|___/
""")


def require_root_for_service() -> None:
    if os.geteuid() != 0:
        print("[!] This command needs root privileges.")
        print("    Try: sudo rsip ...")
        raise SystemExit(1)


def cmd_status() -> int:
    banner()
    manager = TorManager()
    try:
        manager.connect()
        ip = get_tor_ip()
        print("[+] Tor Control : connected")
        print(f"[+] Exit IP     : {ip}")
        print(f"[+] SOCKS       : {manager.socks_host}:{manager.socks_port}")
        return 0
    except Exception as exc:
        print(f"[!] Status error: {exc}")
        return 1
    finally:
        manager.close()


def cmd_rotate() -> int:
    banner()
    manager = TorManager()
    try:
        manager.connect()
        before = get_tor_ip()
        print(f"[+] Current IP  : {before}")
        print("[*] Requesting new Tor identity...")
        manager.new_identity()

        deadline = time.time() + 30
        after = before
        while time.time() < deadline:
            time.sleep(2)
            try:
                after = get_tor_ip()
            except Exception:
                continue
            if after != before:
                break

        print(f"[+] New IP      : {after}")
        if after == before:
            print("[!] Tor accepted NEWNYM, but the exit IP did not change in the timeout.")
            return 2
        print("[+] Rotation successful.")
        return 0
    except Exception as exc:
        print(f"[!] Rotation error: {exc}")
        return 1
    finally:
        manager.close()


def daemon_loop(interval: int) -> int:
    if interval < 1:
        raise ValueError("interval must be >= 1 second")

    manager = TorManager()
    manager.connect()

    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    print(f"[+] RsiP daemon started | interval={interval}s")

    try:
        while True:
            try:
                before = get_tor_ip()
            except Exception as exc:
                print(f"[!] IP check failed: {exc}")
                before = "unknown"

            try:
                manager.new_identity()
                print(f"[*] Rotation requested | old={before}")
            except Exception as exc:
                print(f"[!] Rotation failed: {exc}")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n[*] Stopping RsiP daemon.")
        return 0
    finally:
        try:
            PID_FILE.unlink(missing_ok=True)
        except Exception:
            pass
        manager.close()


def cmd_start(interval: int) -> int:
    save_interval(interval)
    print(f"[+] Saved interval: {interval}s")
    print("[*] Starting RsiP in foreground. Press Ctrl+C to stop.")
    return daemon_loop(interval)


def cmd_stop() -> int:
    if not PID_FILE.exists():
        print("[!] RsiP is not running.")
        return 1

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
        os.kill(pid, 15)
        print(f"[+] Stop signal sent to PID {pid}.")
        return 0
    except ProcessLookupError:
        PID_FILE.unlink(missing_ok=True)
        print("[!] RsiP was not running.")
        return 1
    except PermissionError:
        print("[!] Permission denied. Try: sudo rsip stop")
        return 1
    except Exception as exc:
        print(f"[!] Stop error: {exc}")
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rsip",
        description="RsiP - RsServ IP Rotation Utility",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show Tor and current exit IP")
    sub.add_parser("rotate", help="request a new Tor identity")

    start = sub.add_parser("start", help="start automatic rotation")
    start.add_argument(
        "--interval",
        "-i",
        type=int,
        default=None,
        help="rotation interval in seconds",
    )

    sub.add_parser("stop", help="stop a running foreground daemon")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "status":
        return cmd_status()
    if args.command == "rotate":
        return cmd_rotate()
    if args.command == "start":
        cfg = load_config()
        interval = args.interval if args.interval is not None else cfg["interval"]
        return cmd_start(interval)
    if args.command == "stop":
        return cmd_stop()

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
