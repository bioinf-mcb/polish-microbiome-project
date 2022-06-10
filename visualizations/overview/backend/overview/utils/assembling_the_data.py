import biom
import glob
import pandas as pd
import json
from datetime import datetime

def map_id_to_run(level='', location="/data/bioms/*/ogu.biom"):
    mapping = []

    biom_files = glob.glob(f"{location}{level}*")
    for family in biom_files:
        data = json.loads(biom.load_table(family).to_json('me'))
        processed_samples = [i['id'].replace('_','-').split('-')[0] for i in data['columns']]
        processed_samples = list(set(processed_samples))

        fname = family
        run = fname
        for i in data['columns']:
            pid = i['id'].replace('_','-').split('-')[0]
            if 'undetermined' in pid.lower():
                continue

            sample_date = i['id'].replace('_','-').split('-')[1]
            sample_date = datetime.strptime(sample_date, '%d%m%Y')
            sample_id = i['id'].replace('_','-').split('-')[2]
            mapping.append({
                'patient_id': pid,
                'sample_date': sample_date,
                'sample_id': sample_id,
                'fname': fname,
                'run': run
            })
    mapping = pd.DataFrame.from_records(mapping)        
    return mapping
