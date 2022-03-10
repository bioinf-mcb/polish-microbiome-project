from os import stat
import re
import zipfile
import glob
from datetime import datetime
from collections import deque

from bleach import clean

class ODTParser:
    @staticmethod
    def parse_hospitalization_time(fname):
        try:
            with zipfile.ZipFile(fname, 'r') as zip_ref:
                text = zip_ref.read("content.xml").decode("utf-8")
        except OSError:
            text = fname

        duration = next(re.finditer("Pobyt w(?:<text:s/>|\s)Klinice od(?:.*?)([\d\.]{10})(?:.*?)([\d\.]{10})", text))
        duration_start = datetime.strptime(duration.group(1), "%d.%m.%Y").date()
        duration_end = datetime.strptime(duration.group(2), "%d.%m.%Y").date()
        return duration_start, duration_end

    @staticmethod
    def parse_drugs(fname):
        with zipfile.ZipFile(fname, 'r') as zip_ref:
            content = zip_ref.read("content.xml").decode("utf-8")

        return ODTParser._extract_drugs(content)

    @staticmethod
    def parse_covid(fname):
        # with zipfile.ZipFile(fname, 'r') as zip_ref:
        #     content = zip_ref.read("content.xml").decode("utf-8")
        # cleanr = re.compile('<.*?>')
        # clean_text = re.sub(cleanr, '|', content)
        # clean_text = re.sub('\|+', '|', clean_text)

        # data = []
        # tmp = clean_text.split("\n")
        # for i in tmp:
        #     data.extend(i.split("|"))
        raise NotImplementedError

    @staticmethod
    def _extract_drugs(text):
        with open("tmp/extracted.txt", "w") as f:
            f.write(text)
        
        duration = next(re.finditer("Pobyt w(?:<text:s/>|\s)Klinice od(?:.*?)([\d\.]{10})(?:.*?)([\d\.]{10})", text))
        duration_end = datetime.strptime(duration.group(2), "%d.%m.%Y").date()
         
        with open("utils/Antibiotic.csv", "r") as f:
            antibiotics = f.readlines()

        antibiotics = [i.strip().lower() for i in antibiotics]

        taken_medicines = {
            "drug_name": [],
            "drug_start_date": [],
            "drug_end_date": [],
            "is_antibiotic": [],
        }

        for med in re.finditer("Nazwa międzynaro.:(.+?)(?=Dawkowanie)", text):
            med_name = med.group(1).replace("<text:s/>", "").strip().replace('<text:s text:c="2"/>', '')
            period = next(re.finditer("Okres(?:.*?)podawania(?:.*?)od:(\S+?) (?:[\d:\s]*?) do:(\S+?) ", text[med.start():]))

            start = datetime.strptime(period.group(1), "%Y-%m-%d").date()
            try:
                end = datetime.strptime(period.group(2), "%Y-%m-%d").date()
            except ValueError:
                end = duration_end

            is_anti = "1" if med_name.lower() in antibiotics else "0"

            taken_medicines["drug_name"].append(med_name)
            taken_medicines["drug_start_date"].append(start)
            taken_medicines["drug_end_date"].append(end)
            taken_medicines["is_antibiotic"].append(is_anti)

        return taken_medicines

    @staticmethod
    def parse_epicrysis(fname):
        try:
            with zipfile.ZipFile(fname, 'r') as zip_ref:
                content = zip_ref.read("content.xml").decode("utf-8")
        except OSError:
            content = fname

        cleanr = re.compile('<.*?>')
        clean_text = re.sub(cleanr, '', content)
        for sample in ["Epikryza", "EPIKRYZA", "epikryza"]:
            if sample in clean_text:
                return clean_text.partition(sample)[-1]
        return ''

    @staticmethod
    def to_text(fname):
        try:
            with zipfile.ZipFile(fname, 'r') as zip_ref:
                content = zip_ref.read("content.xml").decode("utf-8")
        except OSError:
            content = fname

        cleanr = re.compile('<.*?>')
        clean_text = re.sub(cleanr, '', content)
        return clean_text

    @staticmethod
    def parse_age(fname):
        epicrisis = ODTParser.parse_epicrysis(fname)
        try:
            age = next(re.finditer("(\d{1,3})\s*-?\s*letni", epicrisis))
        except StopIteration:
            age = next(re.finditer("lat (\d{1,3})", epicrisis))
        age = age.group(1)
        return age