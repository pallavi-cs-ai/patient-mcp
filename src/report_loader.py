import json

def load_patient_data(path):
    with open(path) as f:
        return json.load(f)