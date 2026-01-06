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

class RetailWeightedMeanEngine :
    def __init__(self, inputFilePath : str, outputFilePath : str):
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath
        
        self.dataFrame : pd.DataFrame | None = None
        
        self.numericFeatures : List[str] = ["CustomerRating"]
        self.weightedColumn : str = "RevenueWeight"
        
        self.requiredColumns : List[str] = [
            "UnitPrice",
            "UnitsSold",
            "CustomerRating"
        ]
        
    def loadData(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DataFileNotFoundError(
                f"Fatal Error! Dataset not found at : {self.inputFilePath}"
            )
        
        self.dataFrame = pd.read_excel(self.inputFilePath)
        
        if self.dataFrame.empty :
            raise DataSetEmptyError("Fatal Error! Dataset contains no records.")
        
    def validateSchema(self) -> None :
        requiredColumns = self.numericFeatures + [self.weightedColumn]
        
        for outColumn in self.requiredColumns :
            if outColumn not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required column is missing : {outColumn}"
                )
                
    def addDerivationColumns(self) -> None :
        self.dataFrame["Revenue"] = (
            self.dataFrame["UnitPrice"] * self.dataFrame["UnitsSold"]
        )
        
        totalRevenue = self.dataFrame["Revenue"].sum()
        
        if totalRevenue == 0 :
            raise WeightedMeanComputationError(
                "Fatal Error! Total revenue is zero, cannot compute weights."
            )
            
        self.dataFrame[self.weightedColumn] = (
            self.dataFrame["Revenue"] / totalRevenue
        )
        
    def debugWeightDistributions(self) -> None :
        print("------Revenue & Weight Diagnostics--------")
        print(self.dataFrame[["Revenue", self.weightedColumn]].describe())
        
        print(f"\nPrinting top 5 hiigh revenue transactions...")
        print(
            self.dataFrame
            .sort_values("Revenue", ascending = False)
            .head(5)[
                ["UnitPrice", "UnitsSold", "Revenue", "CustomerRating"]
            ]
        )
        
        print(
            f"\nThe Total weighted sum : "
            f"{self.dataFrame[self.weightedColumn].sum() : .6f}"
        )
        
    def computeSimpleMean(self) -> pd.Series :
        return self.dataFrame[self.numericFeatures].mean()
    
    def computeWeightedMean(self) -> pd.Series :
        try :
            weights = self.dataFrame[self.weightedColumn]
            
            if weights.isnull().any() :
                raise ("Fatal Error! Null values detected in Weight Column....")
            weightedMeans = {
                feature : (
                    self.dataFrame[feature] * weights
                ).sum()
                for feature in self.numericFeatures
            }
            
            return pd.Series(weightedMeans)
        except Exception as exceptObject :
            raise WeightedMeanComputationError(
                f"Fatal Error! Weighted mean computation failed : {exceptObject}"
            )
            
    def plotcomparisonCharts(
        self,
        simpleMean : pd.Series,
        weightedMean : pd.Series
    ) -> None :    
        comparisonFrame = pd.DataFrame({
            "Simple Mean" : simpleMean,
            "Revenue Weighted Mean" : weightedMean
        })
        
        comparisonFrame.plot(
            kind = 'bar',
            figsize = (8, 5),
            title = "Customer Rating : Simple Mean vs Revenue-Weighted Mean"
        )
        
        plt.ylabel("Rating Value")
        plt.grid(axis = 'y')
        plt.tight_layout()
        plt.show()
        
    def saveEnhancedDataset(self) -> None :
        self.dataFrame.to_excel(
            self.outputFilePath,
            index = False
        )
        
    def runAnalysis(self) -> None :
        self.loadData()
        self.validateSchema()
        self.addDerivationColumns()
        
        self.debugWeightDistributions()
        
        simpleMean = self.computeSimpleMean()
        weightedMean = self.computeWeightedMean()
        
        print("\n--------Displaying the Simple Mean Value--------")
        print(simpleMean.round(4))
        
        print("\n----------Displaying the Weighted Mean value----------")
        print(weightedMean.round(4))
        
        self.plotcomparisonCharts(simpleMean, weightedMean)
        self.saveEnhancedDataset()
        
def main() -> None :
    inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\RetailSalesRecords.xlsx"
    outputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\EnhancedData\RetailSalesRecordsEnhanced.xlsx"
        
    try :
        engine = RetailWeightedMeanEngine(
            inputFilePath = inputFilePath,
            outputFilePath = outputFilePath
        )
            
        engine.runAnalysis()
            
        print("\nRetail Weighted Mean Analysis completed successfully..")
        print(f"Enhanced dataset saved at : {outputFilePath}")
    except (
        DataFileNotFoundError,
        DataSetEmptyError,
        InvalidSchemaError,
        WeightedMeanComputationError
    ) as meanErrors :
        print(f"\n{meanErrors}")
    except Exception as exceptObject :
        raise WeightedMeanComputationError(
            f"Fatal Error! Weighted mean computation failed : {exceptObject}"
        )
        
if __name__ == "__main__" :
    main()