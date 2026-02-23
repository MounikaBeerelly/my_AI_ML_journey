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

class InvalidMetricRateError(Exception) :
    pass

class GeometricMeanComputationError(Exception) :
    pass

class CampaignPerformanceGeometricMeanEngine :
    """
    Computes Simple Geometric Mean of Campaign Performance Metrics To Evaluate True Marketing Growth
    """

    def __init__(self, inputFilePath : str) -> None :
        self.inputFilePath = inputFilePath
        self.dataFrame : pd.DataFrame | None = None

        self.requiredColumns = [
            "CampaignID",
            "Date",
            "MetricType",
            "MetricGrowthRate",
            "Channel",
            "BudgetBucket"
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
        for column in self.requiredColumns :
            if column not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required Column Missing : {column}"
                )

        print("Dataset Schema Validation Successful")

    def validateRates(self) -> None :
        if (self.dataFrame["MetricGrowthRate"] <= -100).any() :
            raise InvalidMetricRateError(
                "Fatal Error! MetricGrowthRate Must Be Greater Than -100%"
            )

        print("Metric Rate Validation Successful")

    def computeGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            print("\nConverting Percentage Metrics To Growth Factors...")
            df["GrowthFactor"] = 1 + (df["MetricGrowthRate"] / 100)

            resultDF = (
                df.groupby(["CampaignID", "MetricType"])
                .agg(
                    Channel = ("Channel", "first"),
                    BudgetBucket = ("BudgetBucket", "first"),
                    Days = ("Date", "count"),
                    GeometricMeanGrowth = (
                        "GrowthFactor",
                        lambda x : np.exp(np.mean(np.log(x)))
                    )
                )
                .reset_index()
            )

            resultDF["GeometricMeanMetricGrowth"] = (
                (resultDF["GeometricMeanGrowth"] - 1) * 100
            )

            print("Geometric Mean Computation Completed Successfully")

            return resultDF

        except Exception as exceptObject :
            raise GeometricMeanComputationError(
                f"Fatal Error! GM Computation Failed : {exceptObject}"
            )

    def plotGeometricMean(self, resultDF : pd.DataFrame) -> None :
        plotDF = resultDF.sort_values(
            by="GeometricMeanMetricGrowth",
            ascending=True
        )

        plt.figure(figsize=(10, max(5, len(plotDF) * 0.4)))

        plt.barh(
            plotDF["CampaignID"].astype(str) + " | " + plotDF["MetricType"],
            plotDF["GeometricMeanMetricGrowth"]
        )

        plt.xlabel("Geometric Mean Metric Growth (%)")
        plt.ylabel("Campaign | Metric")
        plt.title("Campaign Performance Growth (Geometric Mean)")
        plt.tight_layout()
        plt.show()

def main() -> None :
    try :
        inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\DataSets\CampaignPerformanceRecords.xlsx"
        

        campaignEngine = CampaignPerformanceGeometricMeanEngine(inputFilePath)

        campaignEngine.loadDataset()
        campaignEngine.validateSchema()
        campaignEngine.validateRates()

        resultDF = campaignEngine.computeGeometricMean()

        print("\nFinal Campaign Performance Geometric Mean Output")
        print(resultDF)

        campaignEngine.plotGeometricMean(resultDF)

    except (
        DatasetNotFoundError,
        DatasetEmptyError,
        InvalidSchemaError,
        InvalidMetricRateError,
        GeometricMeanComputationError
    ) as knownException :
        print(f"\nApplication Failed : {knownException}")

    except Exception as unknownException :
        print(f"\nUnexpected System Error : {unknownException}")


if __name__ == "__main__" :
    main()        