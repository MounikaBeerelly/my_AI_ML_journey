import os
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class DatasetNotFoundError(Exception) :
    pass


class DatasetEmptyError(Exception) :
    pass


class InvalidSchemaError(Exception) :
    pass


class InvalidReturnRateError(Exception) :
    pass


class GeometricMeanComputationError(Exception) :
    pass


class InvestmentGeometricMeanEngine :
    """
    Computes Simple Geometric Mean of Investment Returns
    To Analyze True Compounded Growth
    """

    def __init__(self, inputFilePath : str) -> None :
        self.inputFilePath = inputFilePath
        self.dataFrame : pd.DataFrame | None = None

        self.requiredColumns = [
            "InvestmentID",
            "InvestmentName",
            "Year",
            "AnnualReturnRate",
            "Sector",
            "RiskCategory"
        ]

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Fatal Error! Dataset Not Found At Path : {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError(
                "Fatal Error! Dataset Contains No Records."
            )

        print("Dataset Loaded Successfully")

    def validateSchema(self) -> None :
        for outColumn in self.requiredColumns :
            if outColumn not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required Column is Missing : {outColumn}"
                )

        print("Dataset Schema Validation Successful")

    def validateReturnRates(self) -> None :
        if (self.dataFrame["AnnualReturnRate"] <= -100).any() :
            raise InvalidReturnRateError(
                "Fatal Error! AnnualReturnRate Must Be Greater Than -100%"
            )

        print("Return Rate Validation Successful")

    def computeGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            print("\nConverting Percentage Returns To Growth Factors...")
            df["GrowthFactor"] = 1 + (df["AnnualReturnRate"] / 100)

            geometricMeanDF = (
                df.groupby(["InvestmentID", "InvestmentName"])
                .agg(
                    Sector = ("Sector", "first"),
                    RiskCategory = ("RiskCategory", "first"),
                    Years = ("Year", "count"),
                    GeometricMeanGrowth = (
                        "GrowthFactor",
                        lambda x : np.exp(np.mean(np.log(x)))
                    )
                )
                .reset_index()
            )

            geometricMeanDF["GeometricMeanReturnPercent"] = (
                (geometricMeanDF["GeometricMeanGrowth"] - 1) * 100
            )

            print("Geometric Mean Computation Completed Successfully")

            return geometricMeanDF

        except Exception as exceptObject :
            raise GeometricMeanComputationError(
                f"Fatal Error! Geometric Mean Computation Failed : {exceptObject}"
            )

    def plotGeometricMean(self, geometricMeanDF : pd.DataFrame) -> None :
        plotDF = geometricMeanDF.sort_values(
            by="GeometricMeanReturnPercent",
            ascending=True
        )

        plt.figure(figsize=(10, max(5, len(plotDF) * 0.4)))

        plt.barh(
            plotDF["InvestmentName"],
            plotDF["GeometricMeanReturnPercent"]
        )

        plt.xlabel("Geometric Mean Return (%)")
        plt.ylabel("Investment Name")
        plt.title("Geometric Mean Return By Investment")
        plt.tight_layout()
        plt.show()


def main() -> None :
    try :
        inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\DataSets\InvestmentGrowthRecords.xlsx"

        investmentEngine = InvestmentGeometricMeanEngine(inputFilePath)

        investmentEngine.loadDataset()
        investmentEngine.validateSchema()
        investmentEngine.validateReturnRates()

        geometricMeanDF = investmentEngine.computeGeometricMean()

        print("\nFinal Geometric Mean Output")
        print(geometricMeanDF)

        investmentEngine.plotGeometricMean(geometricMeanDF)

    except (
        DatasetNotFoundError,
        DatasetEmptyError,
        InvalidSchemaError,
        InvalidReturnRateError,
        GeometricMeanComputationError
    ) as knownException :
        print(f"\nApplication Failed : {knownException}")

    except Exception as unknownException :
        print(f"\nUnexpected System Error : {unknownException}")

if __name__ == "__main__" :
    main()
