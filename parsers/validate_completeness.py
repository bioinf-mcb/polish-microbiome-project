#%%
import sys

# from parsers.utils.odt_parser import ODTParser
sys.path.append("../parsers")

#%%
# from pandas.io.parsers import TextParser
from enum import Enum
from utils.xls_parser import XLSParser
from utils.rtf_parser import RTFParser
from utils.odt_parser import ODTParser
from utils.resolve_files import PatientResolver
import glob
import pandas as pd
import os
from collections import defaultdict, Counter
from process_data import fix_dates
import zipfile
import tqdm
# import threading
import multiprocessing
import biom
import json

#%%
ROOT_DIR = "/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload/"

#%%
class FileState:
    NOT_FOUND = "Not found"
    FOUND = "Found"
    ERROR = "Error!"
    CONTENT_EMPTY = "Missing MHR"

#%%
def get_patient_id(x):
    return os.path.split(x)[-1].split()[-1].split('.')[0]

#%%
resolver = PatientResolver()
def process_file_list(ids, dfs, main=False):
    rows = defaultdict(dict)

    for i in tqdm.tqdm(ids, disable = not main):
        rows[i]['Karta'] = FileState.NOT_FOUND
        rows[i]['Wyniki'] = FileState.NOT_FOUND
        rows[i]['RTF'] = FileState.NOT_FOUND
        rows[i]['ODT'] = FileState.NOT_FOUND

        xls, history = resolver.get_files(i)
        if xls is not None and len(xls)>0:
            try:
                XLSParser.open_file(xls)
                rows[i]['Wyniki'] = FileState.FOUND
            except Exception as e:
                print(e)
                rows[i]['Wyniki'] = FileState.ERROR
        else:
            rows[i]['Wyniki'] = FileState.NOT_FOUND
        
        if history is not None and 'rtf' in history:
            RTFParser.parse(history)
            epicrisis = RTFParser.parse_epicrysis(history)
            
            status = FileState.FOUND
            if len(epicrisis) == 0:
                status = FileState.CONTENT_EMPTY

            rows[i]['RTF'] = FileState.FOUND
            rows[i]['Karta'] = status
        elif history is not None:
            epicrisis = ODTParser.parse_epicrysis(history)

            status = FileState.FOUND
            if len(epicrisis) == 0:
                status = FileState.CONTENT_EMPTY

            rows[i]['ODT'] = FileState.FOUND
            rows[i]['Karta'] = status
            
    dfs.append(pd.DataFrame.from_dict(rows, orient='index'))

#%% Gather info about file
manager = multiprocessing.Manager()
dfs = manager.list()
threads = []
batch = 50
main = True
for i in range(1, 311, batch):
    t = multiprocessing.Process(target=process_file_list, args=(list(range(i, i+batch)), dfs, main))
    t.start()
    threads.append(t)
    main = False
    
for i in threads:
    i.join()

# %% Fill missing patient IDs
dataframe = pd.concat(dfs)
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

#%%
def _try_find_meta(x):
    try:
        if not pd.isna(metadata.loc[x, "admission_date"]) and not pd.isna(metadata.loc[x, "final_date"]):
            return "Found"
        else:
            return "Not found"
    except KeyError:
        return "Not found"
        
metadata = pd.read_csv("tmp/metadata.csv").set_index("patient_id")
dataframe["Data przyjęcia i wypisu"] = dataframe.index.map(_try_find_meta)

print(dataframe)
# %%
del dataframe["RTF"]
del dataframe["ODT"]

dataframe.sort_index().to_csv("summary.csv", sep=';')

# %%
