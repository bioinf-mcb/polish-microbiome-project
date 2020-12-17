#%%
import requests
import pandas as pd

#%%
def upload(dataframe):
    data = {
        'token': 'A65197E9E9857DFA5A15F6DD03E5E6F1',
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