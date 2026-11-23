"""Reference BOM checker for controlled test fixtures; does not fetch network data."""
from __future__ import annotations
import csv
import json
from pathlib import Path
import re
import sys


def run(filename: str) -> dict:
    raw=Path(filename).read_text(encoding="utf-8-sig")
    head=raw.splitlines()[0] if raw else ""
    delim="\t" if "\t" in head else ";" if head.count(";") > head.count(",") else ","
    reader=csv.reader(raw.splitlines(keepends=True),delimiter=delim)
    lines=list(reader)
    if not lines:
        return {"row_count":0,"issues":[]}
    issues=[]
    keys=[x.lower().strip() for x in lines[0]]
    mapping={"mpn":keys.index("mpn"),"manufacturer":keys.index("manufacturer"),
             "quantity":keys.index("quantity"),"refs":keys.index("reference designators")}
    refs,mpns=set(),set()
    for row_num, row in enumerate(lines[1:],2):
        def add(code,severity="error"):
            issues.append({"row":row_num,"severity":severity,"code":code,"message":code.replace("_"," ").title()})
        if len(row)!=len(keys):
            add("FIELD_COUNT_MISMATCH")
        def get(field):
            ix=mapping[field]
            return row[ix].strip() if ix<len(row) else ""
        mpn,mfr,qty,refs_string=get("mpn"),get("manufacturer"),get("quantity"),get("refs")
        if not mpn: add("MISSING_MPN")
        if not mfr: add("MISSING_MANUFACTURER")
        if not re.fullmatch(r"[1-9][0-9]*",qty): add("INVALID_QUANTITY")
        if mpn:
            if mpn in mpns: add("REPEATED_MPN","warning")
            mpns.add(mpn)
        for ref in filter(None,re.split(r"[,;\s]+",refs_string)):
            if ref in refs: add("DUPLICATE_REFERENCE")
            refs.add(ref)
    return {"row_count":max(0,len(lines)-1),"issues":issues}

if __name__=="__main__":
    print(json.dumps(run(sys.argv[1]),separators=(",",":")))
