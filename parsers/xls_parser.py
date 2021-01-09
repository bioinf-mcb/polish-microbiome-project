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
        def _parse_covid_res(filtered):
            try:
                result = filtered[filtered['Wynik']=='Wynik badania']
                answer = result['Wartość'].values[0]
            except IndexError as e:
                result = filtered[filtered['Wynik']=='Wykrywanie materiału genetyczneg']
                answer = result['Wartość'].values[0]
                if "nie wykryto" in answer.lower():
                    answer = 'ujemny'
                elif "wykryto" in answer.lower():
                    answer = 'dodatni'
                elif "niejednoznaczny" in answer.lower():
                    answer = 'niejednoznaczny'
                else:
                    print(answer)
                    raise e

            
            return answer, result

        data = pd.read_html(fname)[0]
        name = data.columns[0][0]
        data.columns = data.columns.droplevel().droplevel()
        data = data.dropna()
        
        covid_test = data[data['Profil'] == 'Koronawirus SARS-CoV-2']
        unique_orders = covid_test['Nr zlecenia'].unique()

        # # %%
        covid_results = defaultdict(list)
        for order in unique_orders:
            filtered = data[data['Nr zlecenia']==order]
            answer, result = _parse_covid_res(filtered)
            order_date = result['Data zlec.'].values[0]
            exec_date = result['Data wyk.'].values[0]
            
            if answer == 'dodatni':
                res = 1
            elif answer == 'ujemny':
                res = 0
            else:
                res = -1

            try:
                additional = filtered[filtered['Wynik']=='Materiał diagnostyczny']
                material = additional['Wartość'].values[0]
            except IndexError as e:
                material = '-'

            covid_results['Profil'].append('SARS-CoV-2')
            covid_results['Test'].append(answer)
            covid_results['Data zlec.'].append(order_date)
            covid_results['Data wyk.'].append(exec_date)
            covid_results['Nr zlecenia'].append(order)
            covid_results['Wynik'].append(material)
            covid_results['Wartość'].append(res)
            covid_results['Norma'].append('0 - 0')
            covid_results['Jedn.'].append('Obecność')

        data = data[data["Nr zlecenia"].apply(lambda x: x not in unique_orders)]
        data = data.append(pd.DataFrame.from_dict(covid_results, orient='columns'), ignore_index=True).reset_index(drop=True)
        return data, name

# %%
if __name__ == "__main__":
    data, _ = XLSParser.parse("data/pacjent nr 10.xls")
    data