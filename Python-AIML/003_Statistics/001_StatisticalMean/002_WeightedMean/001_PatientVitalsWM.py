import pandas as pd
import matplotlib.pyplot as plt
from typing import List
import os

class DataFileNotFoundError(Exception):
    pass

class DataSetEmptyError(Exception) :
    pass

class InvalidSchemaError(Exception) :
    pass

class WeightedMeanComputationError(Exception) :
    pass

class HealthCareWMEngine :
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.dataFrame : pd.DataFrame | None = None
        self.weightedColumn : str = "RiskWeight"
        self.numericFeatures : List[str] = [
            "HeartRate",
            "SystolicBP",
            "OxygenLevel"
        ]
        
    def loadData(self) -> None :
        if not os.path.exists(self.inFilePath) :
            raise DataFileNotFoundError(
                f"Fatal Error! Dataset not found at : {self.inFilePath}"
            )
        
        self.dataFrame = pd.read_excel(self.inFilePath)
        
        if self.dataFrame.empty :
            raise DataSetEmptyError("Fatal Error! Dataset contains no records.")
        
    def validateSchema(self) -> None :
        requiredcolumns = self.numericFeatures + [self.weightedColumn]
        
        for outcolumn in requiredcolumns :
            if outcolumn not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required column is missing : {outcolumn}"
                )
                
    def computeWeightedMean(self) -> None :  
        try :
            weightedMeans = {}
            inWeights = self.dataFrame[self.weightedColumn]
            
            for outFeature in self.numericFeatures :
                weightedValue = (
                    (self.dataFrame[outFeature] * inWeights).sum() / inWeights.sum()
                )
                weightedMeans[outFeature] = weightedValue
                
            return pd.Series(weightedMeans)
        except Exception as exceptObject :
            raise WeightedMeanComputationError(
                f"Fatal Error! Error computing weighted mean : {exceptObject}"
            )
        
    def computeSimpleMean(self) -> pd.Series :
        return self.dataFrame[self.numericFeatures].mean()
    
    def plotcomparisonCharts(
        self,
        simpleMean : pd.Series,
        weightedMean : pd.Series
    ) -> None :
        
        comparisonFrame = pd.DataFrame({
            "Simple Mean" : simpleMean,
            "Weighted Mean" : weightedMean
        })
        
        comparisonFrame.plot(
            kind = 'bar',
            figsize = (10, 6),
            title = "Simple Mean vs Weighted Mean of Patient vitals"
        )
        
        plt.ylabel("Measurement Value")
        plt.xticks(rotation = 0)
        plt.grid(axis = 'y')
        plt.tight_layout()
        plt.show()
        
    def runAnalysis(self) -> None :
        self.loadData()
        self.validateSchema()
        
        simpleMean = self.computeSimpleMean()
        weightedMean = self.computeWeightedMean()
        
        print("\n--------Simple Mean--------")
        print(simpleMean.round(2))
        
        print("\n----------Weighted Mean----------")
        print(weightedMean.round(2))
        
        self.plotcomparisonCharts(simpleMean, weightedMean)
        
class HealthCareAnalyticsApp :
    @staticmethod
    def run() -> None :
        try :
            inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\PatientVitalsRecords.xlsx"
            
            engine = HealthCareWMEngine(inFilePath)
            engine.runAnalysis()
        except (
            DataFileNotFoundError,
            DataSetEmptyError,
            InvalidSchemaError,
            WeightedMeanComputationError
        ) as knownException :
            print(f"Fatal Error! Error encountered is : {knownException}")
        except Exception as exceptObject :
            print(f"Fatal Error! Error computing weighted mean : {exceptObject}")
            
if __name__ == "__main__" :
    HealthCareAnalyticsApp.run()