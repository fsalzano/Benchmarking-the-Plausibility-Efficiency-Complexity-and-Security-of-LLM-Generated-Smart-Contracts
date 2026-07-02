#!/usr/bin/env python3

import csv
from pathlib import Path


SMARTCHECK_DOS_FINDINGS = {
    "solidity_gas_limit_in_loops",
    "solidity_transfer_in_loop",
    "solidity_extra_gas_in_loops",
    "solidity_var_in_loop_for",
}


def extract_smartcheck_dos(findings_str):
    if not findings_str:
        return []

    cleaned = findings_str.strip().strip("{}")
    items = [item.strip().lower() for item in cleaned.split(",")]

    return [item for item in items if item in SMARTCHECK_DOS_FINDINGS]


def main():
    current_dir = Path(__file__).resolve().parent
    csv_files = sorted(current_dir.glob("*.csv"))

    global_count = {}

    for csv_file in csv_files:
        file_count = {}

        try:
            with csv_file.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)

                if not reader.fieldnames or not {"toolid", "findings"}.issubset(reader.fieldnames):
                    continue

                for row in reader:
                    toolid = (row.get("toolid") or "").lower()
                    if "smartcheck" not in toolid:
                        continue

                    findings = row.get("findings") or ""
                    dos_findings = extract_smartcheck_dos(findings)

                    for finding in dos_findings:
                        file_count[finding] = file_count.get(finding, 0) + 1
                        global_count[finding] = global_count.get(finding, 0) + 1

        except Exception:
            continue

        if file_count:
            print(f"\n=== File: {csv_file.name} ===")
            for k, v in file_count.items():
                print(f"{k}: {v}")

    if global_count:
        print("\n=== Global count ===")
        for k, v in global_count.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    main()