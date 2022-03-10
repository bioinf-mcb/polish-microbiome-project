from utils.resolve_files import PatientResolver, ROOT_DIR
from utils.parsers import RTFParser, ODTParser, ParserRouter
from tqdm import trange
import glob
import pandas as pd

print("Files presence")
missing_lab = []
missing_history = []
missing_epicrisis = []
missing_metadata = set(list(range(1,311)))

def collapse_sequence(sequence):
    res = []
    consecutive = [None, None]
    previous = 0

    for i in [*sequence, -1]:
        if consecutive[0] is None:
            consecutive[0] = i
        elif i == previous + 1:
            consecutive[1] = i
        elif i - previous != 1:
            if consecutive[1] is not None:
                if consecutive[1] - consecutive[0] > 2:
                    res.append(f"{consecutive[0]} - {consecutive[1]}")
                else:
                    res.extend(list(range(consecutive[0], consecutive[1]+1)))
            else:
                res.extend([previous, i])
            consecutive = [i, None]
        previous = i
    return res

resolver = PatientResolver()
for i in trange(1, 311):
    lab, history = resolver.get_files(i)
    if lab is None:
        missing_lab.append(i)
    if history is None:
        missing_history.append(i)
        missing_epicrisis.append(i)
    else:
        text = ParserRouter.route(history).parse_epicrysis(history)
        if text == '':
            missing_epicrisis.append(i)

for fname in glob.glob(f"{ROOT_DIR}/*/zestawienie*.xlsx"):
    patient_df = pd.read_excel(fname)
    for _, row in patient_df.iterrows():
        i = int(row['Numer pacjenta '])
        missing_metadata.remove(i)

print("Missing lab results:")
print(collapse_sequence(list(missing_lab)))
print()
print("Missing patient history file")
print(missing_history)
print()
print("Missing medical history report")
print(missing_epicrisis)
print()
print("Missing metadata file")
print(collapse_sequence(list(missing_metadata)))