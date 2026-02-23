import os
import pandas as pd
import matplotlib.pyplot as plt

class DataFileNotFoundError(Exception) :
    pass

class InvalidFileFormatError(Exception) :
    pass

class DataNotLoadedError(Exception) :
    pass

class EmptyDataSetError(Exception) :
    pass

class MissingColumnError(Exception) :
    pass

class HealthCareEVCalculator :
    requiredColumns = [
        "Case ID",
        "Case Type",
        "Severity Level",
        "Probability",
        "Resource Cost (USD)",
        "Treatment Time (Minutes)",
        "ICU Required"
    ]
    
    severityMapping = {
        "Mild" : 1,
        "Moderate" : 2,
        "Severe" : 3,
        "Critical" : 4
    }
    
    def __init__(self, inFilePath):
        self.inFilePath = inFilePath
        self.data = None
        
    def validateDataFile(self) :
        try :
            if not os.path.exists(self.inFilePath) :
                raise DataFileNotFoundError(
                    f"\nFatal Error! Dataset file not found : {self.inFilePath}\n"
                )
                
            if not self.inFilePath.endswith(".xlsx") :
                raise InvalidFileFormatError (
                    "\nFatal Error! Only .xlsx files are accepted\n"
                )
            
        except Exception as exceptObject :
            print(f"\nFatal Error! File validation failed : {exceptObject}\n")
            raise
        
    def validateRequiredColumns(self) :
        missingColumns = [
            outColumn for outColumn in self.requiredColumns if outColumn not in self.data.columns
        ]
        if missingColumns :
            raise MissingColumnError(
                f"\nFatal Error! Missing required columns : {missingColumns}\n"
            )
            
    def loadData(self) :
        try :
            self.validateDataFile()
            self.data = pd.read_excel(self.inFilePath)
            
            if self.data.empty :
                raise EmptyDataSetError("\nFatal Error! Dataset loaded is Empty\n")
            
            self.validateRequiredColumns()
            
            print(f"\nDataset loaded successfully from : {self.inFilePath}\n")
        except Exception as exceptObject :
            print(f"\nFatal Error! Error in loading dataset : {exceptObject}")
            raise
        
    def calculatedExpectedValue(self) :
        try:
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Data not loaded : Cannot compute Expected value\n"
                )
            self.data["Severity Weight"] = self.data["Severity Level"].map(self.severityMapping)
            self.data["Expected Resource Cost"] = self.data["Resource Cost (USD)"] * self.data["Probability"]
            self.data["Expected Treatment Time"] = self.data["Treatment Time (Minutes)"] * self.data["Probability"]
            self.data["Weighted Risk Contribution"] = self.data["Probability"] * self.data["Severity Weight"]
            
            totalExpectedValue = self.data["Expected Resource Cost"].sum()
            return totalExpectedValue
        except Exception as exceptObject :
            print(f"\nFatal Error! Error in computing Expected value : {exceptObject}\n")
            raise
    
    def addHelperColumns(self) :
        try :
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Dataset Not loaded : cannot add Helper Columns\n"
                )
                
            self.data["Severity Weight"] = self.data["Severity Level"].map(self.severityMapping)
            self.data["Risk Score"] = self.data["Probability"] * self.data["Severity Weight"]
            
            print(f"\nICU load factor (adds 40% additional resource cost)")
            self.data["ICU Load Factor"] = self.data["ICU Required"].apply(lambda x : 1.4 if x == "Yes" else 1.0)
            self.data["Adjusted Resource Cost"] = self.data["Resource Cost (USD)"] * self.data["ICU Load Factor"]
            self.data["Time Efficiency Score"] = self.data["Resource Cost (USD)"] / self.data["Treatment Time (Minutes)"]
            self.data["Criticality Index"] = self.data["Severity Weight"] * self.data["Treatment Time (Minutes)"]
            self.data["Case Priority Rank"] = self.data["Criticality Index"].rank(ascending=False)
        except Exception as exceptObject :
            print(f"\nFatal Error! Error adding Helper Columns : {exceptObject}\n")
            raise
        
    def generateSummaryReport(self) :
        try :
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Dataset not loaded : cannot generate summary\n"
                )
                
            print(f"----------------Business Intellisence summary------------")
            print("\nCases by Severity...")
            print(self.data["Severity Level"].value_counts(), "\n")
            print("ICU Requirement distribution...")
            print(self.data["ICU Required"].value_counts(), "\n")
            
            print("Total expected resource load (USD)...", round(self.data["Expected Resource Cost"].sum(),2))
            print("Highest Risk Cases...")
            print(self.data.nlargest(5, "Risk Score")[[
                "Case ID", "Case Type", "Risk Score"
                ]], "\n")
        except Exception as exceptObject :
            print(f"\nFatal Error! Summary Report failed : {exceptObject}")
            raise
        
    def showData(self, message = "Displaying Dataset") :
        try :
            if self.data is None :
                raise DataNotLoadedError("\nFatal Error! Dataset not loaded\n")
            
            print(f"\n{message}")
            print(self.data.to_string(index = False))
            print("\n")
        except Exception as exceptObject :
            print(f"\nFatal Error! Error displaying records : {exceptObject}\n")
            raise
        
    def saveModifiedData(self, outputPath) :
        try :
            if self.data is None :
                raise DataNotLoadedError("\nFatal Error! No modified data to save\n")
            
            self.data.to_excel(outputPath, index = False)
            print(f"\nEnhanced Healthcare Dataset Saved at : {outputPath}\n")
        except Exception as exceptObject :
            print(f"\nFatal Error! Error saving output file : {exceptObject}\n")
            raise
        
