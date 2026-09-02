#!/usr/bin/env python3

import argparse
import hashlib
from pathlib import Path


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def baseline_file(target):
    return target.with_name(f"{target.name}.sha256")


def create_baseline(target):
    checksum = sha256_file(target)
    baseline = baseline_file(target)
    baseline.write_text(checksum + "\n", encoding="utf-8")

    print(f"[+] Baseline created: {baseline}")
    print(f"[+] SHA-256: {checksum}")
    return 0


def check_integrity(target):
    baseline = baseline_file(target)

    if not baseline.is_file():
        print(f"[!] Missing baseline: {baseline}")
        return 2

    expected = baseline.read_text(encoding="utf-8").strip()
    actual = sha256_file(target)

    if expected == actual:
        print(f"[OK] Integrity verified: {target}")
        return 0

    print(f"[ALERT] File changed: {target}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Create and verify SHA-256 file-integrity baselines."
    )
    parser.add_argument("action", choices=("create", "check"))
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    target = args.file.expanduser()

    if not target.is_file():
        parser.error(f"file not found: {target}")

    if args.action == "create":
        raise SystemExit(create_baseline(target))

    raise SystemExit(check_integrity(target))


if __name__ == "__main__":
    main()
