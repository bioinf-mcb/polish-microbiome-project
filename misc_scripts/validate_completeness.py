#%%
import sys
sys.path.append("../parsers")

#%%
# from pandas.io.parsers import TextParser
from enum import Enum
from xls_parser import XLSParser
from rtf_parser import RTFParser
from lxml.etree import XMLSyntaxError
from results_to_csv import parse_to_csv
import glob
import pandas as pd
import os
from collections import defaultdict, Counter
from process_data import fix_dates
import zipfile
import tqdm
import threading
import biom
import json

#%%
ROOT_DIR = "/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload/"

#%%
class FileState:
    NOT_FOUND = "Not found"
    FOUND = "Found"
    ERROR = "Error!"

#%%
def get_patient_id(x):
    return os.path.split(x)[-1].split()[-1].split('.')[0]

#%%
def process_file_list(inner, dfs, main=False):
    ids = [get_patient_id(i) for i in inner]
    ids = list(set(ids))
    rows = defaultdict(dict)
    for i in tqdm.tqdm(ids, disable = not main):
        rows[i]['Karta'] = FileState.NOT_FOUND
        rows[i]['Wyniki'] = FileState.NOT_FOUND
        rows[i]['RTF'] = FileState.NOT_FOUND
        rows[i]['ODT'] = FileState.NOT_FOUND

        xls = [x for x in inner if i+'.' in x and 'xls' in x]
        if len(xls)>0:
            try:
                XLSParser.open_file(xls[0])
                rows[i]['Wyniki'] = FileState.FOUND
                xls = xls[0]
            except Exception as e:
                print(e)
                rows[i]['Wyniki'] = FileState.ERROR
        else:
            rows[i]['Wyniki'] = FileState.NOT_FOUND
        
        rtf = [x for x in inner if i+'.' in x and 'rtf' in x]
        if len(rtf)>0:
            try:
                RTFParser.parse(rtf[0])
                rows[i]['RTF'] = FileState.FOUND
                rows[i]['Karta'] = FileState.FOUND
                text = rtf[0]
            except Exception as e:
                print(e)
                rows[i]['Karta'] = FileState.ERROR

        else:
            rows[i]['RTF'] = FileState.NOT_FOUND
        
        odt = [x for x in inner if i+'.' in x and 'odt' in x]
        if len(odt)>0:
            try:
                with zipfile.ZipFile(odt[0], 'r') as zip_ref:
                    xml = zip_ref.read("content.xml").decode("utf-8")
                    lab_tests = XLSParser.parse(xls)
                    lab_tests = fix_dates(lab_tests, xml)

                rows[i]['ODT'] = FileState.FOUND
                rows[i]['Karta'] = FileState.FOUND
                text = odt[0]
            except Exception as e:
                print(e)
                rows[i]['Karta'] = FileState.ERROR
        else:
            rows[i]['ODT'] = FileState.NOT_FOUND
    dfs.append(pd.DataFrame.from_dict(rows, orient='index'))

#%%
# dirs = glob.glob(f"{ROOT_DIR}/[pP]acj*")
# dfs = []
# threads = []
# main = True
# for dir in dirs:
#     inner = glob.glob(f"{dir}/*/*")
#     t = threading.Thread(target=process_file_list, args=(inner, dfs, main))
#     main = False
#     t.start()
#     threads.append(t)
    
# for i in threads:
#     i.join()

#%% Fill missing patient IDs
# dataframe = pd.concat(dfs)
dataframe = pd.DataFrame(columns=["Karta", "Wyniki", "RTF", "ODT"])
dataframe.index = dataframe.index.astype(int)
dataframe = dataframe.sort_index()
for i in range(1, 311):
    if i not in dataframe.index:
        dataframe.loc[i] = [FileState.NOT_FOUND]*4

#%% Add info about metadata 
for fname in glob.glob(f"{ROOT_DIR}/*/zestawienie*.xlsx"):
    patient_df = pd.read_excel(fname)
    for _, row in patient_df.iterrows():
        i = row['Numer pacjenta ']
        dataframe.loc[i, "Metadane"] = FileState.FOUND

dataframe = dataframe.fillna(FileState.NOT_FOUND)

#%% Add info about fully processed samples
biom_files = glob.glob("/storage/PawelLab/kkopera/COVID/Run*/R*/results/woltka/classify/fam*")
for family in biom_files:
    data = json.loads(biom.load_table(family).to_json('me'))
    processed_samples = [i['id'].replace('_','-').split('-')[0] for i in data['columns']]
    processed_samples = Counter(processed_samples)
    for pid, val in processed_samples.items():
        val = int(val)
        try:
            pid = int(pid)
        except ValueError as e:
            continue
        try:
            if not pd.isna(dataframe.loc[pid, "Przetworzone próbki"]):
                dataframe.loc[pid, "Przetworzone próbki"] += val
            else:
                dataframe.loc[pid, "Przetworzone próbki"] = val
        except KeyError as e:
            dataframe.loc[pid, "Przetworzone próbki"] = val

dataframe.loc[:, "Przetworzone próbki"] = dataframe.loc[:, "Przetworzone próbki"].fillna(0).astype(int)
print(dataframe)
# %%
del dataframe["RTF"]
del dataframe["ODT"]

dataframe.sort_index().to_csv("summary.csv", sep=';')

# %%
