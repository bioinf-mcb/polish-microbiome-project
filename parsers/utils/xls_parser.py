#%%
import pandas as pd
from collections import defaultdict
import datetime

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
    def open_file(fname):
        try:
            data = pd.read_html(fname)[0]
            data.columns = data.columns.droplevel().droplevel()
        except ValueError:
            data = pd.ExcelFile(fname).parse(0)
            data.columns = data.iloc[9]
            data = data.drop(9, axis=0)
            # data = data.dropna()
        return data

    @staticmethod
    def parse(fname):
        def fix_excel_date_conversion(date):
            # The date can be misinterpreted in two ways:
            # a) 12.39 -> {month}.{year} -> 01.12.1939
            # b) 2.7 -> {day}.{month} -> 02.07.[current year]
            res = date["Wartość"]
            if type(res) is datetime.datetime:
                # a)
                if res.year != datetime.datetime.now().year and res.day == 1:
                    res = float(f"{res.month}.{str(res.year)[-2:]}")
                # b)
                else:
                    res = float(f"{res.day}.{res.month}")
                print(date["Data wyk."], date["Wynik"], res)
            return res

        def _parse_covid_res(filtered):
            try:
                result = filtered[filtered['Wynik']=='Wynik badania']
                answer = result['Wartość'].values[0]
            except IndexError as e:
                for potential_descr in ['Wykrywanie materiału genetyczneg', 'Materiał genetyczny SARS CoV-2']:
                    result = filtered[filtered['Wynik']==potential_descr]
                    if len(result) > 0:
                        break
                    
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

        try:
            data = pd.read_html(fname)[0]
            # name = data.columns[0][0]
            data.columns = data.columns.droplevel().droplevel()
        except ValueError:
            data = pd.ExcelFile(fname).parse(0)
            if '.xls' in fname:
                data.columns = data.iloc[9]
                data = data.drop(9, axis=0)
            elif '.ods' in fname:
                data.columns = data.iloc[5]
                data = data.drop(5, axis=0)

            data = data.rename(columns={'Wyniki': 'Wynik', 'Data zlecenia': 'Data zlec.'})
            try:
                data = data.drop(9, axis=0)
            except KeyError:
                pass
            data = data.dropna()
            # data["Wartość"] = data.apply(fix_excel_date_conversion, axis=1)

        # print(data)
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
        return data

# %%
if __name__ == "__main__":
    data = XLSParser.parse("data/Pacjenci 70-100 XLS/Pacjent numer 85.xls")
    print(data)