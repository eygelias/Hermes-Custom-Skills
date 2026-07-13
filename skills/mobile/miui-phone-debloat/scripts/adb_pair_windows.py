#!/usr/bin/env python3
"""
ADB Pairing Script for Windows
Usage: python adb_pair_windows.py <ip:port> <pairing_code>
Example: python adb_pair_windows.py 192.168.100.249:39623 203885

Problem: On Windows, piping input to `adb pair` doesn't work.
Solution: Use subprocess with Popen to send the pairing code interactively.
"""
import subprocess
import sys
import time

def adb_pair(address, code):
    """Pair with an Android device via wireless debugging."""
    proc = subprocess.Popen(
        ["adb", "pair", address],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for the prompt
    time.sleep(2)
    
    # Send the pairing code
    proc.stdin.write(f"{code}\n")
    proc.stdin.flush()
    proc.stdin.close()
    
    # Get the result
    try:
        out = proc.communicate(timeout=15)[0]
        print(out)
        return "Successfully paired" in out
    except subprocess.TimeoutExpired:
        proc.kill()
        print("TIMEOUT: Pairing took too long")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python adb_pair_windows.py <ip:port> <pairing_code>")
        print("Example: python adb_pair_windows.py 192.168.100.249:39623 203885")
        sys.exit(1)
    
    address = sys.argv[1]
    code = sys.argv[2]
    
    success = adb_pair(address, code)
    sys.exit(0 if success else 1)
