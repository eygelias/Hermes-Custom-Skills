#!/usr/bin/env python3
"""ADB wireless pairing helper for Windows where piped input doesn't work."""
import subprocess, time, sys

def adb_pair(ip_port: str, code: str, adb_path: str = "adb") -> bool:
    """Pair with an Android device via wireless ADB.
    
    Args:
        ip_port: IP:Port from the pairing dialog (e.g. "192.168.100.249:39623")
        code: 6-digit pairing code
        adb_path: path to adb executable
    
    Returns:
        True if pairing succeeded
    """
    proc = subprocess.Popen(
        [adb_path, "pair", ip_port],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    time.sleep(2)
    proc.stdin.write(f"{code}\n")
    proc.stdin.flush()
    proc.stdin.close()
    
    try:
        out = proc.communicate(timeout=15)[0]
        print(out)
        return "Successfully paired" in out
    except subprocess.TimeoutExpired:
        proc.kill()
        print("TIMEOUT — pairing code may have expired")
        return False

def adb_connect(ip_port: str, adb_path: str = "adb") -> bool:
    """Connect to a paired device via wireless ADB."""
    r = subprocess.run(
        [adb_path, "connect", ip_port],
        capture_output=True, text=True, timeout=15
    )
    print(r.stdout.strip())
    return "connected" in r.stdout

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: adb_wireless.py <IP:PORT> <CODE>")
        print("  IP:PORT from pairing dialog")
        print("  CODE = 6-digit pairing code")
        sys.exit(1)
    
    ip_port = sys.argv[1]
    code = sys.argv[2]
    
    if adb_pair(ip_port, code):
        print("✅ Pairing successful!")
        # Now connect to main port
        main_ip = ip_port.split(":")[0]
        print(f"Now connect with: adb connect {main_ip}:<MAIN_PORT>")
    else:
        print("❌ Pairing failed")
