# File Integrity Monitor

A defensive Python command-line tool that uses SHA-256 hashes to detect file changes.

## Features

- Creates a SHA-256 baseline for a file
- Detects modified file contents
- Displays expected and actual hashes
- Returns automation-friendly exit codes
- Uses only the Python standard library

## Requirements

- Python 3.10 or newer
- Linux, macOS, or Windows

## Usage

Create a baseline:

    python3 fim.py create example.txt

Verify file integrity:

    python3 fim.py check example.txt

## Exit Codes

- `0` – Integrity verified
- `1` – File contents changed
- `2` – Baseline missing

## Security Purpose

This project demonstrates defensive file-integrity monitoring. It should only be used on files and systems you own or are authorized to monitor.
