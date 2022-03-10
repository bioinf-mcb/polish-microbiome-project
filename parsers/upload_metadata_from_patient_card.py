#%%
from utils.xls_parser import XLSParser
from utils.odt_parser import ODTParser
from utils.rtf_parser import RTFParser
from utils.upload_csv import upload
import pandas as pd
from utils.resolve_files import PatientResolver
import sys

# %%

if __name__=="__main__":
    resolver = PatientResolver()
    if len(sys.argv)==1:
        rng = range(1, 311)
    else:
        rng = sys.argv[1:]

    for patient_id in rng:
        laboratory, history = resolver.get_files(patient_id)

        if laboratory is None:
            print(f"Absent laboratory data! {patient_id = }")
            pass
        if history is None:
            print(f"Absent patient history! {patient_id = }")
            continue

        if '.rtf' in history:
            parser = RTFParser
        else:
            parser = ODTParser

        try:
            age = parser.parse_age(history)
        except StopIteration:
            print(f"Absent age!")
            age = ''

        try:
            stay_start, stay_end = parser.parse_hospitalization_time(history)
        except StopIteration:
            print(f"Absent start/end date! {patient_id = }")
            stay_start = ''
            stay_end = ''

        epicrisis = parser.parse_epicrysis(history)
        death = None
        if epicrisis != '':
            death = 'zgon' in epicrisis.lower()
        else:
            print(f"Absent epicrisis! {patient_id = }")
            continue

        text = parser.to_text(history)
        obese = int('otyłość' in text.lower())

        try:
            sars = XLSParser.parse(laboratory)
            sars = sars.loc[sars['Profil'].apply(lambda x: 'SARS-CoV-2' in x)].sort_values("Data wyk.")
            sars = str(sars.loc[sars['Wartość']==1]['Data wyk.'].iloc[0]).split()[0]
        except Exception as e:
            sars = ''
            print(f"Absent positive COVID test date! {patient_id = }")
            # continue
            pass

        clinical_data_df = pd.DataFrame.from_dict([{
            "patient_id": patient_id,
            "age": age,
            "covid_test_date": sars,
            "admission_date": stay_start,
            "final_date": stay_end,
            "death": death,
            "obesity": obese
        }], orient='columns')

        clinical_data_df["death"] = clinical_data_df["death"].apply(lambda x: 1 if x else 2)
        clinical_data_df.loc[:, "patient_clinical_info_complete"] = 1
        upload("https://redcap.mcb.bio", clinical_data_df)
        print(f"Patient uploaded! {patient_id = }")
        clinical_data_df