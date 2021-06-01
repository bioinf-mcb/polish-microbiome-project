#%%
import json
import requests
from io import StringIO
import pandas as pd

# %%
with open("db_pass", "r") as f:
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
    'exportSurveyFields': 'true',
    'exportDataAccessGroups': 'false',
    'returnFormat': 'csv'
}

r = requests.post('http://192.168.45.244/api/',data=data)
print('HTTP Status: ' + str(r.status_code))
data = StringIO(r.text)
# %%
df = pd.read_csv(data)
df.to_csv("survey_data.csv")
print(df)
# %%
