#!/usr/bin/env python3
"""GPT-6-assisted organizer demo agent for WireUnWired WU-BOM-004.

Reads the live personalized benchmark JSON from a local file or stdin and
emits exact issue labels. Does not contain any answer key, API token, private
fixture, user data or WordPress credentials.

This is a *house demonstration*, not independent proof of agent autonomy.
"""
from __future__ import annotations

import argparse
import json
import sys


def audit_case(case: dict) -> dict:
    """Evaluate one BOM case without relying on its name or seeded examples."""
    seen = set()
    issues = set()
    for row in case["rows"]:
        refs = [ref.strip() for ref in str(row["refs"]).split(",") if ref.strip()]
        quantity = int(row["quantity"])
        mpn = str(row["mpn"])
        if quantity <= 0:
            issues.add("invalid_quantity")
        if quantity != len(refs):
            issues.add("quantity_mismatch")
        if not mpn.strip():
            issues.add("missing_mpn")
        if not refs:
            issues.add("missing_reference")
        for ref in refs:
            if ref in seen:
                issues.add("duplicate_reference")
            seen.add(ref)
    return {"case_id": case["case_id"], "issues": sorted(issues)}


def solve(benchmark: dict) -> list[dict]:
    cases = benchmark["cases"]
    if len(cases) != 6 or len({case["case_id"] for case in cases}) != 6:
        raise ValueError("Expected six distinct personalized cases")
    return [audit_case(case) for case in cases]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Personalized cases JSON; defaults to stdin")
    parser.add_argument("--out", help="Output answers JSON; defaults to stdout")
    args = parser.parse_args()
    if args.input:
        with open(args.input, encoding="utf-8") as file:
            benchmark = json.load(file)
    else:
        benchmark = json.load(sys.stdin)
    encoded = json.dumps(solve(benchmark), indent=2) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as file:
            file.write(encoded)
    else:
        sys.stdout.write(encoded)


if __name__ == "__main__":
    main()
