"""Run one version of the SentinelOps module on the assessment test data.

Usage:  python src/demo.py original | corrected | optimised
Prints the expected and the actual output of every function.
"""
import importlib
import sys

name = sys.argv[1] if len(sys.argv) > 1 else "corrected"
mod = importlib.import_module(name)

alerts = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
blocklist = ["10.0.0.5", "10.0.0.9", "172.16.4.2"]
queries = ["10.0.0.9", "10.0.0.5", "8.8.8.8"]
log, pattern = "FAILFAIXFAIL", "FAIL"
events = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]

print(f"=== module under test: {name} ===")

print("\n[1] sort_alerts")
print("  input    :", alerts)
print("  expected :", [("A2", 9), ("A4", 9), ("A3", 5), ("A1", 3), ("A5", 1)])
print("  actual   :", mod.sort_alerts(list(alerts)))

print("\n[2] is_blocked")
bl = mod.build_blocklist(blocklist) if hasattr(mod, "build_blocklist") else blocklist
print("  expected :", [True, True, False])
print("  actual   :", [mod.is_blocked(bl, q) for q in queries])

print("\n[3] find_signature")
print(f"  log={log!r} pattern={pattern!r}")
print("  expected :", [0, 8])
print("  actual   :", mod.find_signature(log, pattern))

print("\n[4] closest_logins")
print("  expected :", ((0, 5), 1.4142135623730951))
print("  actual   :", mod.closest_logins(events))
