#%%
import xml.etree.ElementTree as ET
import pandas as pd

# %%
with open("data/SAMEA3687225.xml", "r") as f:
    root = ET.fromstring(f.read())

attrs = root.findall(".//SAMPLE_ATTRIBUTE/TAG")

# %%
header = [i.text for i in attrs]

# %%
df = pd.DataFrame(columns=header)

# %%
df.to_csv("data/template.csv")
