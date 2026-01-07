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

class InsuranceCompositeWMEngine :
    """
    Computes Simple Mean and Composite Weighted Mean for Claim Severity Considering
    1. Premium Exposure
    2. Claim Probability
    3. Claim Amount Severity
    4. Loss Ratio
    5. Severity Index
    """
    def __init__(
        self,
        inputFilePath : str,
        outputFilePath : str
    ) -> None :
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath

        self.dataFrame : pd.DataFrame | None = None

        self.targetFeatures : List[str] = ["ClaimAmount"]
        self.weightColumn : str = "CompositeWeight"

        """
        Actuarial Coefficients (Defined by Risk / Pricing Teams)
        """
        self.alpha   : float = 0.30  # Premium Exposure
        self.beta    : float = 0.25  # Claim Probability
        self.gamma   : float = 0.20  # Claim Severity
        self.delta   : float = 0.15  # Loss Ratio
        self.epsilon : float = 0.10  # Severity Index

        self.requiredColumns : List[str] = [
            "ClaimAmount",
            "AnnualPremium",
            "ClaimProbability"
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
        Core Actuarial Metrics
        """
        self.dataFrame["LossRatio"] = (
            self.dataFrame["ClaimAmount"] / self.dataFrame["AnnualPremium"]
        )

        self.dataFrame["SeverityIndex"] = (
            self.dataFrame["ClaimAmount"]
            * self.dataFrame["ClaimProbability"]
        )

        """
        Normalized Risk Components
        """
        self.dataFrame["NormPremium"] = self._minMaxNormalize(
            self.dataFrame["AnnualPremium"]
        )

        self.dataFrame["NormClaimProbability"] = self._minMaxNormalize(
            self.dataFrame["ClaimProbability"]
        )

        self.dataFrame["NormClaimAmount"] = self._minMaxNormalize(
            self.dataFrame["ClaimAmount"]
        )

        self.dataFrame["NormLossRatio"] = self._minMaxNormalize(
            self.dataFrame["LossRatio"]
        )

        self.dataFrame["NormSeverityIndex"] = self._minMaxNormalize(
            self.dataFrame["SeverityIndex"]
        )

        """
        Composite Weight Construction
        """
        self.dataFrame[self.weightColumn] = (
            self.alpha   * self.dataFrame["NormPremium"]
            + self.beta  * self.dataFrame["NormClaimProbability"]
            + self.gamma * self.dataFrame["NormClaimAmount"]
            + self.delta * self.dataFrame["NormLossRatio"]
            + self.epsilon * self.dataFrame["NormSeverityIndex"]
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
                f"Fatal Error! Composite Claim Severity Computation Failed : {exceptObject}"
            )

    def plotComparison(
        self,
        simpleMean : pd.Series,
        compositeMean : pd.Series
    ) -> None :

        comparisonFrame = pd.DataFrame({
            "Simple Mean Claim Severity" : simpleMean,
            "Composite Weighted Claim Severity" : compositeMean
        })

        comparisonFrame.plot(
            kind = "bar",
            figsize = (9, 5),
            title = "Claim Severity : Simple Mean vs Composite Weighted Mean"
        )

        plt.ylabel("Claim Amount")
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

        print("\n---------------- Simple Mean Claim Severity ----------------")
        print(simpleMean.round(4))

        print("\n---------- Composite Weighted Claim Severity ----------")
        print(compositeMean.round(4))

        self.plotComparison(simpleMean, compositeMean)
        self.saveEnhancedDataset()

def main() -> None:
    inputFilePath = (
        r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\InsuranceClaims.xlsx"
    )

    outputFilePath = (
        r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\002_WeightedMean\DataSets\EnhancedData\InsuranceClaimsCompositeWeightedData.xlsx"
    )            

    try :
        engine = InsuranceCompositeWMEngine(
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