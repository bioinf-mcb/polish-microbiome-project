#%%
from .odt_parser import ODTParser
from os import stat
from striprtf import striprtf
from pprint import pprint
import re
from collections import deque
import pandas as pd
from datetime import datetime

# #%%
# ENCODING_TABLE = [
#     ("³", "ł"),
#     ("ê", "ę"),
#     ("¹", "ą"),
#     ("¿", "ż"),
#     ("\x9c", "ś"),
#     ("cæ", "ć")
# ]

# #%%
# with open("data/pacjent nr 1.rtf", "r", encoding='iso-8859-15') as f:
#     data = f.read()

# data = striprtf.rtf_to_text(data).split("\n")

# %%
class Parser:
    def __init__(self):
        self.results = []
        self.epicrisis = []
        self.last_line = ""
        self.parsing_mode = "REGULAR"
        self.date = ""
        self.group = "Albuminy"
        self.test = ""

    def parse_line(self, line):
        if "Nazwisko" in line or "PESEL" in line or "Pobyt" in line or "Adres" in line:
            return

        line = line.strip()
        self.date, line = self._set_date(line)

        if 'Zalecenia' in line:
            return
        if self.parsing_mode == "EPICRISIS" and line!='':
            self.epicrisis.append(line)
        if 'epikryza' in line.lower():
            self.parsing_mode = "EPICRISIS"
        if "ANTYBIOGRAM" in line:
            self.parsing_mode = "ANTYBIOGRAM"

        if self.parsing_mode == "REGULAR":
            if '|' not in line:
                self._parse_group_name(line)
                return

            if line[0] != "|": 
                self.last_line, line = line.split("|")[1], self.last_line+' : '+line
            if line[-1] == "|":
                self._parse_result(line)

        self.last_line = line

    def _set_date(self, line):
        date = self.date
        new_date = re.findall(".*\d{4}-\d{2}-\d{2}.*\|", line)

        if len(new_date)>0:
            date = new_date[0]
            date = re.findall("\d{4}-\d{2}-\d{2}", date)[0]
            
            # if len(self.last_line) > 0:
                # self.results[date].append(self.last_line)
            
            line = ' '.join(line.split()[1:])
        return date, line

    def _parse_group_name(self, line):
        pass

    def _parse_result(self, line):
        split_lines = line.split("|")
        for test in split_lines:
            if test == '':
                continue
            try:
                test_name = test.split()[0]
                test_norm = re.findall("\([^\)]*\)", test)
                if len(test_norm) > 0:
                    test_norm = test_norm[0]
                    parsed_test_norm = test_norm.rstrip(")").lstrip("(").split(" - ")
                    if parsed_test_norm[0] == '':
                        parsed_test_norm[0] = 0
                    if len(parsed_test_norm) == 1:
                        parsed_test_norm.append(parsed_test_norm[0])
                        test_norm = f"({parsed_test_norm[0]} - {parsed_test_norm[0]})"
                else:
                    test_norm = '(0 - 0)'

                value = test.split(" : ")[1].split(" ")[0]
                unit = test.split(" : ")[1].split(" ")[-1]
            except IndexError as e:
                print(line)
                print(test)
                raise e

            test_res = {}
            test_res["Data wyk."] = self.date
            test_res["Profil"] = test_name
            test_res["Wartość"] = value
            test_res["Norma"] = test_norm
            test_res["Jedn."] = unit
            test_res["Wynik"] = test_name
            test_res["Nr zlecenia"] = ''
            self.results.append(test_res)
# #%%
# parser = Parser()
# for line in data:
#     line = line.strip()
#     parser.parse_line(line)

# df = pd.DataFrame.from_dict(parser.results)

