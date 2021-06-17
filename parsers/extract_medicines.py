#%%
import re
import zipfile
import glob

#%%
ROOT_DIR = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload'

#%%
def extract_drugs(fname):
    patient_id = re.findall(".*(?:numer)?(?:nr)? (\d*).*", fname)[0]
    print(fname, patient_id)

    with zipfile.ZipFile(fname, 'r') as zip_ref:
        xml = zip_ref.read("content.xml").decode("utf-8")
    
    xml = re.sub("<[^<]+>", "", xml)

    med = re.findall("Nazwa międzynaro.:(.+?)(?=Dawkowanie)", xml)
    med = list(set([i.strip() for i in med]))
    return med

if __name__=="__main__":
    for fname in glob.glob(f"{ROOT_DIR}/pacjenci 70-100/*/*.odt"):
        try:
            print(extract_drugs(fname))
        except (ValueError, FileNotFoundError):
            continue

# %%
# content = extract_drugs(fname)
# content

# # %%
# med = re.findall("Nazwa międzynaro.:(.+?)(?=Dawkowanie)", content)[0].strip()
# doze = re.findall(f"(?<={med}) Dawkowanie: (\S*)", content)[0]
# re.findall(f"(?<={med}) ([^(?=Okres podawania)]*)", content)[0]


# re.findall("Nazwa międzynaro.:([^(?=Dawkowanie)]*)", content)[0]


# %%
