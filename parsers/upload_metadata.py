import pandas as pd
import glob
from extract_medicines import extract_drugs
from upload_csv import upload
from resolve_files import PatientResolver, get_raw_text
from collections import defaultdict
import re
import datetime

ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload'

resolv = PatientResolver()

def get_data(df):
    data = df["patient_id"].apply(lambda x: resolv.get_files(x))
    
    res = defaultdict(list)
    for idx, _, text_file in data:
        if text_file is None:
            print(idx, "file missing!")
            res["sex"].append('')
            res["age"].append(-1)
            continue
            
        text = get_raw_text(text_file).lower()
        if "pacjentka" in text or "pacjentkę" in text:
            res["sex"].append(2)
        else:
            res["sex"].append(1)

        try:
            res["age"].append(re.findall("\d+", text)[0])
        except IndexError:
            print(idx, "age not found")
            res["age"].append(-1)
    
    df.loc[:, "age"] = res["age"]
    df.loc[:, "sex"] = res["sex"]
    return df

def fix_dates(df):
    def _fix(date):
        try:
            return date.strftime("%Y-%m-%d")
        except AttributeError:
            return datetime.datetime.strptime(date, "%d.%m.%Y").strftime("%Y-%m-%d")
    df.loc[:, "final_date"] = clinical_data_df["final_date"].apply(_fix)
    df.loc[:, "admission_date"] = clinical_data_df["admission_date"].apply(_fix)
    df.loc[:, "covid_test_date"] = clinical_data_df["covid_test_date"].apply(_fix)
    
    return df

if __name__=="__main__":
    for fname in glob.glob(f"{ROOT_DIR}/*/zestawienie*.xlsx"):
        print(fname)

        patient_df = pd.read_excel(fname)

        basic_data_df = patient_df.loc[:, ["Numer pacjenta ", "waga ", "wzrost"]]
        basic_data_df.columns = ["patient_id", "weight", "height"]
        basic_data_df.loc[:, "patient_info_complete"] = 1
        basic_data_df = basic_data_df.pipe(get_data)
        print("Basic data:")
        upload("http://localhost", basic_data_df)

        clinical_data_df = patient_df.loc[:, ["Numer pacjenta ", "data testu SARS-CoV-2", "data włączenia ", "data wyłączenia", "Zgon"]]
        clinical_data_df.columns = ["patient_id", "covid_test_date", "admission_date", "final_date", "death"]
        clinical_data_df["death"] = clinical_data_df["death"].apply(lambda x: 1 if x=="tak" else 2)
        clinical_data_df = clinical_data_df.pipe(fix_dates)
        clinical_data_df.loc[:, "patient_info_complete"] = 1
        print("Clinical data:")
        upload("http://localhost", clinical_data_df)
