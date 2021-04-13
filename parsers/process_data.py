from xls_parser import XLSParser
from lxml.etree import XMLSyntaxError
from results_to_csv import parse_to_csv
from upload_csv import upload
import sys
import re
import glob
import zipfile
import datetime

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = "data/pacjent nr 10.xls"

def fix_dates(df, xml):
    xml = xml.replace("<text:s/>", " ")
    for idx, row in df.iterrows():
        try:
            row["Data wyk."] = row["Data wyk."].strftime("%Y-%m-%d")
        except AttributeError:
            pass
        try:
            row["Data zlec."] = row["Data zlec."].strftime("%Y-%m-%d")
        except AttributeError:
            pass

        res = row["Wartość"]
        if type(res) is datetime.datetime:
            # a)
            if res.year != datetime.datetime.now().year and res.day == 1:
                parsed = float(f"{res.month}.{str(res.year)[-2:]}")
            # b)
            else:
                if row["Norma"] == "-":
                    prefix = ">"
                else:
                    norm = row["Norma"].replace("(", ".").replace(")", ".")
                    prefix = f'{norm}</text:p><text:p text:style-name="[^"]*"><text:span text:style-name="[^"]*">'
                if re.search(f"{prefix}{res.day}.{res.month}", xml) is not None:
                    parsed = float(f"{res.day}.{res.month}")
                elif re.search(f"{prefix}{res.day}.0{res.month}", xml) is not None:
                    parsed = float(f"{res.day}.0{res.month}")
                elif re.search(f"{prefix}{res.month}.{str(res.year)[-2:]}", xml) is not None:
                    parsed = float(f"{res.month}.{str(res.year)[-2:]}")

                else:
                    print(f"{prefix}{res.day}.{res.month}<")
                    print(f"{prefix}{res.day}.0{res.month}<")
                    print(df.iloc[[idx]])

                    raise ValueError

            df.iloc[idx]["Wartość"] = parsed
            # print(df.iloc[[idx]])
    return df


def process(fname):
    patient_id = re.findall(".*(?:numer)?(?:nr)? (\d*).*", fname)[0]
    print(fname, patient_id)

    lab_tests = XLSParser.parse(fname)
    odt_name = fname.replace("XLS", "ODT").replace("xls", "odt")
    with zipfile.ZipFile(odt_name, 'r') as zip_ref:
        xml = zip_ref.read("content.xml").decode("utf-8")
    
    lab_tests = fix_dates(lab_tests, xml)

    df = parse_to_csv(lab_tests, patient_id)
    df.to_csv("processed.csv", index=False)
    upload(df)

for fname in glob.glob("data/Pacjenci 70-100 XLS/*.xls"):
    try:
        try:
            process(fname)
        except (ValueError, FileNotFoundError):
            continue
    except XMLSyntaxError as e:
        print("File corrupted!")