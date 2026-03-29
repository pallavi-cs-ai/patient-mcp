from report_loader import load_patient_data
from analysis import analyze_thyroid

def main():
    data = load_patient_data("../data/patient_data.json")
    result = analyze_thyroid(data)
    
    print("Analysis Result:")
    print(result)

if __name__ == "__main__":
    main()