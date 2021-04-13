#%%
from striprtf import striprtf
from pprint import pprint
import re
from collections import defaultdict
import pandas as pd

#%%
ENCODING_TABLE = [
    ("³", "ł"),
    ("ê", "ę"),
    ("¹", "ą"),
    ("¿", "ż"),
    ("\x9c", "ś"),
    ("cæ", "ć")
]

#%%
with open("data/pacjent nr 1.rtf", "r", encoding='iso-8859-15') as f:
    data = f.read()

data = striprtf.rtf_to_text(data).split("\n")

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
        if 'Epikryza' in line:
            self.parsing_mode = "EPICRISIS"

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
                    test_norm = test_norm.rstrip(")").lstrip("(").split(" - ")
                    if test_norm[0] == '':
                        test_norm[0] = 0

                value = test.split(" : ")[1].split(" ")[0]
                unit = test.split(" : ")[1].split(" ")[-1]
            except IndexError as e:
                print(line)
                print(test)
                raise e

            test_res = {}
            test_res["Date"] = self.date
            test_res["Test name"] = test_name
            test_res["Value"] = value
            test_res["Norm"] = test_norm
            test_res["Unit"] = unit
            self.results.append(test_res)
#%%
parser = Parser()
for line in data:
    line = line.strip()
    parser.parse_line(line)

df = pd.DataFrame.from_dict(parser.results)

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
    def parse_epicrysis(fname):
        with open(fname, "r", encoding='iso-8859-15') as f:
            data = f.read()

        data = striprtf.rtf_to_text(data)
        data = re.sub("<[^>]+>", "", data)
        data = data.split("\n")
        print(data)
        epicrysis_found = False
        epicrisis = []
        for line in data:
            line = line.strip()
            if epicrysis_found  and line!='':
                for key, sub in RTFParser.ENCODING_TABLE.items():
                    line = line.replace(key, sub)

                epicrisis.append(line)
            if 'Epikryza' in line:
                epicrysis_found = True

        epicrisis = " ".join(epicrisis)
        return epicrisis

    @staticmethod
    def parse_covid(fname):
        with open(fname, "r", encoding='iso-8859-15') as f:
            data = f.read()

        data = striprtf.rtf_to_text(data).split("\n")

        sars_found = False
        sars = []
        for line in data:
            line = line.strip()
            if 'SARS' in line:
                sars_found = True

            if sars_found  and line!='':
                for key, sub in RTFParser.ENCODING_TABLE.items():
                    line = line.replace(key, sub)

                sars.append(line)

        # sars = " ".join(sars)
        return sars

# # %%
# RTFParser.parse_epicrysis("data/pacjent nr 1.rtf")

#%%
# RTFParser.parse_covid("data/pacjent nr 1.rtf")
# %%

if __name__=="__main__":
    print(RTFParser.parse_epicrysis("data/content.xml"))