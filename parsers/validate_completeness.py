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
from collections import defaultdict
from process_data import fix_dates
import zipfile
import tqdm
import threading

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
            rows[i]['RTF'] = FileState.FOUND
            rows[i]['Karta'] = FileState.FOUND
            text = rtf[0]
        else:
            rows[i]['RTF'] = FileState.NOT_FOUND
        
        odt = [x for x in inner if i+'.' in x and 'odt' in x]
        if len(odt)>0:
            rows[i]['ODT'] = FileState.FOUND
            rows[i]['Karta'] = FileState.FOUND
            text = odt[0]
        else:
            rows[i]['ODT'] = FileState.NOT_FOUND
    dfs.append(pd.DataFrame.from_dict(rows, orient='index'))

#%%
dirs = glob.glob(f"{ROOT_DIR}/[pP]acj*")
dfs = []
threads = []
main = True
for dir in dirs:
    inner = glob.glob(f"{dir}/*/*")
    t = threading.Thread(target=process_file_list, args=(inner, dfs, main))
    main = False
    t.start()
    threads.append(t)
    # ids = [get_patient_id(i) for i in inner]
    # ids = list(set(ids))
    # rows = defaultdict(dict)
    # for i in tqdm.tqdm(ids):
    #     rows[i]['Karta'] = FileState.NOT_FOUND
    #     rows[i]['Wyniki'] = FileState.NOT_FOUND
    #     rows[i]['RTF'] = FileState.NOT_FOUND
    #     rows[i]['ODT'] = FileState.NOT_FOUND

    #     xls = [x for x in inner if i+'.' in x and 'xls' in x]
    #     if len(xls)>0:
    #         try:
    #             XLSParser.open_file(xls[0])
    #             rows[i]['Wyniki'] = FileState.FOUND
    #             xls = xls[0]
    #         except Exception as e:
    #             print(e)
    #             rows[i]['Wyniki'] = FileState.ERROR
    #     else:
    #         rows[i]['Wyniki'] = FileState.NOT_FOUND
        
    #     rtf = [x for x in inner if i+'.' in x and 'rtf' in x]
    #     if len(rtf)>0:
    #         rows[i]['RTF'] = FileState.FOUND
    #         rows[i]['Karta'] = FileState.FOUND
    #         text = rtf[0]
    #     else:
    #         rows[i]['RTF'] = FileState.NOT_FOUND
        
    #     odt = [x for x in inner if i+'.' in x and 'odt' in x]
    #     if len(odt)>0:
    #         rows[i]['ODT'] = FileState.FOUND
    #         rows[i]['Karta'] = FileState.FOUND
    #         text = odt[0]
    #     else:
    #         rows[i]['ODT'] = FileState.NOT_FOUND

        # rows[i]['Karta'] = int(bool(rows[i]['ODT']+rows[i]['RTF']))
        # lab_tests = XLSParser.parse(xls)
        # rows[i]['Integralność'] = 0
        # if 'rtf' in text:
        #     lab_tests2 = RTFParser.parse(text)
        #     try:
        #         for idx, (profile, value) in lab_tests[['Wynik', 'Wartość']].iterrows():
        #             value = str(value)
        #             assert len(lab_tests2.query(f"Wynik==@profile and Wartość==@value")) > 0
        #         rows[i]['Integralność'] = 1
        #     except AssertionError:
        #         pass
    # dfs.append(pd.DataFrame.from_dict(rows, orient='index'))
for i in threads:
    i.join()

# %%
dataframe = pd.concat(dfs)
dataframe.index = dataframe.index.astype(int)
dataframe = dataframe.sort_index()
for i in range(1, dataframe.index.max()):
    if i not in dataframe.index:
        dataframe.loc[i] = [FileState.NOT_FOUND]*4

del dataframe["RTF"]
del dataframe["ODT"]

dataframe.sort_index().to_csv("summary.csv", sep=';')

# %%
