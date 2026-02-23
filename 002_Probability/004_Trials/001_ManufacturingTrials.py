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

class ProductRecord :
    def __init__(
        self,
        product_id : str,
        is_defective : bool,
        weight_g : float,
        length_mm : float,
        batch_id : str,
        machine_id : str,
        timestamp
    ) :
        self.product_id = product_id
        self.is_defective = is_defective
        self.weight_g = weight_g
        self.length_mm = length_mm 
        self.batch_id = batch_id
        self.machine_id = machine_id
        self.timestamp = timestamp
        
class ManufacturingDataSet : 
    REQUIRED_COLUMNS = {
        "product_id",
        "is_defective",
        "weight_g",
        "length_mm",
        "batch_id",
        "machine_id",
        "timestamp"
    }
    
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.records : List[ProductRecord] = []
    
    def load(self) -> None :
        try :
            df = pd.read_excel(self.inFilePath)
        except Exception as exceptObject :
            raise DataLoadingError(f"Fatal Error! Failed to read the excel file : {exceptObject}\n")
        
        if not self.REQUIRED_COLUMNS.issubset(df.columns) :
            missingColumns = self.REQUIRED_COLUMNS - set(df.columns)
            raise DataLoadingError(f"Fatal Error! Missing the Required columns for analysis : {missingColumns}\n")
        
        for _, outRecord in df.iterrows() :
            productRecord = ProductRecord(
                product_id = str(outRecord["product_id"]),
                is_defective = bool(outRecord["is_defective"]),
                weight_g = float(outRecord["weight_g"]),
                length_mm = float(outRecord["length_mm"]),
                batch_id = str(outRecord["batch_id"]),
                machine_id = str(outRecord["machine_id"]),
                timestamp = outRecord["timestamp"]
            )
            self.records.append(productRecord)
            
    def getDefectProbability(self) -> float :
        if not self.records :
            raise DataLoadingError("Fatal Error! Loaded Data is empty...")
        
        defectCount = sum(1 for foundDefectProduct in self.records if foundDefectProduct.is_defective) 
        return defectCount / len(self.records)
    
    def getMachineWiseProbabilities(self) -> dict :
        productDataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        outStatistics = productDataFrame.groupby("machine_id")["is_defective"].mean().to_dict()
        return outStatistics
    
    def getBatchWiseStatistics(self) -> dict :
        productDataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        outStatistics = productDataFrame.groupby("batch_id")["is_defective"].mean().to_dict()
        return outStatistics
    
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
        
        self.inNumTrials =inNumTrials
        self.inTrial = inTrial
        self.trialResults : List[bool] = []
        
    def executeTrials(self) -> None :
        for _ in range(self.inNumTrials) :
            trialOutCome = self.inTrial.run()
            self.trialResults.append(trialOutCome)
    
    def generateSummary(self) -> dict :
        defectiveCounts = sum(self.trialResults)
        
        return {
            "totalTrials" : self.inNumTrials,
            "defectiveCount" : defectiveCounts,
            "nonDefectiveCounts" : self.inNumTrials - defectiveCounts,
            "estimatedDefectiveProbability" : defectiveCounts / self.inNumTrials
        }
        
class ManufacturingCharts :
    
    @staticmethod
    def plotMachineWiseDefects(machineWiseStats : dict) -> None :
        machines = list(machineWiseStats.keys())
        probabilities = list(machineWiseStats.values())
        
        plt.figure(figsize = (10,5))
        plt.bar(machines, probabilities)
        plt.title("Machine-wise Defect Probabilities")
        plt.xlabel("Machine ID")
        plt.ylabel("Defect Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def plotBatchWiseDefects(batchWiseStats : dict) -> None :
        batches = list(batchWiseStats.keys())
        probabilities = list(batchWiseStats.values())
        
        plt.figure(figsize = (10, 5))
        plt.bar(batches, probabilities, color = "orange")
        plt.title("Batch-Wise Defect Probabilities")
        plt.xlabel("Batch ID")
        plt.ylabel("Defect Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\004_Trials\DataSets\ManufacturingQuality.xlsx"
        manuFacturingData = ManufacturingDataSet(inFilePath)
        manuFacturingData.load()
        
        defectiveProbability = manuFacturingData.getDefectProbability()
        print(f"\nOverall Defect Probability is : {defectiveProbability : .4f}")
        
        machineProbability = manuFacturingData.getMachineWiseProbabilities()
        print(f"\nDisplaying Machine Wise Defect Probabilities...")
        outTable = [[outMachine, f"{outProbability : .4f}"] for outMachine, outProbability in machineProbability.items()]
        print(tabulate(outTable, headers = ["Machine ID", "Probability"], tablefmt = "pretty", stralign ="right"))        
            
        batchProbability = manuFacturingData.getBatchWiseStatistics()
        print(F"\nDisplaying Batch Wise Probabilities...")
        outTable = [[outBatch, f"{outProbability : .4f}"] for outBatch, outProbability in batchProbability.items()]
        print(tabulate(outTable, headers = ["Batch ID", "Probability"], tablefmt = "pretty", stralign ="right"))        

        trial = ProbabilityTrial(inProbability = defectiveProbability)
        runner = TrialRunner(inNumTrials = 5000, inTrial = trial)
        runner.executeTrials()
        
        summary = runner.generateSummary()
        print("\nSimulated Trial Summary ...")
        outTable = [[outKey, outValue] for outKey, outValue in summary.items()]
        print(tabulate(outTable, headers = ["Name", "Value"], tablefmt = "pretty", stralign ="left"))        

        ManufacturingCharts.plotMachineWiseDefects(machineProbability)
        ManufacturingCharts.plotBatchWiseDefects(batchProbability)
    except DataLoadingError :
        print("\nFatal Error! Encountered Issue While Loading The Data")
    except InvalidTrialError :
        print("\nFatal Error! Encountered Issue While Conducting The Trials")
    except Exception as exceptObject :
        print("\nFatal Error! Encountered Unexpected Error While Executing The Application...")
        print(f"Message From The Application : {exceptObject}")
        
if __name__ == "__main__":
    main()