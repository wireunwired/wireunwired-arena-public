"""Practice runner executes only code you trust on your own machine. Not a sandbox."""
import argparse
import subprocess
import tempfile
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from practice.suite import generate_cases,validate_output
p=argparse.ArgumentParser()
p.add_argument("--entrypoint",required=True)
p.add_argument("--seed",default="public-practice-v0.2")
a=p.parse_args()
script=Path(a.entrypoint).resolve()
if not script.is_file() or script.suffix!=".py": p.error("trusted local Python script required")
points=0
total=0
for case in generate_cases(a.seed):
    with tempfile.TemporaryDirectory(prefix="wu-practice-") as d:
        inp=Path(d)/"bom.csv"
        inp.write_bytes(case.csv_data)
        try:
            proc=subprocess.run([sys.executable,"-B","-S",str(script),str(inp)],capture_output=True,text=True,timeout=5,check=False)
            ok,reason,_=validate_output(proc.stdout,case) if proc.returncode==0 else (False,"nonzero exit",())
        except subprocess.TimeoutExpired: ok,reason=False,"timeout"
        points+=case.points if ok else 0
        total+=case.points
        print(f'{case.name}: {"PASS" if ok else "FAIL"} ({reason})')
print(f"Public practice fixture points: {points}/{total}. This is NOT an official score.")
