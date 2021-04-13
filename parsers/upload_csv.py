#%%
import json
import requests
import pandas as pd

with open("db_pass.json", "r") as f:
    token = json.load(f)['token']

#%%
def upload(dataframe):
    data = {
        'token': token,
        'content': 'record',
        'format': 'csv',
        'type': 'flat',
        'overwriteBehavior': 'normal',
        'forceAutoNumber': 'false',
        'data': '',
        'returnContent': 'count',
        'returnFormat': 'json'
    }

    data['data'] = dataframe.to_csv(index=False).strip()
    r = requests.post('http://argon.mcb.uj.edu.pl:7000/api/',data=data)
    print('HTTP Status: ' + str(r.status_code))


if __name__ == "__main__":
    df = pd.read_csv("upload.csv")
    upload(df)
