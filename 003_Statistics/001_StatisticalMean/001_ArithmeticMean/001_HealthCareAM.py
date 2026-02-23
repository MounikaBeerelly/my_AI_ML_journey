import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
from typing import List
import os

class DataFileNotFoundError(Exception):
    pass

class DataSetEmptyError(Exception) :
    pass

class NumericFeatureNotFoundError(Exception) :
    pass

class HealthCareAMEngine :
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.dataFrame : pd.DataFrame | None = None
        self.numericFeatures : List[str] = []
        
    def loadData(self) -> None :
        if not os.path.exists(self.inFilePath) :
            raise DataFileNotFoundError(
                f"Fatal Error! Dataset not found at : {self.inFilePath}"
            )
        
        self.dataFrame = pd.read_excel(self.inFilePath)
        
        if self.dataFrame.empty :
            raise DataSetEmptyError("Fatal Error! Dataset contains no records.")
        
    def identifyNumericFeatures(self) -> None :
        if self.dataFrame is None :
            raise DataSetEmptyError("Dataset must be loaded before analysis.")
        
        self.numericFeatures = self.dataFrame.select_dtypes(
            include = ["int64", "float64"]
        ).columns.tolist()
        
        if not self.numericFeatures :
            raise NumericFeatureNotFoundError(
                "No numeric features found for Arithmetic Mean calculation"
            )
            
    def calculateArithmeticMean(self) -> pd.DataFrame :
        meanResults = {
            outFeature : self.dataFrame[outFeature].mean()
            for outFeature in self.numericFeatures
        }
        
        return pd.DataFrame(
            meanResults.items(),
            columns = ["FeatureName", "ArithmeticMean"]
        ).sort_values(by = "ArithmeticMean", ascending = False)
        
        
    def plotMeanValues(self, meanDataFrame : pd.DataFrame) -> None :
        plt.figure(figsize = (14, 6))
        plt.bar(
            meanDataFrame["FeatureName"],
            meanDataFrame["ArithmeticMean"]
        )
        plt.xticks(rotation = 60)
        plt.title("Arithmetic Mean of Healthcare Numeric Features")
        plt.xlabel("Feature")
        plt.ylabel("Mean Value")
        plt.grid(axis = 'y')
        plt.tight_layout()
        plt.show()
        
    def plotFeatureDistribution(self) -> None :
        self.dataFrame[self.numericFeatures].hist(
            figsize = (16, 12),
            bins = 25,
            edgecolor = "black"
        )
        plt.suptitle("Distribution of Numeric Healthcare Features", fontsize = 16)
        plt.tight_layout()
        plt.show()
        
    def plotCorrelationHeatMap(self) -> None :
        correlationMatrix = self.dataFrame[self.numericFeatures].corr()
        plt.figure(figsize = (14, 10))
        sns.heatmap(
            correlationMatrix,
            annot = None,
            cmap = "coolwarm",
            linewidths = 0.5
        )
        plt.title("Correlation heatmap of Healthcare Features")
        plt.tight_layout()
        plt.show()
        
class HealthCareAMApp :
    @staticmethod
    def run() -> None :
        try :
            inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\001_ArithmeticMean\DataSets\HealthCareRecords.xlsx"
            
            healthCareAMAppObject = HealthCareAMEngine(inFilePath = inFilePath)
            
            healthCareAMAppObject.loadData()
            healthCareAMAppObject.identifyNumericFeatures()
            
            meanDataFrame = healthCareAMAppObject.calculateArithmeticMean()
            
            print("\n----Displaying the Arithmetic Mean Results (Healthcare Data) -----\n")
            print(meanDataFrame)
            
            healthCareAMAppObject.plotMeanValues(meanDataFrame)
            healthCareAMAppObject.plotFeatureDistribution()
            healthCareAMAppObject.plotCorrelationHeatMap()
            
            HealthCareAMApp.printInterpretation(meanDataFrame)
        except DataFileNotFoundError as dataFileNotLoadingError :
            print(f"\nFatal Error! data file is missing : {dataFileNotLoadingError}")
        except DataSetEmptyError as datasetEmptyError:
            print(f"\nFatal Error! Data is unable to be loaded : {datasetEmptyError}")
        except NumericFeatureNotFoundError as numericFeatureNotFounderror :
            print(f"\nFatal error! Unable to find the numeric Features : {numericFeatureNotFounderror}")
        except Exception as exceptObject :
            print(f"\nFatal Error! Unexpected error occured : {exceptObject}")
              
    @staticmethod
    def printInterpretation(inMeanDataFrame : pd.DataFrame) -> None :
        print(f"\n------------Data Scientist Interpretation (Healthcare AI context) -----------\n")
        
        for _, outRow in inMeanDataFrame.iterrows() :
            print(
                f"_ The average value of {outRow['FeatureName']} "
                f"is {outRow['ArithmeticMean'] : .2f}, Represents the "
                f" Baseline behavior of the patients population."
            )
        
        
if __name__ == "__main__" :
    HealthCareAMApp.run()