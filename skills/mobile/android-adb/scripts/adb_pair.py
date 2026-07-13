"""
ADB Wireless Pairing Script for Windows.

Usage: python adb_pair.py <ip:port> <pairing_code>
Example: python adb_pair.py 192.168.100.249:41781 917628

Why this exists: adb pair is interactive and can't accept piped input on Windows.
Piping (echo code | adb pair) produces "protocol fault" errors.
PTY mode in terminal tools also doesn't work reliably.

Requirements: ADB platform-tools installed (adb.exe must exist).
"""
import subprocess
import sys
import time
import os

ADB_PATH = os.path.expanduser(r"~\platform-tools\adb.exe")
if not os.path.exists(ADB_PATH):
    # Try system PATH
    ADB_PATH = "adb"

def pair(ip_port: str, code: str, timeout: int = 15) -> str:
    """Pair with an Android device via wireless debugging."""
    proc = subprocess.Popen(
        [ADB_PATH, "pair", ip_port],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    time.sleep(2)  # Wait for "Enter pairing code:" prompt
    
    proc.stdin.write(f"{code}\n")
    proc.stdin.flush()
    proc.stdin.close()
    
    try:
        out = proc.communicate(timeout=timeout)[0]
        return out.strip()
    except subprocess.TimeoutExpired:
        proc.kill()
        return "TIMEOUT: pairing took too long"

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <ip:port> <pairing_code>")
        print(f"Example: {sys.argv[0]} 192.168.100.249:41781 917628")
        sys.exit(1)
    
    result = pair(sys.argv[1], sys.argv[2])
    print(result)
    sys.exit(0 if "Successfully paired" in result else 1)