class HealthCareCharts :
    
    @staticmethod 
    def plotSeverityDistribution(data) :
        plt.figure(figsize = (7, 4))
        data["Severity Level"].value_counts().plot(kind = "bar")
        plt.title("Case count by Severity Level")
        plt.xlabel("Severity Level")
        plt.ylabel("Count")
        plt.grid(axis = 'y')
        plt.show()
        
    @staticmethod 
    def plotRiskScoreTrend(data) :
        plt.figure(figsize = (10, 4))
        plt.plot(data["Case ID"], data["Risk Score"], marker = "o")
        plt.title("Risk Score Trend by Case")
        plt.xlabel("Case ID")
        plt.ylabel("Risk Score")
        plt.grid()
        plt.show()
        
    @staticmethod 
    def plotICUComparison(data) :
        plt.figure(figsize = (7, 4))
        data.groupby("ICU Required")["Resource Cost (USD)"].mean().plot(kind = "bar")
        plt.title("Average Resource Cost : ICU vs Non-ICU Cases")
        plt.ylabel("Avg Cost (USD)")
        plt.grid(axis = 'y')
        plt.show()
        
    @staticmethod 
    def plotExpectedResourceDistribution(data) :
        plt.figure(figsize = (10, 4))
        plt.bar(data["Case ID"], data["Expected Resource Cost"])
        plt.title("Expected Resource Cost per Case")
        plt.xlabel("Case ID")
        plt.ylabel("Expected Cost (USD)")
        plt.grid(axis = 'y')
        plt.show()
        
def main() :
    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\003_ExpectedValue\DataSets\HealthCareData.xlsx"
    outFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\003_ExpectedValue\DataSets\OutData\OutHealthCareData.xlsx"
    try :
        healthObj = HealthCareEVCalculator(inFilePath)
    
        healthObj.loadData()
        healthObj.showData("displaying Original Healthcare Emergency Dataset")
        healthObj.addHelperColumns()
        
        totalEV = healthObj.calculatedExpectedValue()
        
        print(f"\n----------Expected Value Analysis Summary-----------")
        print(f"\nTotal Expected Rsource Load (USD) : {totalEV : .2f}")
        
        healthObj.generateSummaryReport()
        healthObj.showData("Dataset with all healthcare enhancements applied")
        
        charts = HealthCareCharts()
        charts.plotSeverityDistribution(healthObj.data)
        charts.plotRiskScoreTrend(healthObj.data)
        charts.plotICUComparison(healthObj.data)
        charts.plotExpectedResourceDistribution(healthObj.data)
        
        healthObj.saveModifiedData(outFilePath)
    except Exception as exceptObject :
        print(f"\nApplication Terminated - Reason : {exceptObject}\n")
        
if __name__ == "__main__" :
    main()