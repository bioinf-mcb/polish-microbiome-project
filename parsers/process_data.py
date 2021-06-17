from xls_parser import XLSParser
from rtf_parser import RTFParser
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

    try:
        lab_tests = XLSParser.parse(fname)
        odt_name = fname.replace("Wyniki badań XLS", "Karty pobytu")
        odt_name = odt_name.replace("XLS", "ODT").replace("xls", "odt")
        with zipfile.ZipFile(odt_name, 'r') as zip_ref:
            xml = zip_ref.read("content.xml").decode("utf-8")
        lab_tests = fix_dates(lab_tests, xml)
    except FileNotFoundError:
        rtf_name = fname.replace("Wyniki badań XLS", "Karty pobytu")
        rtf_name = rtf_name.replace("XLS", "RTF").replace("xls", "rtf")
        lab_tests = RTFParser.parse(rtf_name)
        # print(lab_tests)
        

    df = parse_to_csv(lab_tests, patient_id)
    df.to_csv("processed.csv", index=False)
    upload('http://localhost', df)

if __name__=="__main__":
    for fname in glob.glob("/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload/pacjenci 201-250/*/*.xls"):
        try:
            try:
                print(fname)
                process(fname)
            except (ValueError, FileNotFoundError) as e:
                raise e
                continue
        except XMLSyntaxError as e:
            print("File corrupted!")