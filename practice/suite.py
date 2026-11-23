"""Deterministic public practice fixtures for WU-BOM-001, not official tests."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
import random

SUITE_VERSION = "wu-bom-001-python-v0.1"
TECHNICAL_MAX = 90
DOCUMENTATION_MAX = 10
CODES = frozenset({"MISSING_MPN","INVALID_QUANTITY","DUPLICATE_REFERENCE","MISSING_MANUFACTURER","FIELD_COUNT_MISMATCH","REPEATED_MPN"})
SEVERITIES = frozenset({"error","warning"})

@dataclass(frozen=True)
class Case:
    name: str
    csv_data: bytes
    expected: frozenset[tuple[int,str,str]]
    data_rows: int
    points: int
    category: str

def _case(name: str, data: str, expected: set, rows: int, points: int, category: str) -> Case:
    return Case(name,data.encode("utf-8"),frozenset(expected),rows,points,category)

def generate_cases(seed: str) -> list[Case]:
    if not seed or len(seed)>160:
        raise ValueError("Seed length must be between 1 and 160")
    rng=random.Random(int.from_bytes(hashlib.sha256(seed.encode()).digest()[:16],"big"))
    tag=str(rng.randint(10000,99999))
    p1,p2,p3="ABC"+tag,"RTE"+tag,"ZZZ"+tag
    h="MPN,Manufacturer,Quantity,Reference Designators,Description\n"
    return [
        _case("clean_baseline",h+f"{p1},Acme,2,R1 R2,resistors\n{p2},Other,1,U1,controller\n",set(),2,5,"detection"),
        _case("missing_part_number",h+f"{p1},Acme,1,R1,good\n   ,Other,1,U2,missing\n",{(3,"MISSING_MPN","error")},2,9,"detection"),
        _case("invalid_quantities",h+f"{p1},Acme,0,R1,zero\n{p2},Acme,-2,R2,negative\n{p3},Acme,2.5,R3,fractional\nNEW{tag},Acme,abc,R4,text\n",{(2,"INVALID_QUANTITY","error"),(3,"INVALID_QUANTITY","error"),(4,"INVALID_QUANTITY","error"),(5,"INVALID_QUANTITY","error")},4,12,"detection"),
        _case("duplicate_references",h+f"{p1},Acme,2,C1 C2,first\n{p2},Other,2,C2 C3,second\n",{(3,"DUPLICATE_REFERENCE","error")},2,10,"detection"),
        _case("missing_manufacturer",h+f"{p1},,1,U1,blank\n{p2},Acme,1,U2,good\n",{(2,"MISSING_MANUFACTURER","error")},2,8,"detection"),
        _case("field_count_mismatch",h+f"{p1},Acme,1,U1,full\n{p2},Acme,1,U2\n",{(3,"FIELD_COUNT_MISMATCH","error")},2,8,"detection"),
        _case("repeated_mpn",h+f"{p1},Acme,1,C1,first\n{p1},Acme,1,C2,repeat\n",{(3,"REPEATED_MPN","warning")},2,8,"detection"),
        _case("quoted_commas",h+f'"{p1}","Acme, Ltd",1,U1,"a ""quoted"" description"\n',set(),1,5,"format"),
        _case("semicolon_delimiter","MPN;Manufacturer;Quantity;Reference Designators;Description\n"+f"{p1};Acme;2;R1 R2;good\n{p2};Other;1;U1;good\n",set(),2,5,"format"),
        _case("tab_delimiter","MPN\tManufacturer\tQuantity\tReference Designators\tDescription\n"+f"{p1}\tAcme\t1\tU1\tclean\n",set(),1,5,"format"),
        _case("crlf_and_escaping",h.replace("\n","\r\n")+f'"{p1}","Acme",1,U1,"quote ""escaped"""\r\n',set(),1,5,"format"),
    ]

def validate_output(stdout: str, case: Case) -> tuple[bool,str,tuple]:
    if len(stdout.encode("utf-8"))>128000: return False,"Output exceeds limit",()
    try: obj=json.loads(stdout,parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite")))
    except (json.JSONDecodeError,ValueError,TypeError): return False,"not one valid JSON document",()
    if not isinstance(obj,dict) or type(obj.get("row_count")) is not int or obj["row_count"]!=case.data_rows:
        return False,"wrong row_count",()
    issues=obj.get("issues")
    if not isinstance(issues,list) or len(issues)>300: return False,"invalid issues",()
    normalized=[]
    for item in issues:
        if not isinstance(item,dict): return False,"issue not object",()
        row,severity,code=item.get("row"),item.get("severity"),item.get("code")
        if type(row) is not int or not 2<=row<=case.data_rows+1: return False,"invalid row",()
        if severity not in SEVERITIES or code not in CODES or not isinstance(item.get("message"),str): return False,"invalid issue",()
        normalized.append((row,code,severity))
    if len(normalized)!=len(set(normalized)): return False,"duplicate issue",()
    canonical=(obj["row_count"],tuple(sorted(normalized)))
    if set(normalized)!=set(case.expected): return False,"issue mismatch",canonical
    return True,"passed",canonical

def validate_suite():
    cases=generate_cases("built-in-regression")
    assert len(cases)==11
    assert sum(c.points for c in cases)==80
    assert sum(c.points for c in cases if c.category=="detection")==60
    assert sum(c.points for c in cases if c.category=="format")==20
    return True
