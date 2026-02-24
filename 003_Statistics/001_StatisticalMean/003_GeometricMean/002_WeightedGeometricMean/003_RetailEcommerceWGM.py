import os
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

class RuntimeMetricComputationError(Exception) :
    pass

class WeightedGeometricMeanComputationError(Exception) :
    pass

class CustomerRuntimeWeightedGeometricMeanEngine :
    """
    Computes Runtime Customer Metrics and Applies Risk-Weighted Geometric Mean for Customer Value Growth Analytics"""
    def __init__(
        self,
        inputFilePath: str,
        outputFilePath: str
    ) -> None :

        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath

        self.dataFrame: pd.DataFrame | None = None

        self.requiredColumns = [
            "CustomerID",
            "CustomerName",
            "Year",
            "AnnualSpendGrowthRate",
            "CustomerSegment",
            "RiskCategory"
        ]

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Dataset not found at path: {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError(
                "Fatal Error! Dataset Contains No Records"
            )

        print("Dataset loaded successfully")

    def validateSchema(self) -> None :
        for outColumns in self.requiredColumns :
            if outColumns not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Missing Required Column: {outColumns}"
                )

        print("Schema validation successful")

    def validateGrowthRates(self) -> None :
        if(self.dataFrame["AnnualSpendGrowthRate"] <= -100).any() :
            raise InvalidReturnRateError(
                "Fatal Error! AnnualSpendGrowthRate must be greater than -100%"
            )
        print("AnnualSpendGrowthRate validation successful")

    def computeRuntimeMetrics(self) -> None :
        try :
            df = self.dataFrame.copy()

            print(f"\nComputing runtime customer Metrics...")

            segmetBaseValue = {
                "New" :8000,
                "Regular" : 15000,
                "HighValue" : 30000,
                "ChurnRisk" : 6000
            }
            df["CustomerLifetimeValue"] = (
                df["CustomerSegment"].map(segmetBaseValue)
                * np.random.uniform(0.8, 1.2, size=len(df))
            )
            df["VolatalityPercent"] = (
                df.groupby("CustomerID")["AnnualSpendGrowthRate"]
                .transform("std")
                .fillna(6.0)
            )

            df["ChurnRiskFactor"] = df["RiskCategory"].map(
                {
                    "Low": 0.4,
                    "Medium": 0.8,
                    "High": 1.4
                }
            )

            df["GrowthFactor"] = (
                1 + (df["AnnualSpendGrowthRate"] / 100)
            )

            self.dataFrame = df

            print("Runtime customer metrics computation computed successfully")
        except Exception as exceptObj :
            raise RuntimeMetricComputationError(
                f"Error during runtime metric computation: {exceptObj}"
            )

    def computeWeights(self) -> None :
        print(f"\nComputing dynamic Customer weights...")

        rawWeight = (
            self.dataFrame["CustomerLifetimeValue"]
            / (1 + self.dataFrame["VolatalityPercent"])
            / (1 + self.dataFrame["ChurnRiskFactor"])
        )

        self.dataFrame["Weight"] = rawWeight / rawWeight.sum()

        print(f"\nDynamic weight Computation completed")

    def computeWeightedGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            df["WeightedLogGrowth"] = (
                df["Weight"] * np.log(df["GrowthFactor"])
            )

            resultDF = (
                df.groupby(["CustomerID", "CustomerName"])
                .agg(
                    Age = ("CustomerSegment", "first"),
                    RiskCategory = ("RiskCategory", "first"),
                    TotalWeight = ("Weight", "sum"),
                    WeightedLogSum = ("WeightedLogGrowth", "sum")
                )
                .reset_index()
            )

            resultDF["WeightedGeometricMeanGrowth"] = (
                np.exp(resultDF["WeightedLogSum"])
            )

            resultDF["WeightedGeometricMeanReturnPercent"] = (
                (resultDF["WeightedGeometricMeanGrowth"] - 1) * 100
            )

            print("Weighted Geometric Mean Computation completed successfully")

            return resultDF

        except Exception as exceptObj :
            raise WeightedGeometricMeanComputationError(
                f"Error during weighted geometric mean computation: {str(exceptObj)}"
            )

    def run(self) -> None :
        self.loadDataset()
        self.validateSchema()
        self.validateGrowthRates()
        self.computeRuntimeMetrics()
        self.computeWeights()

        resultDF = self.computeWeightedGeometricMean()
        resultDF.to_excel(self.outputFilePath, index=False)

        print(f"\nFinal output saved to: {self.outputFilePath}")

        resultDF.sort_values(
            "WeightedGeometricMeanReturnPercent",
            ascending = False
        ).plot(
            x = "CustomerName",
            y = "WeightedGeometricMeanReturnPercent",
            kind = "bar",
            legend = False,
            title = "Weighted Geometric Mean Returns"
        )

        plt.tight_layout()
        plt.show()

if __name__ == "__main__" :
    inFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\CustomerValueGrowth.xlsx"
    outFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\EnhancedData\CustomerValueGrowthEnhancedData.xlsx"

    engine = CustomerRuntimeWeightedGeometricMeanEngine(
        inputFilePath=inFilePath,
        outputFilePath=outFilePath
    )

    engine.run()