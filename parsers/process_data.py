from utils.xls_parser import XLSParser
from utils.rtf_parser import RTFParser
from lxml.etree import XMLSyntaxError
from results_to_csv import parse_to_csv
from utils.upload_csv import upload
import sys
import re
import glob
import zipfile
import datetime
from utils.resolve_files import PatientResolver
from threading import Thread
from tqdm import trange

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


def process(results, history, patient_id, pbar=None):
    # patient_id = re.findall(".*(?:numer)?(?:nr)? (\d*).*", fname)[0]

    # try:
    #     lab_tests = XLSParser.parse(fname)
    #     odt_name = fname.replace("Wyniki badań XLS", "Karty pobytu")
    #     odt_name = odt_name.replace("XLS", "ODT").replace("xls", "odt")
    #     with zipfile.ZipFile(odt_name, 'r') as zip_ref:
    #         xml = zip_ref.read("content.xml").decode("utf-8")
    #     lab_tests = fix_dates(lab_tests, xml)
    # except FileNotFoundError:
    #     rtf_name = fname.replace("Wyniki badań XLS", "Karty pobytu")
    #     rtf_name = rtf_name.replace("XLS", "RTF").replace("xls", "rtf")
    #     lab_tests = RTFParser.parse(rtf_name)
        # print(lab_tests)
        
    if '.rtf' in history:
        lab_tests = RTFParser.parse(history)
    else:
        lab_tests = XLSParser.parse(results)
        with zipfile.ZipFile(history, 'r') as zip_ref:
            xml = zip_ref.read("content.xml").decode("utf-8")
        lab_tests = fix_dates(lab_tests, xml)
    
    pbar.read_tests += 1
    df = parse_to_csv(lab_tests, patient_id)
    pbar.parsed_csvs += 1
    df.to_csv("processed.csv", index=False)
    t = Thread(target=upload, args=('https://redcap.mcb.bio', df))
    t.start()
    pbar.uploaded += 1

    pbar.set_postfix(read_tests=pbar.read_tests, parsed_csvs=pbar.parsed_csvs, uploaded=pbar.uploaded)
    return t

if __name__=="__main__":
    threads = []
    resolver = PatientResolver()

    with trange(1, 60) as pbar:
        pbar.read_tests = 0
        pbar.parsed_csvs = 0
        pbar.uploaded = 0
        for i in pbar:
            results, history = resolver.get_files(i)
            if history is None:
                print("History not found for patient", i)
                continue

            t = process(results, history, i, pbar)
            threads.append(t)

            if len(threads)==16:
                for i in threads:
                    i.join()
                threads = []