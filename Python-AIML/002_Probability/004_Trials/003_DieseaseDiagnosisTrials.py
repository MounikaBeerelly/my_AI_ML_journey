import os
import pandas as pd
import matplotlib.pyplot as plt
import random
from typing import List
from tabulate import tabulate

class DataLoadingError(Exception) :
    pass

class InvalidTrialError(Exception) :
    pass

class PatientRecord :
    def __init__(
        self,
        patient_id : str,
        is_diagnosed : bool,
        age : int,
        blood_pressure : float,
        clinic_id : str,
        doctor_id : str,
        timestamp
    ) :
        self.patient_id = patient_id
        self.is_diagnosed = is_diagnosed
        self.age = age
        self.blood_pressure = blood_pressure
        self.clinic_id = clinic_id
        self.doctor_id = doctor_id
        self.timestamp = timestamp
        
class HealthDataSet : 
    REQUIRED_COLUMNS = {
        "patient_id",
        "is_diagnosed",
        "age",
        "blood_pressure",
        "clinic_id",
        "doctor_id",
        "timestamp"
    }
    
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.records : List[PatientRecord] = []
    
    def load(self) -> None :
        try :
            df = pd.read_excel(self.inFilePath)
        except Exception as exceptObject :
            raise DataLoadingError(f"Fatal Error! Failed to read the excel file : {exceptObject}\n")
        
        if not self.REQUIRED_COLUMNS.issubset(df.columns) :
            missingColumns = self.REQUIRED_COLUMNS - set(df.columns)
            raise DataLoadingError(f"Fatal Error! Missing the Required columns for analysis : {missingColumns}\n")
        
        for _, outRecord in df.iterrows() :
            patientRecord = PatientRecord(
                patient_id = str(outRecord["patient_id"]),
                is_diagnosed = bool(outRecord["is_diagnosed"]),
                age = int(outRecord["age"]),
                blood_pressure = float(outRecord["blood_pressure"]),
                clinic_id = str(outRecord["clinic_id"]),
                doctor_id = str(outRecord["doctor_id"]),
                timestamp = outRecord["timestamp"]
            )
            self.records.append(patientRecord)
            
    def getDiagnosedProbability(self) -> float :
        if not self.records :
            raise DataLoadingError("Fatal Error! Network Dataset is empty...")
        
        diagnosedCount = sum(1 for outRecord in self.records if outRecord.is_diagnosed) 
        return diagnosedCount / len(self.records)
    
    def getClinicWiseProbabilities(self) -> dict :
        dataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        return dataFrame.groupby("clinic_id")["is_diagnosed"].mean().to_dict()
    
    def getDoctorWiseProbabilities(self) -> dict :
        dataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        return dataFrame.groupby("doctor_id")["is_diagnosed"].mean().to_dict()
    
    
class ProbabilityTrial :
    def __init__(self, inProbability : float):
        if not (0 <= inProbability <= 1) :
            raise InvalidTrialError("Fatal Error! Probability must be in between 0 and 1")
        self.inProbability = inProbability
        
    def run(self) -> bool :
        return random.random() < self.inProbability
    
class TrialRunner :
    def __init__(self, inNumTrials : int, inTrial : ProbabilityTrial):
        if inNumTrials <= 0 :
            raise InvalidTrialError("Fatal Error! The input for number of trials must be positive")
        
        self.inNumTrials = inNumTrials
        self.inTrial = inTrial
        self.trialResults : List[bool] = []
        
    def executeTrials(self) -> None :
        for _ in range(self.inNumTrials) :
            trialOutCome = self.inTrial.run()
            self.trialResults.append(trialOutCome)
    
    def generateSummary(self) -> dict :
        diagnosedCount = sum(self.trialResults)
        
        return {
            "totalTrials" : self.inNumTrials,
            "diagnosedCount" : diagnosedCount,
            "nonDiagnosedCount" : self.inNumTrials - diagnosedCount,
            "estimatedDiagnosedProbability" : diagnosedCount / self.inNumTrials
        }
        
class HealthRecordCharts :
    
    @staticmethod
    def plotClinicWiseIntrusions(clinicWiseStats : dict) -> None :
        clinics = list(clinicWiseStats.keys())
        probabilities = list(clinicWiseStats.values())
        
        plt.figure(figsize = (10,5))
        plt.bar(clinics, probabilities)
        plt.title("clinic-wise Diagnosed Probabilities")
        plt.xlabel("clinic ID")
        plt.ylabel("Diagnosed Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def plotDoctorWiseIntrusions(doctorWiseStats : dict) -> None :
        doctors = list(doctorWiseStats.keys())
        probabilities = list(doctorWiseStats.values())
        
        plt.figure(figsize = (10, 5))
        plt.bar(doctors, probabilities, color = "orange")
        plt.title("Doctor-Wise Diagnosed Probabilities")
        plt.xlabel("Doctor ID")
        plt.ylabel("Diagnosed Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\004_Trials\DataSets\DiseaseDiagnosis.xlsx"
        healthData = HealthDataSet(inFilePath)
        healthData.load()
        
        diagnosedProbability = healthData.getDiagnosedProbability()
        print(f"\nOverall Diagnosed Probability is : {diagnosedProbability : .4f}")
        
        clinicProbability = healthData.getClinicWiseProbabilities()
        print(f"\nDisplaying Clinic-Wise Diagnosed Probabilities...")
        outTable = [[outServer, f"{outProbability : .4f}"] for outServer, outProbability in clinicProbability.items()]
        print(tabulate(outTable, headers = ["Clinic ID", "Probability"], tablefmt = "pretty", stralign ="right"))        
            
        doctorProbability = healthData.getDoctorWiseProbabilities()
        print(f"\nDisplaying Doctor-Wise Diagnosed Probabilities...")
        outTable = [[outProtocol, f"{outProbability : .4f}"] for outProtocol, outProbability in doctorProbability.items()]
        print(tabulate(outTable, headers = ["Doctor ID", "Probability"], tablefmt = "pretty", stralign ="right"))        
        
        trial = ProbabilityTrial(inProbability = diagnosedProbability)
        runner = TrialRunner(inNumTrials = 5000, inTrial = trial)
        runner.executeTrials()
        
        summary = runner.generateSummary()
        print("\nSimulated Trial Summary ...")
        outTable = [[outTrialKey, outValue] for outTrialKey, outValue in summary.items()]
        print(tabulate(outTable, headers = ["Name", "Value"], tablefmt = "pretty", stralign ="left"))        

        HealthRecordCharts.plotClinicWiseIntrusions(clinicProbability)
        HealthRecordCharts.plotDoctorWiseIntrusions(doctorProbability)
    except DataLoadingError as dataLoadingError :
        print(f"\nFatal Error! Encountered Issue While Loading The Data : {dataLoadingError}")
    except InvalidTrialError as invalidTrialError :
        print("\nFatal Error! Encountered Issue While Conducting The Trials: {invalidTrialError}")
    except Exception as exceptObject :
        print("\nFatal Error! Encountered Unexpected Error While Executing The Application...")
        print(f"Message From The Application : {exceptObject}")
        
if __name__ == "__main__":
    main()