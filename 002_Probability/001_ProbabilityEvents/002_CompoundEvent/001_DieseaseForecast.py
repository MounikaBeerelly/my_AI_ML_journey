import pandas as pd
import matplotlib.pyplot as plt

class PatientRecord :
    def __init__(self, inPatientID, inAge, inBMI, inSmoker, inHasDiesease) :
        self.inPatientID = inPatientID
        self.inAge = inAge
        self.inBMI = inBMI
        self.inSmoker = inSmoker
        self.inHasDiesease = inHasDiesease
        
class DieseaseProbabilityAnalyzer :
    def __init__(self) :
        self.patients = []
        
    # Adding patients
    def addPatients(self, inPatient) :
        self.patients.append(inPatient)
        
    def calculateProbabilities(self) :
        # This method calculates the compound probabilities for disease events
        
        # vars() function returns __dict__ attribute of an object i.e. it returns a dictionary of all the object attributes as name-value pairs
        df = pd.DataFrame([vars(outPatient) for outPatient in self.patients])
        
        """Logic to mark the required conditions to recognize higher BMI values and he is a smoker"""
        df["IsHighBMI"] = df["inBMI"] > 30
        df["IsSmoker"] = df["inSmoker"] == "Yes" 
        
        totalPatients = len(df)
        
        """Calculating the base probabilities for each required event"""
        pDiesease = len(df[df["inHasDiesease"] == "Yes"]) / totalPatients
        pHighBMI = len(df[df["IsHighBMI"] == "True"]) / totalPatients
        pIsSmoker = len(df[df["IsSmoker"] == "True"]) / totalPatients

        """Calculating the compound event probabilities: High BMI and also smoker"""
        dfCompound = df[(df["IsHighBMI"]) & (df["IsSmoker"])]
        pCompound = len(dfCompound) / totalPatients
        
        """Calculating the conditional probability for : diesease | (HighBMI ∩ Smoker)"""
        if len(dfCompound) > 0 :
            pDieseaseGivenCompound = len(dfCompound[dfCompound["inHasDiesease"] == "Yes"]) / len(dfCompound)
        else :
            pDieseaseGivenCompound = 0.0
            
        return {
            "P(Diesease)" : round(pDiesease, 4),
            "P(HighBMI)" : round(pHighBMI, 4),
            "P(Smoker)" : round(pIsSmoker, 4),
            "P(HighBMI ∩ Smoker)" : round(pCompound, 4),
            "P(Diesease | HighBMI ∩ Smoker)" : round(pDieseaseGivenCompound, 4)
        }        
        
def resultsVisualizer(inProbabilities) :
    """function to visualize the compound probability trends across years"""
    df = pd.DataFrame(inProbabilities).T.reset_index()
    df.columns= ["Year", "P(Diesease)", "P(HighBMI)", "P(Smoker)", "P(HighBMI ∩ Smoker)", "P(Diesease | HighBMI ∩ Smoker)"]

    plt.figure(figsize = (10, 6)) 
    plt.plot(df["Year"], df["P(Diesease | HighBMI ∩ Smoker)"], marker = "o", label = "P(Diesease | HighBMI ∩ Smoker)", color = "red")
    plt.plot(df["Year"], df["P(Diesease)"], marker = "o", label = "P(diesease)", color = "blue")
    plt.title("Compound Event Probability Trend : Diesease | (HighBMI ∩ Smoker)")
    plt.xlabel("Year")
    plt.ylabel("Probability")
    plt.legend()
    plt.grid(True)
    plt.show()
    
def processSheet(inDataFrame) :
    analyzer = DieseaseProbabilityAnalyzer()
    
    for _, outData in inDataFrame.iterrows() :
        outPatient = PatientRecord(outData["PatientID"], outData["Age"], outData["BMI"], outData["Smoker"], outData["HasDisease"])
        analyzer.addPatients(outPatient)
        
    return analyzer.calculateProbabilities()

def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\002_CompoundEvent\DataSets\HealthPatientData.xlsx"
        excelFile = pd.ExcelFile(inFilePath)
    except FileNotFoundError as fileNotFoundError :
        print(f"\nFatal Error! Excel file not foundm please ensure : {fileNotFoundError} exists in the specified path")
        return
    
    allYearProbabilities = {}
    
    for outSheetName in excelFile.sheet_names :
        print(f"Processing year sheet : {outSheetName}")
        sheetDataFrame = pd.read_excel(excelFile, sheet_name = outSheetName)
        yearProbabilities = processSheet(sheetDataFrame)
        allYearProbabilities[outSheetName] = yearProbabilities
        
    resultsVisualizer(allYearProbabilities)
    
if __name__ == "__main__":
    main()