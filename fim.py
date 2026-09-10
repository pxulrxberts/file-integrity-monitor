#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
from pathlib import Path

BASELINE_NAME = ".fim-baseline.json"
IGNORED_DIRS = {".git", "__pycache__"}


def sha256_file(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def scan_directory(root):
    results = {}

    for current, directories, filenames in os.walk(root):
        directories[:] = [
            name for name in directories if name not in IGNORED_DIRS
        ]

        for filename in filenames:
            if filename == BASELINE_NAME:
                continue

            path = Path(current) / filename

            if path.is_symlink():
                continue

            relative_path = path.relative_to(root).as_posix()
            results[relative_path] = sha256_file(path)

    return dict(sorted(results.items()))


def create_directory_baseline(root):
    files = scan_directory(root)
    baseline = root / BASELINE_NAME

    data = {
        "algorithm": "sha256",
        "files": files,
    }

    baseline.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"[+] Directory baseline created: {baseline}")
    print(f"[+] Files recorded: {len(files)}")
    return 0


def check_directory(root):
    baseline = root / BASELINE_NAME

    if not baseline.is_file():
        print(f"[!] Missing baseline: {baseline}")
        return 2

    try:
        data = json.loads(baseline.read_text(encoding="utf-8"))
        expected = data["files"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        print(f"[!] Invalid baseline: {baseline}")
        return 2

    actual = scan_directory(root)

    expected_names = set(expected)
    actual_names = set(actual)

    added = sorted(actual_names - expected_names)
    deleted = sorted(expected_names - actual_names)
    modified = sorted(
        name
        for name in expected_names & actual_names
        if expected[name] != actual[name]
    )

    for name in added:
        print(f"[ADDED] {name}")

    for name in modified:
        print(f"[MODIFIED] {name}")

    for name in deleted:
        print(f"[DELETED] {name}")

    if added or modified or deleted:
        print(
            f"[ALERT] {len(added)} added, "
            f"{len(modified)} modified, {len(deleted)} deleted"
        )
        return 1

    print(f"[OK] Directory integrity verified: {root}")
    print(f"[OK] Files checked: {len(actual)}")
    return 0


def file_baseline_path(target):
    return target.with_name(f"{target.name}.sha256")


def create_file_baseline(target):
    baseline = file_baseline_path(target)
    checksum = sha256_file(target)
    baseline.write_text(checksum + "\n", encoding="utf-8")

    print(f"[+] File baseline created: {baseline}")
    return 0


def check_file(target):
    baseline = file_baseline_path(target)

    if not baseline.is_file():
        print(f"[!] Missing baseline: {baseline}")
        return 2

    expected = baseline.read_text(encoding="utf-8").strip()
    actual = sha256_file(target)

    if expected == actual:
        print(f"[OK] File integrity verified: {target}")
        return 0

    print(f"[MODIFIED] {target}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    return 1


def main():
    parser = argparse.ArgumentParser(
        description="Create and verify SHA-256 baselines for files or directories."
    )
    parser.add_argument("action", choices=("create", "check"))
    parser.add_argument("path", type=Path)
    args = parser.parse_args()

    target = args.path.expanduser()

    if not target.exists():
        parser.error(f"path not found: {target}")

    if target.is_dir():
        result = (
            create_directory_baseline(target)
            if args.action == "create"
            else check_directory(target)
        )
    else:
        result = (
            create_file_baseline(target)
            if args.action == "create"
            else check_file(target)
        )

    raise SystemExit(result)


if __name__ == "__main__":
    main()
