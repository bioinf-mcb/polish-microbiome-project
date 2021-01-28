from xls_parser import XLSParser
from lxml.etree import XMLSyntaxError
from results_to_csv import parse_to_csv
from upload_csv import upload
import sys
import re
import glob


if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = "data/pacjent nr 10.xls"

def process(fname):
    patient_id = re.findall(".*(?:numer)?(?:nr)? (\d*).*", fname)[0]
    print(fname, patient_id)

    lab_tests, patient_name = XLSParser.parse(fname)
    df = parse_to_csv(lab_tests, patient_id)
    df.to_csv("processed.csv", index=False)
    upload(df)

for fname in glob.glob("data/Pacjenci 1-69 XLS/*.xls"):
    try:
        process(fname)
    except XMLSyntaxError as e:
        print("File corrupted!")