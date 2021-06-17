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
    'fields': 'patient_id,age,bmi,covid_test_date,date_of_test,weight,height,admission_date,final_date,death,sex'
}

r = requests.post('http://192.168.45.244/api/',data=data)
print('HTTP Status: ' + str(r.status_code))
data = StringIO(r.text)

# %%
df = pd.read_csv(data)
df = df[df["height"].apply(lambda x: not pd.isna(x))]
df = df.dropna(axis=1, how='all')
df["bmi"] = df["bmi"].apply(lambda x: round(x, 1))
df.to_csv("metadata.csv", index=False)
print(df)

# %%
