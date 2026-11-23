import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from practice.suite import generate_cases, validate_output, validate_suite

ROOT=Path(__file__).resolve().parents[1]

class PracticeTests(unittest.TestCase):
    def test_weights(self):
        self.assertTrue(validate_suite())
    def test_reference(self):
        for case in generate_cases("fresh-sample"):
            with self.subTest(case=case.name), tempfile.TemporaryDirectory() as d:
                p=Path(d)/"input.csv"
                p.write_bytes(case.csv_data)
                result=subprocess.run([sys.executable,str(ROOT/"examples/reference/main.py"),str(p)],capture_output=True,text=True,timeout=5)
                self.assertEqual(result.returncode,0,result.stderr)
                valid,reason,_=validate_output(result.stdout,case)
                self.assertTrue(valid,reason)
    def test_broken(self):
        case=generate_cases("fresh-sample")[0]
        result=subprocess.run([sys.executable,str(ROOT/"examples/broken/main.py")],capture_output=True,text=True)
        self.assertFalse(validate_output(result.stdout,case)[0])
