#%%
import json
import requests
import pandas as pd

with open("../db_pass", "r") as f:
    token = json.load(f)['token']

#%%
def upload(client, dataframe):
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
    r = requests.post(f'{client}/api/',data=data, verify=False)
    # print('HTTP Status: ' + str(r.status_code))
    print(r.content)
    assert r.status_code==200


if __name__ == "__main__":
    df = pd.read_csv("upload.csv")
    upload(df)