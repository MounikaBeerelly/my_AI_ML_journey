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

class InvestmentRuntimeWeightedGeometricMeanEngine :
    """
    Computes Runtime Financial Metrics and Applies Weighted Geometric Mean using dynamically computed weights.
    """

    def __init__(
        self,
        inputFilePath: str,
        outputFilePath: str
    ) -> None :

        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath

        self.dataFrame: pd.DataFrame | None = None

        self.requiredColumns = [
            "InvestmentID",
            "InvestmentName",
            "Year",
            "AnnualReturnRate",
            "Sector",
            "RiskCategory"
        ]

        self.riskFreeRate = 4.0

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Dataset not found at path: {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError(
                "Dataset contains no records"
            )

        print("Dataset loaded successfully")

    def validateSchema(self) -> None :
        for outColumns in self.requiredColumns :
            if outColumns not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Required column '{outColumns}' not found in dataset"
                )
        print("Dataset schema validated successfully")

    def validateReturnRates(self) -> None :
        if(self.dataFrame["AnnualReturnRate"] <= -100).any() :
            raise InvalidReturnRateError(
                "Fatal Error! Annual Return Rate cannot be less than -100%"
            )
        print("Return Rates validation successful")

    def computeRuntimeMetrics(self) -> None :
        try :
            df = self.dataFrame.copy()

            print(f"\nComputing runtime financial Metrics...")

            print(f"\nTaking the parameters and values for marketcap (simulated by sector and Risk)")

            sectorBaseCap = {
                "Technology": 180000,
                "Banking": 150000,
                "Healthcare": 120000,
                "Energy": 100000,
                "FMCG": 90000,
                "Infrastructure": 110000
            }

            riskMultiplier = {
                "Low": 1.2,
                "Medium": 1.0,
                "High": 0.8
            }

            df["MarketCap"] = df.apply(
                lambda x: sectorBaseCap.get(x["Sector"], 100000) *
                riskMultiplier.get(x["RiskCategory"], 1.0) *
                np.random.uniform(0.8, 1.2),
                axis=1
            )

            df["BenchmarkReturnRate"] = (
                df.groupby("Year")["AnnualReturnRate"]
                .transform("mean")
            )

            df["VolatalityPercent"] = (
                df.groupby("InvestmentID")["AnnualReturnRate"]
                .transform("std")
                .fillna(5.0)
            )

            print(f"\nCalculating Expense Ratio (Risk-Based)")
            df["ExpenseRatioPercent"] = df["RiskCategory"].map(
                {"Low":0.8, "Medium":1.2, "High":1.8}
            )

            print(f"\nCalculating the value of Beta (Covariance vs Benchmark)")
            df["Beta"] = (
                df.groupby("InvestmentID")[["AnnualReturnRate", "BenchmarkReturnRate"]]
                .apply(
                    lambda x :
                        np.cov(
                            x["AnnualReturnRate"],
                            x["BenchmarkReturnRate"]
                        )[0,1] /
                        np.var(x["BenchmarkReturnRate"])
                        if len(x) > 1 and np.var(x["BenchmarkReturnRate"]) != 0
                        else 1.0
                    )
            )

            df["SharpRatio"] = (
                (df["AnnualReturnRate"] - self.riskFreeRate) /
                df["VolatalityPercent"].replace(0, np.nan)
            ).fillna(0)

            df["Alpha"] = (
                df["AnnualReturnRate"] -
                (
                    self.riskFreeRate +
                    df["Beta"] *
                    (df["BenchmarkReturnRate"] - self.riskFreeRate)
                )
            )

            df["GrowthFactor"] = (
                1 + (df["AnnualReturnRate"] / 100)
            )

            self.dataFrame = df

            print("Runtime metrics computed successfully")

        except Exception as exceptObj :
            raise RuntimeMetricComputationError(
                f"Error during runtime metric computation: {str(exceptObj)}"
            )

    def computeWeights(self) -> None :
        print(f"\nComputing dynamic weights...")

        rawWeight = (
            self.dataFrame["MarketCap"] *
            (1 + self.dataFrame["SharpRatio"].clip(lower = 0)) /
            (1 + self.dataFrame["VolatalityPercent"]) /
            (1 + self.dataFrame["ExpenseRatioPercent"])
        )

        self.dataFrame["Weight"] = rawWeight / rawWeight.sum()

        print(f"\nDynamic weight calculate completed successfully")

    def computeWeightedGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            df["WeightedLogGrowth"] = (
                df["Weight"] * np.log(df["GrowthFactor"])
            )

            resultDF = (
                df.groupby(["InvestmentID", "InvestmentName"])
                .agg(
                    Sector = ("Sector", "first"),
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
        self.validateReturnRates()
        self.computeRuntimeMetrics()
        self.computeWeights()

        resultDF = self.computeWeightedGeometricMean()
        resultDF.to_excel(self.outputFilePath, index=False)

        print(f"\nFinal output saved to: {self.outputFilePath}")

        resultDF.sort_values(
            "WeightedGeometricMeanReturnPercent",
            ascending = False
        ).plot(
            x = "InvestmentName",
            y = "WeightedGeometricMeanReturnPercent",
            kind = "bar",
            legend = False,
            title = "Weighted Geometric Mean Returns"
        )

        plt.tight_layout()
        plt.show()

if __name__ == "__main__" :
    inFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\InvestmentAnalytics.xlsx"
    outFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\EnhancedData\InvestmentAnalyticsEnhanced.xlsx"

    engine = InvestmentRuntimeWeightedGeometricMeanEngine(
        inputFilePath=inFilePath,
        outputFilePath=outFilePath
    )

    engine.run()