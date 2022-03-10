#%%
from datetime import datetime
import pandas as pd
import pgeocode

# %%
def corrected_wrapper(func, range):
    # 9.6 - 79
    def _wrap(x):
        res = func(x)
        try:
            if res<range[0] or res>range[1]:
                return 'Unspecified'
        except TypeError:
            return res
        return res
    return _wrap    

def parse_age(row):
    try:
        timestamp = row['ankieta_dla_uczestnika_badania_timestamp']
    except KeyError:
        timestamp = datetime.now().strftime("%Y-%M-%d %H:%m:%S")
    birth_year = row['birth_year']
    try:
        return datetime.strptime(timestamp, "%Y-%M-%d %H:%m:%S").year - birth_year
    except ValueError:
        pass
    return None

def age_cat(age):
    if pd.isna(age):
        return "Unspecified"
    elif age>=20:
        return str(int(age//10*10))+"s"
    elif age>=13:
        return "teen"
    elif age>=4:
        return "child"
    else:
        return "baby"

def map_numerical(labels, nan_value="Not applicable", offset=-1):
    def _wrapper(value):
        try:
            return labels[int(value)+offset]
        except:
            return nan_value
    return _wrapper

def try_parse(type):
    def _wrapper(value):
        try:
            return type(value)
        except ValueError:
            return "Unspecified"
    return _wrapper

def get_bmi(row):
    try:
        bmi = row['weight_kg']/((row['height_cm']/100)**2)
        return round(bmi, 3)
    except (ZeroDivisionError, TypeError):
        return "Unspecified"

def get_bmi_cat(row):
    try:
        bmi = int(get_bmi(row))
    except ValueError:
        return "Unspecified"

    if bmi < 14 or bmi > 41:
        return "Unspecified"

    if bmi<18.5:
        return "underweight"
    elif bmi<=24.9:
        return "normal"
    elif bmi <= 29.9:
        return "overweight"
    elif bmi <= 41:
        return "obese"


class LatLonParser:
    IDENTIFIER_COL = "patient_id"
    NOMI = pgeocode.Nominatim('pl')

    def __init__(self):
        self.cache = {}

    def get_lat(self, row):
        try:
            zipc = str(int(row['zip_code']))
            zipc = f"{zipc[:2]}-{zipc[2:]}01"
        except ValueError:
            return "Unspecified"
        if row[LatLonParser.IDENTIFIER_COL] not in self.cache.keys():
            self.cache[row[LatLonParser.IDENTIFIER_COL]] = LatLonParser.NOMI.query_postal_code(zipc)[['latitude', 'longitude']]
        return self.cache[row[LatLonParser.IDENTIFIER_COL]]['latitude']
    
    def get_lon(self, row):
        try:
            zipc = str(int(row['zip_code']))
            zipc = f"{zipc[:2]}-{zipc[2:]}01"
        except ValueError:
            return "Unspecified"

        if row[LatLonParser.IDENTIFIER_COL] not in self.cache.keys():
            self.cache[row[LatLonParser.IDENTIFIER_COL]] = LatLonParser.NOMI.query_postal_code(zipc)[['latitude', 'longitude']]
        return self.cache[row[LatLonParser.IDENTIFIER_COL]]['longitude']

def get_alcohol(x):
    freq = try_parse(int)(x)
    if freq==5:
        return "No"
    elif freq != "Unspecified":
        return "Yes"
    
    return "Unspecified"

def get_cancer_treatment(row):
    if row["cancer_treatment___2"]==1:
        return "Chemotherapy"
    if row["cancer_treatment___1"]==1:
        return "Radiation therapy"
    if row["cancer_treatment___3"]==1:
        return "Surgery only"
    if row["cancer_treatment___4"]==1:
        return "No treatment"
    return "Unspecified"

def get_contraceptives(row):
    if row["contraceptives"]==2:
        return "No"
    elif row["contraceptives"]==0:
        return "Not applicable"
    
    wrap = map_numerical(['Yes, I am taking the "pill"', 
                            'Yes, I use a contraceptive patch (Ortho-Evra)', 
                            'Yes, I use a hormonal IUD (Mirena)', 
                            'Yes, I use the NuvaRing',
                            'Yes, I use an injected contraceptive (DMPA)',
                            'Yes, I use an injected contraceptive (DMPA)'], offset=0)
    return wrap(row["contraceptive_type"])

lat_lon_parser = LatLonParser()

mapping = {
    "patient_id": ["patient_id", try_parse(int)],
    "age": parse_age,
    "age_cat": ["age", age_cat],
    "age_years": ["age", try_parse(int)],
    "age_corrected": ["age_years", corrected_wrapper(try_parse(int), [0, 101])],
    "sex": ["gender", map_numerical(["female", "male", "other"])],
    "pregnant": ["pregnant", map_numerical(["Yes", "No", "Unspecified"])],
    "race": ["race", map_numerical(["Caucasian", "African American", "Hispanic", "Asian or Pacific Islander", "Other", "Other"], "Unspecified")],
    "weight_kg": ["weight_kg", try_parse(int)],
    "weight_units": lambda x: "kg",
    "height_cm": ["height_cm", try_parse(int)],
    "height_units": lambda x: "cm",
    "bmi": get_bmi,
    "bmi_corrected": corrected_wrapper(get_bmi, [9.6, 79]),
    "bmi_cat": get_bmi_cat,
    "latitude": lat_lon_parser.get_lat,
    "longitude": lat_lon_parser.get_lon,
    "country": lambda x: "PL",
    "geo_loc_name": lambda x: "PL",
    "country_residence": lambda x: "PL",
    "level_of_education": ["level_of_education", map_numerical(["Did not complete high school", "High School or GED equilivant", "Some college or technical school"])],
    "smoking_frequency":  ["smoking_frequency", map_numerical(["Daily", "Regulary (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"])],
    "alcohol_consumption": ["alkohol_frequency", get_alcohol],
    "alcohol_frequency": ["alkohol_frequency", map_numerical(["Daily", "Regulary (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"])],
    "alcohol_types_beercider": ["alcohol_types___1", map_numerical(["No", "Yes"], offset=0)],
    "alcohol_types_white_wine": ["alcohol_types___2", map_numerical(["No", "Yes"], offset=0)],
    "alcohol_types_red_wine": ["alcohol_types___3", map_numerical(["No", "Yes"], offset=0)],
    "alcohol_types_spiritshard_alcohol": lambda x: "Yes" if any(x[f"alcohol_types___{i}"] for i in range(4, 9)) else "No",
    "lung_disease": ["asthma", map_numerical(["Diagnosed by a medical professional (doctor, physician assistant)", "I do not have this condition", "Self-diagnosed"])],
    "diabetes": ["diabetes", map_numerical(["Diagnosed by a medical professional (doctor, physician assistant)", "I do not have this condition", "Self-diagnosed"], "Unspecified")],
    "diabetes_type": ["diabetes_type", map_numerical(["Type I diabetes", "Type II diabetes"])],
    "cardiovascular_disease": ["cardiovascular_disease", map_numerical(["Diagnosed by a medical professional (doctor, physician assistant)", "I do not have this condition", "Self-diagnosed"], "Unspecified")],
    "ibd": ["ibd", map_numerical(["Diagnosed by a medical professional (doctor, physician assistant)", "I do not have this condition", "Self-diagnosed"], "Unspecified")],
    "ibd_diagnosis": ["ibd_diagnosis", map_numerical(["Ulcerative Colitis", "Crohn's Disease", "Unspecified"])],
    "cancer": ["cancer", map_numerical(["Diagnosed by a medical professional (doctor, physician assistant)", "I do not have this condition", "Self-diagnosed"], "Unspecified")],
    "cancer_treatment": get_cancer_treatment,
    "antibiotic_history": ["antibiotics_before_hospital", map_numerical(["Week", "Week", "Month", "6 months", "6 months", "Year", "I have not taken antibiotics in the past year."], "Unspecified")],
    "subset_antibiotic_history": ["antibiotics_before_hospital", map_numerical(["No"]*6 + ["Yes"], "Unspecified")],
    "allergic_to_i_have_no_food_allergies_that_i_know_of": ["allergies", map_numerical(["No", "Yes", "No"], "Unspecified")], #FINISH ALLERGIES LATER
    "allergic_to_other": ["allergic_to___4", map_numerical(["No", "Yes"], offset=0)],
    "allergic_to_peanuts": ["allergic_to___1", map_numerical(["No", "Yes"], offset=0)],
    "allergic_to_tree_nuts": ["allergic_to___2", map_numerical(["No", "Yes"], offset=0)],
    "allergic_to_shellfish": ["allergic_to___3", map_numerical(["No", "Yes"], offset=0)],
    "allergic_to_unspecified": ["allergies", map_numerical(["No", "No", "No"], nan_value="Yes")],
    "exercise_frequency": ["exercise_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "seasonal_allergies": ["seasonal_allergies", map_numerical(["Yes", "No"])],
    "non_food_allergies_beestings": ["non_food_allergies___3", map_numerical(["No", "Yes"], offset=0)],
    "non_food_allergies_drug_eg_penicillin": ["non_food_allergies___1", map_numerical(["No", "Yes"], offset=0)],
    "non_food_allergies_pet_dander": ["non_food_allergies___2", map_numerical(["No", "Yes"], offset=0)],
    "non_food_allergies_poison_ivyoak": ["non_food_allergies___5", map_numerical(["No", "Yes"], offset=0)],
    "non_food_allergies_sun": ["non_food_allergies___6", map_numerical(["No", "Yes"], offset=0)],
    "non_food_allergies_unspecified": ["allergies", map_numerical(["No", "No", "No"], nan_value="Yes")],
    "diet_type": ["diet_type", map_numerical(["Omnivore", "Omnivore but do not eat red meat", "Vegan", "Vegetarian", "Vegetarian but eat seafood"], "Unspecified")],
    "lactose": ["lactose", map_numerical(["Yes", "No"], "Unspecified")],
    "gluten": ["gluten", map_numerical([ "I was diagnosed with celiac disease", "I was diagnosed with gluten allergy (anti-gluten IgG), but not celiac disease", "No"])],
    "fruit_frequency": ["fruit_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "vegetable_frequency": ["vegetable_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "red_meat_frequency": ["red_meat_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "fermented_plant_frequency": ["fermented_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "sugar_sweetened_drink_frequency": ["sugar_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "sugary_sweets_frequency": ["sugar_frequency", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    "artificial_sweeteners": ["artificial_sweeteners", map_numerical(["Daily", "Regularly (3-5 times/week)", "Occasionally (1-2 times/week)", "Rarely (a few times/month)", "Never"], "Unspecified")],
    #TODO: Finish supplements
    "contraceptive": get_contraceptives,
}

# %%

if __name__=="__main__":

    template = pd.read_csv("data/template.csv")
    # data = pd.read_csv("data/data_patients.csv", sep=';')
    data = pd.read_csv("data/survey_like_filled.csv")


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
            print("Error!", col)
    template.to_csv("data/template_filled.csv")
