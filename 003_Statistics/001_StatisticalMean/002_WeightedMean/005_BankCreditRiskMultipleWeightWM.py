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

class BankingCompositeWMEngine :
    '''
    Computes Simple Mean and Composite Risk-Weighted Credit score considering
    1. Loan Exposure
    2. Probability of default
    3. Credit Score Stability
    '''
    def __init__(self, inputFilePath : str, outputFilePath : str):
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath
        
        self.dataFrame : pd.DataFrame | None = None
        
        self.numericFeatures : List[str] = ["CreditScore"]
        self.weightedColumn : str = "CompositeWeight"
        
        """
        Risk Coefficients (defined by Risk Team / Base models)     
        """
        self.alpha : float = 0.55 # Exposure Importance
        self.beta : float = 0.30 # Default Risk Importance
        self.gamma : float = 0.15 # Score stability Importance
        
        self.requiredColumns : List[str] = [
            "CreditScore",
            "LoanAmount",
            "DefaultProbability"
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
        
        # Core Risk Metrics
        self.dataFrame["Exposure"] = (
            self.dataFrame["LoanAmount"] 
            * self.dataFrame["DefaultProbability"]
        )
               
        # Normalized Risk Components
        self.dataFrame["NormExposure"] = self._minMaxNormalize(
            self.dataFrame["Exposure"]
        )
        
        self.dataFrame["NormDefaultProbability"] = self._minMaxNormalize(
            self.dataFrame["DefaultProbability"]
        )
        
        self.dataFrame["NormCreditScore"] = self._minMaxNormalize(
            self.dataFrame["CreditScore"]
        )
        
        # Composite Risk Weight Construction
        self.dataFrame[self.weightedColumn] = (
            self.alpha * self.dataFrame["NormExposure"]
            + self.beta * self.dataFrame["NormDefaultProbability"]
            + self.gamma * self.dataFrame["NormCreditScore"]
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
            "Simple Mean CreditScore" : simpleMean,
            "Composite Weighted Mean CreditScore" : compositeMean
        })
        
        comparisonFrame.plot(
            kind = 'bar',
            figsize = (8, 5),
            title = "CreditScore : Simple Mean vs Composite Risk Weighted Mean"
        )
        
        plt.ylabel("Cedit Score Value")
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
    inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\BankingCreditRisk.xlsx"
    outputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\EnhancedData\BankingCreditRiskCompositeWeightedEnhancedData.xlsx"
        
    try :
        engine = BankingCompositeWMEngine(
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