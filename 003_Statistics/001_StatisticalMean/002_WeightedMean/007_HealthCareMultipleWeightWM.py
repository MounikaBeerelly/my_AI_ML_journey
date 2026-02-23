import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import List

class DatasetNotFoundError(Exception) :
    pass

class DatasetEmptyError(Exception) :
    pass

class InvalidSchemaError(Exception) :
    pass

class WeightedMeanComputationError(Exception) :
    pass

class HealthcareCompositeWMEngine :
    """
    Computes Simple Mean and Composite Weighted Mean for Pathology-Based Health Risk Analysis Considering
    1. Test Severity
    2. Deviation from Normal Range
    3. Risk Probability
    4. Critical Condition Flag
    5. Age Risk Factor
    """
    def __init__(
        self,
        inputFilePath : str,
        outputFilePath : str
    ) -> None :
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath

        self.dataFrame : pd.DataFrame | None = None

        self.targetFeatures : List[str] = ["TestValue"]
        self.weightColumn : str = "CompositeWeight"

        """
        Clinical Weight Coefficients (Defined by Medical Experts)
        """
        self.alpha   : float = 0.30  # Test Severity
        self.beta    : float = 0.25  # Deviation From Normal
        self.gamma   : float = 0.20  # Disease Risk Probability
        self.delta   : float = 0.15  # Critical Condition Flag
        self.epsilon : float = 0.10  # Age Risk Factor

        self.requiredColumns : List[str] = [
            "PatientId",
            "TestName",
            "TestValue",
            "NormalMin",
            "NormalMax",
            "RiskProbability",
            "CriticalFlag",
            "Age"
        ]

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Fatal Error! Dataset Not Found At Path : {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError("Fatal Error! Dataset is Empty.")

    def validateSchema(self) -> None :
        for outColumn in self.requiredColumns :
            if outColumn not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required Column Missing : {outColumn}"
                )

    @staticmethod
    def _minMaxNormalize(inSeries : pd.Series) -> pd.Series :
        if inSeries.max() == inSeries.min() :
            return pd.Series(0.0, index=inSeries.index)
        return (inSeries - inSeries.min()) / (inSeries.max() - inSeries.min())

    def addDerivedColumns(self) -> None :
        """
        Medical Risk Metrics
        """
        self.dataFrame["DeviationScore"] = (
            abs(self.dataFrame["TestValue"]
            - ((self.dataFrame["NormalMin"] + self.dataFrame["NormalMax"]) / 2))
        )

        self.dataFrame["AgeRiskFactor"] = self.dataFrame["Age"] / 100

        """
        Normalized Components
        """
        self.dataFrame["NormDeviation"] = self._minMaxNormalize(
            self.dataFrame["DeviationScore"]
        )

        self.dataFrame["NormRiskProbability"] = self._minMaxNormalize(
            self.dataFrame["RiskProbability"]
        )

        self.dataFrame["NormCriticalFlag"] = self._minMaxNormalize(
            self.dataFrame["CriticalFlag"]
        )

        self.dataFrame["NormAgeRisk"] = self._minMaxNormalize(
            self.dataFrame["AgeRiskFactor"]
        )

        self.dataFrame["NormTestValue"] = self._minMaxNormalize(
            self.dataFrame["TestValue"]
        )

        """
        Composite Health Risk Weight
        """
        self.dataFrame[self.weightColumn] = (
            self.alpha   * self.dataFrame["NormTestValue"]
            + self.beta  * self.dataFrame["NormDeviation"]
            + self.gamma * self.dataFrame["NormRiskProbability"]
            + self.delta * self.dataFrame["NormCriticalFlag"]
            + self.epsilon * self.dataFrame["NormAgeRisk"]
        )

        weightSum = self.dataFrame[self.weightColumn].sum()

        if weightSum == 0 :
            raise WeightedMeanComputationError(
                "Fatal Error! Composite Weight Sum is Zero."
            )

        self.dataFrame[self.weightColumn] /= weightSum

    def computeSimpleMean(self) -> pd.Series :
        return self.dataFrame[self.targetFeatures].mean()

    def computeCompositeWeightedMean(self) -> pd.Series :
        try :
            weights = self.dataFrame[self.weightColumn]

            return pd.Series({
                feature : (
                    self.dataFrame[feature] * weights
                ).sum()
                for feature in self.targetFeatures
            })

        except Exception as exceptObject :
            raise WeightedMeanComputationError(
                f"Fatal Error! Composite Health Risk Computation Failed : {exceptObject}"
            )

    def plotComparison(
        self,
        simpleMean : pd.Series,
        compositeMean : pd.Series
    ) -> None :

        comparisonFrame = pd.DataFrame({
            "Simple Mean Test Value" : simpleMean,
            "Composite Risk Weighted Value" : compositeMean
        })

        comparisonFrame.plot(
            kind ="bar",
            figsize = (9, 5),
            title = "Pathology Report : Simple Mean vs Composite Risk-Weighted Mean"
        )

        plt.ylabel("Test Value")
        plt.grid(axis = "y")
        plt.tight_layout()
        plt.show()

    def saveEnhancedDataset(self) -> None :
        self.dataFrame.to_excel(self.outputFilePath, index=False)

    def runAnalysis(self) -> None :
        self.loadDataset()
        self.validateSchema()
        self.addDerivedColumns()

        simpleMean = self.computeSimpleMean()
        compositeMean = self.computeCompositeWeightedMean()

        print("\n---------------- Simple Mean Test Value ----------------")
        print(simpleMean.round(4))

        print("\n---------- Composite Health Risk Weighted Value ----------")
        print(compositeMean.round(4))

        self.plotComparison(simpleMean, compositeMean)
        self.saveEnhancedDataset()

def main() -> None:
    inputFilePath = (
        r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\HealthcarePathologyReports.xlsx"
    )

    outputFilePath = (
        r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\EnhancedData\HealthcarePathologyReportsCompositeWeightedData.xlsx"
    )            

    try :
        engine = HealthcareCompositeWMEngine(
            inputFilePath = inputFilePath,
            outputFilePath = outputFilePath
        )

        engine.runAnalysis()        

        print("\nComposite Weighted Mean Analysis Completed Successfully.")
        print(f"\nEnhanced Dataset Saved At: {outputFilePath}")
    except (
        DatasetNotFoundError,
        DatasetEmptyError,
        InvalidSchemaError,
        WeightedMeanComputationError
    ) as meanErrors :
        print(f"\n{meanErrors}")
    
    except Exception as unexpectedError:
        print(f"\nFatal Error! Unexpected Error Occurred : {unexpectedError}")

if __name__ == "__main__":
    main()