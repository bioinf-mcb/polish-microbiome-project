#%%
import pandas as pd
from collections import defaultdict

#%%
# data = pd.read_html("data/pacjent nr 1 excel.xls")[0]
# data.columns = data.columns.droplevel().droplevel()

# print(data)
# print(data['Profil'])

# %%
class XLSParser:
    @staticmethod
    def parse_norm(x):
        if type(x)==str:
            x = x.replace("( -", "(0 -")
            try:
                return list(map(float, x[1:-1].split(" - ")))
            except ValueError:
                return None
        return None

    @staticmethod
    def check_norm(x):
        norm = XLSParser.parse_norm(x['Norma'])
        if norm is None:
            return True
        res = float(x['Wartość'])
        return res >= norm[0] and res<=norm[1]

    @staticmethod
    def parse(fname):
        data = pd.read_html(fname)[0]
        name = data.columns[0][0]
        data.columns = data.columns.droplevel().droplevel()
        data = data.dropna()
        
        covid_test = data[data['Profil'] == 'Koronawirus SARS-CoV-2']
        unique_dates = covid_test['Data wyk.'].unique()

        # # %%
        covid_results = defaultdict(list)
        for date in unique_dates:
            filtered = covid_test[covid_test['Data wyk.']==date]
            result = filtered[filtered['Wynik']=='Wynik badania']
            answer = result['Wartość'].values[0]
            if answer == 'dodatni':
                res = 1
            elif answer == 'ujemny':
                res = 0
            else:
                res = -1

            covid_results['Profil'].append('Koronawirus SARS-CoV-2')
            covid_results['Test'].append('SARS-CoV-2')
            covid_results['Data zlec.'].append(date)
            covid_results['Data wyk.'].append(date)
            covid_results['Nr zlecenia'].append(result['Nr zlecenia'].values[0])
            covid_results['Wynik'].append(answer)
            covid_results['Wartość'].append(res)
            covid_results['Norma'].append('0 - 0')
            covid_results['Jedn.'].append('Obecność')

        data = data.append(pd.DataFrame.from_dict(covid_results, orient='columns'))
        return data, name

# %%
if __name__ == "__main__":
    data = XLSParser.parse("data/pacjent nr 1 excel.xls")
    data