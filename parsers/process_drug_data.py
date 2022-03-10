import pandas as pd
import glob
from utils.rtf_parser import RTFParser
from utils.odt_parser import ODTParser
from utils.upload_csv import upload
from utils.resolve_files import PatientResolver, ParserRouter
from collections import defaultdict
import re

ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload'


def process(fname):
    parser = RTFParser
    if 'odt' in fname:
        parser = ODTParser
    
    return parser.parse_drugs(fname)

def to_csv(drug_data):
    data = []
    for i in drug_data:
        data.append(pd.DataFrame(i).drop_duplicates())
        
    res = pd.concat(data)
    res['patient_medicine_info_complete'] = 1
    res["redcap_repeat_instance"] = res["redcap_repeat_instance"].astype(int)
    res.to_csv("tmp/medicine.csv", index=False)
    upload('https://redcap.mcb.bio', res)

if __name__=="__main__":
    resolver = PatientResolver()
    data = []
    for i in range(1, 320):
        _, fname = resolver.get_files(i)
        if fname is None:
            print("Data for patient", i, "not found!")
            continue
        try:
            parser = ParserRouter.route(fname)
            
            try:
                res = parser.parse_drugs(fname)
            except StopIteration:
                print("Admission or release date not found for patient", i)
                continue

            res["patient_id"] = i
            res["redcap_repeat_instrument"] = 'patient_medicine_info'
            res["redcap_repeat_instance"] = list(range(1, len(list(res.values())[0])+1))
            data.append(res)
        except TypeError as e:
            print(i)
            raise e
            pass

    to_csv(data)