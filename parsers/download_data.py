#%%
import json
import requests
from io import StringIO
import pandas as pd

# %%
with open("../db_pass", "r") as f:
    token = json.load(f)['token']

# %%
data = {
    'token': token,
    'content': 'record',
    'format': 'csv',
    'type': 'flat',
    'csvDelimiter': '',
    'rawOrLabel': 'raw',
    'rawOrLabelHeaders': 'raw',
    'exportCheckboxLabel': 'false',
    'exportSurveyFields': 'false',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'csv',
    'fields': 'patient_id,age,bmi,obesity,covid_test_date,weight,height,admission_date,final_date,death,sex'
}

r = requests.post('https://redcap.mcb.bio/api/',data=data)
print('HTTP Status: ' + str(r.status_code))
data = StringIO(r.text)

# %%
df = pd.read_csv(data)
# df = df[df["height"].apply(lambda x: not pd.isna(x))]
del df["redcap_repeat_instrument"]
del df["redcap_repeat_instance"]

df = df.dropna(axis=1, how='all')
df["bmi"] = df["bmi"].apply(lambda x: round(x, 1))
df.to_csv("tmp/metadata.csv", index=False)
print(df)

# %%
