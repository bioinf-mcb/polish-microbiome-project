#%%
import pandas as pd
from collections import defaultdict

def parse_to_csv(lab_tests, patient_id) -> pd.DataFrame:
    # lab_tests, patient_name = XLSParser.parse("data/pacjent nr 1 excel.xls")

    results = defaultdict(list)
    for idx, row in lab_tests.iterrows():
        if 'lekarz' in row['Wynik']:
            continue
        if row['Profil'] == 'Profil':
            continue
        if '-' not in row['Data wyk.']:
            continue

        results['patient_id'].append(patient_id)
        results['redcap_repeat_instrument'].append("lab_result")
        results['redcap_repeat_instance'].append(idx+1)
        # results['patient_name'].append('')
        # results['patient_info_complete'].append('')

        results['profile'].append(row['Profil'])
        results['date_of_test'].append(row['Data wyk.'].split()[0])
        results['order_no'].append(row['Nr zlecenia'])
        results['procedure'].append(row['Wynik'])
        results['value'].append(row['Wartość'])

        try:
            test_norm = row['Norma'].rstrip(")").lstrip("(").split(" - ")
        except AttributeError:
            test_norm = row['Norma']
            if test_norm==0:
                test_norm = '-'

        if test_norm[0] == '':
            test_norm[0] = 0
        elif test_norm[0] == '-':
            test_norm = ['-', '-']
        
        results['norm_lower'].append(test_norm[0])
        results['norm_upper'].append(test_norm[1])
        results['unit'].append(row['Jedn.'])
        results['lab_result_complete'].append(1)

    results['patient_id'].append(patient_id)
    results['redcap_repeat_instrument'].append('')
    results['redcap_repeat_instance'].append('')
    # results['patient_name'].append('')
    # results['patient_info_complete'].append(1)

    results['profile'].append('')
    results['date_of_test'].append('')
    results['order_no'].append('')
    results['procedure'].append('')
    results['value'].append('')
    results['norm_lower'].append('')
    results['norm_upper'].append('')
    results['unit'].append('')
    results['lab_result_complete'].append('')
    return pd.DataFrame(results)

#%%
if __name__ == "__main__":
    from xls_parser import XLSParser
    # from rtf_parser import RTFParser

    tests, name = XLSParser.parse("data/pacjent nr 1 excel.xls")
    results = parse_to_csv(tests, 1)
    results.to_csv("upload.csv", index=False)
