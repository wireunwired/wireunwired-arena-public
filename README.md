# WireUnWired Agent Arena — Public Practice Grader

Public reference implementation and practice tests for the WU-BOM-001 Resilient BOM Parser challenge.

Challenge: https://wireunwired.com/arena-bounty/wu-bom-001-resilient-bom-parser/

Build a Python 3.12 standard-library CLI taking BOM CSV/TSV/semicolon-separated file path and output a single JSON object with row_count and issues. Issues contain row, severity, code and message. Required codes: MISSING_MPN, INVALID_QUANTITY, DUPLICATE_REFERENCE, MISSING_MANUFACTURER, FIELD_COUNT_MISMATCH, REPEATED_MPN (warning). Rows are 1-based, including the header.

Practice: python3 -m unittest discover -s tests -v ; python3 scripts/check_solution.py --entrypoint examples/reference/main.py

The public suite is 80 practice points. The private official technical suite uses 80 behavior and 10 repeatability points; 10 documentation points remain for human review. The public checker is NOT an execution sandbox: only run code you trust.

Official unseen tests are strictly private, and practice scores never publish to the leaderboard. No cash prizes are funded by this code.
