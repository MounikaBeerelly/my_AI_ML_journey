import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import List

class DataFileNotFoundError(Exception):
    pass

class DataSetEmptyError(Exception) :
    pass

class InvalidSchemaError(Exception) :
    pass

class WeightedMeanComputationError(Exception) :
    pass

class EducationCompositeWMEngine :
    '''
    Computes Simple Mean GPA and Composite Credit-weighted GPA considering
    1. Credit Hours
    2. Marks Performance
    3. Grade Stability
    '''
    def __init__(self, inputFilePath : str, outputFilePath : str):
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath
        
        self.dataFrame : pd.DataFrame | None = None
        
        self.numericFeatures : List[str] = ["GradePoints"]
        self.weightedColumn : str = "CompositeWeight"
        
        """
        Academic Controlled Coefficients         
        """
        self.alpha : float = 0.55 # Credit Importance
        self.beta : float = 0.30 # Performance Importance
        self.gamma : float = 0.15 # Stability Importance
        
        self.requiredColumns : List[str] = [
            "Marks",
            "CreditHours"
        ]
        
    def loadDataset(self) -> None :
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
    
    @staticmethod        
    def _minMaxNormalize(inSeries : pd.Series) -> pd.Series :
        if inSeries.max() == inSeries.min() :
            return pd.Series(0.0, index = inSeries.index)
        return (inSeries - inSeries.min()) / inSeries.max() - inSeries.min()
    
    def addDerivedColumns(self) -> None :
        
        # Core Academic Metrics
        self.dataFrame["GradePoints"] = self.dataFrame["Marks"] / 10
        
        # Normalized Components
        self.dataFrame["NormCreditHours"] = self._minMaxNormalize(
            self.dataFrame["CreditHours"]
        )
        
        self.dataFrame["NormMarks"] = self._minMaxNormalize(
            self.dataFrame["Marks"]
        )
        
        self.dataFrame["NormGradePoints"] = self._minMaxNormalize(
            self.dataFrame["GradePoints"]
        )
        
        # Composite Weight Construction
        self.dataFrame[self.weightedColumn] = (
            self.alpha * self.dataFrame["NormCreditHours"]
            + self.beta * self.dataFrame["NormMarks"]
            + self.gamma * self.dataFrame["NormGradePoints"]
        )
        
        weightedSum = self.dataFrame[self.weightedColumn].sum()
        
        if weightedSum == 0 :
            raise WeightedMeanComputationError(
                "Fatal Error! Composite Weight sum is zero, cannot normalize"
            )
            
        self.dataFrame[self.weightedColumn] /= weightedSum
            
    def computeSimpleMean(self) -> pd.Series :
        return self.dataFrame[self.numericFeatures].mean()
    
    def computeCompositeWeightedMean(self) -> pd.Series :
        try :
            weights = self.dataFrame[self.weightedColumn]
            
            return pd.Series({
                feature : (
                    self.dataFrame[feature] * weights
                ).sum()
                for feature in self.numericFeatures
            })
        except Exception as exceptObject :
            raise WeightedMeanComputationError(
                f"\nFatal Error! Composite Weighted Mean failed : {exceptObject}"
            )
            
    def plotcomparisonCharts(
        self,
        simpleMean : pd.Series,
        compositeMean : pd.Series
    ) -> None :    
        comparisonFrame = pd.DataFrame({
            "Simple Mean GPA" : simpleMean,
            "Composite Weighted Mean GPA" : compositeMean
        })
        
        comparisonFrame.plot(
            kind = 'bar',
            figsize = (8, 5),
            title = "GPA : Simple Mean vs Composite Weighted Mean"
        )
        
        plt.ylabel("GPA Value")
        plt.grid(axis = 'y')
        plt.tight_layout()
        plt.show()
    
    def saveEnhancedDataset(self) -> None :
        self.dataFrame.to_excel(
            self.outputFilePath,
            index = False
        )
        
    def runAnalysis(self) -> None :
        self.loadDataset()
        self.validateSchema()
        self.addDerivedColumns()
                
        simpleMean = self.computeSimpleMean()
        compositeMean = self.computeCompositeWeightedMean()
        
        print("\n--------Displaying the Simple Mean Value--------")
        print(simpleMean.round(4))
        
        print("\n----------Displaying the Composite Weighted Mean value----------")
        print(compositeMean.round(4))
        
        self.plotcomparisonCharts(simpleMean, compositeMean)
        self.saveEnhancedDataset()

def main() -> None :
    inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\StudentPerformance.xlsx"
    outputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\EnhancedData\StudentPerformanceCompositeEnhancedData.xlsx"
        
    try :
        engine = EducationCompositeWMEngine(
            inputFilePath = inputFilePath,
            outputFilePath = outputFilePath
        )
            
        engine.runAnalysis()
            
        print("\nComposite Weighted Mean Analysis completed successfully..")
        print(f"Enhanced dataset saved at : {outputFilePath}")
    except (
        DataFileNotFoundError,
        DataSetEmptyError,
        InvalidSchemaError,
        WeightedMeanComputationError
    ) as meanErrors :
        print(f"\n{meanErrors}")
    except Exception as unexpectedError :
        print(
            f"Fatal Error! Unexpected error occured : {unexpectedError}"
        )
        
if __name__ == "__main__" :
    main()