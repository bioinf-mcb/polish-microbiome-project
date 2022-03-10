import glob
import re
import os
import zipfile
from .rtf_parser import RTFParser
from .odt_parser import ODTParser

ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/rolandkadaj/upload'


class PatientResolver:
    def __init__(self, root_dir=ROOT_DIR):
        self.xls_files = glob.glob(f"{root_dir}/*/*/*.xl*")
        self.odt_files = glob.glob(f"{root_dir}/*/*/*.odt*")
        self.ods_files = glob.glob(f"{root_dir}/*/*/*.ods*")
        self.rtf_files = glob.glob(f"{root_dir}/*/*/*.rtf*")
    
    def _get_matching_fname(self, patient_id, names):
        for i in names:
            name = os.path.split(i)[-1]
            if re.findall("(\d+)", name)[0] == str(patient_id):
                return i

    def get_files(self, patient_id) -> tuple((str, str)):
        """ Return a tuple of (lab_results, patient_card) files locations """
        xls = self._get_matching_fname(patient_id, self.xls_files)

        if xls is None:
            xls = self._get_matching_fname(patient_id, self.ods_files)
                
        text = self._get_matching_fname(patient_id, self.odt_files)
        if text is None:
            text = self._get_matching_fname(patient_id, self.rtf_files)
        return xls, text


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

class ParserRouter:
    @staticmethod
    def route(fname):
        if '.rtf' in fname:
            return RTFParser
        if '.odt' in fname:
            return ODTParser