#%%
from parse_survey_to_agp import mapping, map_numerical
import pandas as pd

#%%
data_dict = pd.read_csv("data/survey_dictionary.csv")
template = pd.read_csv("data/template.csv")
data = pd.read_csv("data/data_patients.csv", sep=';')

def label_to_field(label):
    return data_dict[data_dict["Field Label"].str.lower()==label].iloc[0][0]

def split_mapping(text):
    res = {}
    for i in text.split("|"):
        spl = i.split(", ")
        num = spl[0]
        text = ", ".join(spl[1:])
        res[text.strip()] = num.strip()
    return res

def map_to_num(mapping):
    def _wrapper(text):
        text = str(text).strip()
        try:
            return mapping[text]
        except KeyError:
            return mapping[list(mapping.keys())[-1]]
    return _wrapper

#%%
new_cols = []
for column in data.columns:
    column = column.lower().strip()
    try:
        new_cols.append(label_to_field(column).lower())
    except IndexError:
        new_cols.append(column)

data.columns = new_cols

#%%
dropdowns = data_dict[data_dict["Field Type"]=="dropdown"]
for _, row in dropdowns.iterrows():
    try:
        dropdown_map = split_mapping(row["Choices, Calculations, OR Slider Labels"])
        data[row["Variable / Field Name"]] = data[row["Variable / Field Name"]].apply(map_to_num(dropdown_map))
    except KeyError:
        print("Skipping:", row["Variable / Field Name"])

#%%
template = {}
for col, mode in mapping.items():
    try:
        if type(mode) is str:
            template[col] = data[mode]
        elif type(mode) is list:
            template[col] = data[mode[0]].apply(mode[1])
        else:
            template[col] = data.apply(mode, axis=1)
        data[col] = template[col]
    except KeyError:
        data[col] = "Unspecified"
        print("Skipping", col)

# template.to_csv("data/template_filled.csv")
pd.DataFrame.from_dict(template).to_csv("data/survey_like_filled.csv")
# %%
mapping["bmi_corrected"]
# %%
