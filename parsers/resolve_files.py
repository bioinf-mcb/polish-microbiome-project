import glob
import re
import zipfile
from rtf_parser import RTFParser

ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload'


class PatientResolver:
    def __init__(self, root_dir=ROOT_DIR):
        self.xls_files = glob.glob(f"{root_dir}/*/*/*.xl*")
        self.odt_files = glob.glob(f"{root_dir}/*/*/*.odt*")
        self.rtf_files = glob.glob(f"{root_dir}/*/*/*.rtf*")
    
    def get_files(self, patient_id):
        try:
            xls = [i for i in self.xls_files if f"{patient_id}." in i][0]
        except IndexError:
            xls = None
        try:
            text = [i for i in self.odt_files if f"{patient_id}." in i][0]
        except IndexError:
            try:
                text = [i for i in self.rtf_files if f"{patient_id}." in i][0]
            except IndexError:
                text = None

        return patient_id, xls, text


def get_raw_text(fname):
    if 'rtf' in fname:
        return RTFParser.parse_epicrysis(fname)
    
    with zipfile.ZipFile(fname, 'r') as zip_ref:
        xml = zip_ref.read("content.xml").decode("utf-8")
    
    xml = re.sub("<[^<]+>", "", xml)
    try:
        xml = re.findall("Epikryza(.*)", xml)[0]
    except IndexError:
        return ''
    return xml
