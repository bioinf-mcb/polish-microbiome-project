from xls_parser import XLSParser
from results_to_csv import parse_to_csv
from upload_csv import upload
import sys

if len(sys.argv) > 1:
    fname = sys.argv[2]
else:
    fname = "data/pacjent nr 1 excel.xls"

lab_tests, patient_name = XLSParser.parse(fname)
df = parse_to_csv(lab_tests, patient_name)
upload(df)