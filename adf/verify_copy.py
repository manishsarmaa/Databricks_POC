#!/usr/bin/env python3
"""Verify the ADF copy worked: every file in source/input must exist in
sink/output with a matching byte size. Prints PASS/FAIL, exits non-zero on FAIL.

Uses the Azure CLI (az) for the data-plane listing so no SDK/credentials setup
is needed beyond an existing `az login`. The storage key is read transiently and
never written to disk.
"""
import json
import os
import shutil
import subprocess
import sys

# Prefer az on PATH (Linux CI agents); fall back to the Windows install location.
_WIN_AZ = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
AZ = shutil.which("az") or (_WIN_AZ if os.path.exists(_WIN_AZ) else "az")
# Resource names default to the POC values but can be overridden via env (CI).
ACCOUNT = os.environ.get("STORAGE_ACCOUNT", "stadfpoc78cqho")
RG = os.environ.get("RG", "rg-adf-poc")
SOURCE_FS, SOURCE_PATH = "source", "input"
SINK_FS, SINK_PATH = "sink", "output"


def az(args):
    out = subprocess.run([AZ, *args], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"az command failed: {' '.join(args)}\n{out.stderr}")
    return out.stdout


def get_key():
    return az(["storage", "account", "keys", "list", "--account-name", ACCOUNT,
               "--resource-group", RG, "--query", "[0].value", "-o", "tsv"]).strip()


def list_files(key, fs, path):
    """Return {basename: contentLength} for files directly under path."""
    raw = az(["storage", "fs", "file", "list", "--account-name", ACCOUNT,
              "--account-key", key, "--file-system", fs, "--path", path,
              "--query", "[].{name:name, bytes:contentLength}", "-o", "json",
              "--only-show-errors"])
    result = {}
    for item in json.loads(raw):
        base = item["name"].split("/")[-1]
        result[base] = int(item["bytes"])
    return result


def main():
    key = get_key()
    src = list_files(key, SOURCE_FS, SOURCE_PATH)
    snk = list_files(key, SINK_FS, SINK_PATH)

    print(f"source/{SOURCE_PATH}: {len(src)} file(s)")
    print(f"sink/{SINK_PATH}:   {len(snk)} file(s)")

    failures = []
    for name, size in sorted(src.items()):
        if name not in snk:
            failures.append(f"{name}: MISSING in sink")
        elif snk[name] != size:
            failures.append(f"{name}: size mismatch source={size} sink={snk[name]}")
        else:
            print(f"  OK  {name}  ({size} bytes)")

    if not src:
        failures.append("no source files found to verify")

    if failures:
        print("\nFAIL")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print(f"\nPASS — all {len(src)} source file(s) present in sink with matching sizes")
    sys.exit(0)


if __name__ == "__main__":
    main()
