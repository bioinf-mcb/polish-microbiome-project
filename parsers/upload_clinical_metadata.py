import pandas as pd
import glob
from extract_medicines import extract_drugs
from upload_csv import upload
from resolve_files import PatientResolver, get_raw_text
from collections import defaultdict
import re

ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload'

resolv = PatientResolver()