#%%
class RTFParser:
    ENCODING_TABLE = {
        "¹": "ą",
        "æ": "ć",
        "ê": "ę",
        "³": "ł",
        "ñ": "ń",
        "\x9c": "ś",
        "\x8c": "Ś",
        "\x8f": "ź",
        "¿": "ż",
        "¯": "Ż",
    }
    
    @staticmethod
    def to_text(fname):
        with open(fname, "r", encoding='iso-8859-15') as f:
            data = f.read()
        data = striprtf.rtf_to_text(data) 
        data = RTFParser._unicdecode(data)
        return data

    @staticmethod
    def _unicdecode(text):
        for key, sub in RTFParser.ENCODING_TABLE.items():
            text = text.replace(key, sub)
        return text

    @staticmethod
    def parse_epicrysis(fname):
        with open(fname, "r", encoding='iso-8859-15') as f:
            data = f.read()

        data = striprtf.rtf_to_text(data)
        # data = re.sub("<[^>]+>", "", data)
        data = data.split("\n")
        epicrysis_found = False
        epicrisis = []
        for line in data:
            line = line.strip()
            if epicrysis_found  and line!='':
                for key, sub in RTFParser.ENCODING_TABLE.items():
                    line = line.replace(key, sub)

                epicrisis.append(line)
            if 'epikryza' in line.lower():
                epicrysis_found = True

        epicrisis = " ".join(epicrisis)
        return epicrisis

    @staticmethod
    def parse_covid(fname):
        with open(fname, "r", encoding='iso-8859-15') as f:
            tmp = f.read()

        data = []
        tmp = striprtf.rtf_to_text(tmp).split("\n")
        for i in tmp:
            data.extend(i.split("|"))

        sars_found = False
        sars = []
        tmp = []
        previous = deque(maxlen=4)

        for line in data:
            line = line.strip()
            if 'SARS' in line:
                sars_found = True
                countdown = 4
                tmp.extend(previous)

            if sars_found and line!='':
                for key, sub in RTFParser.ENCODING_TABLE.items():
                    line = line.replace(key, sub)

                tmp.append(line)
                countdown -= max(line.count("|"), 1)
                if countdown <= 0:
                    sars_found = False
                    sars.append(tmp)
                    tmp = []

            previous.append(line)

        entries = {}
        for entry in sars:
            answer = None
            date_parsed = None
            for row in entry:
                if "nie wykryto" in row.lower():
                    answer = 'ujemny'
                elif "wykryto" in row.lower() or 'dodatni' in row.lower():
                    answer = 'dodatni'
                elif "niejednoznaczny" in row.lower():
                    answer = 'niejednoznaczny'

                date = row.split(" ")[0]
                try:
                    try:
                        date_parsed = datetime.strptime(date, "%Y-%m-%d")
                    except ValueError:
                        date_parsed = datetime.strptime(date, "%d-%m-%Y")
                except ValueError:
                    pass
            
            if answer is not None and date_parsed is not None:
                entries[date_parsed] = answer
        return entries

    @staticmethod
    def parse(fname):
        parser = Parser()
        with open(fname, "r", encoding='iso-8859-15') as f:
            data = f.read()
        data = striprtf.rtf_to_text(data).split("\n")

        for line in data:
            parser.parse_line(line)

        return pd.DataFrame.from_dict(parser.results)

    @staticmethod
    def parse_drugs(fname):
        data = RTFParser.to_text(fname)
        return ODTParser._extract_drugs(data)

    @staticmethod
    def parse_hospitalization_time(fname):
        data = RTFParser.to_text(fname)
        return ODTParser.parse_hospitalization_time(data)

    @staticmethod
    def parse_age(fname):
        data = RTFParser.to_text(fname)
        return ODTParser.parse_age(data)
        

# # %%
# RTFParser.parse_epicrysis("data/pacjent nr 1.rtf")

# %%
if __name__=="__main__":
    # print(RTFParser.parse_epicrysis("data/content.xml"))
    fname = '/storage/PawelLab/wwydmanski/NCBR-COVID/FTP_DATA/data/upload/pacjenci 201-250/Karty pobytu/Pacjent numer 226.rtf'
    print(RTFParser.parse_drugs(fname))