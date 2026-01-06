import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List

class DataFileNotFoundError(Exception) :
    pass


class DataSetEmptyError(Exception) :
    pass


class NumericFeatureNotFoundError(Exception) :
    pass

class RetailSalesAMEngine :
    def __init__(self, inlFilePath : str) :
        self.inlFilePath = inlFilePath
        self.dataFrame : pd.DataFrame | None = None
        self.numericFeatures : List[str] = []

    def loadData(self) -> None :
        if not os.path.exists(self.inlFilePath) :
            raise DataFileNotFoundError(
                f"Fatal Error! Dataset Not Found At : {self.inlFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inlFilePath)

        if self.dataFrame.empty :
            raise DataSetEmptyError("Fatal Error! Dataset Contains No Records.")

    def identifyNumericFeatures(self) -> None :
        if self.dataFrame is None :
            raise DataSetEmptyError("Dataset Must Be Loaded Before Analysis.")

        self.numericFeatures = self.dataFrame.select_dtypes(
            include = ["int64", "float64"]
        ).columns.tolist()

        if "OrderID" in self.numericFeatures :
            self.numericFeatures.remove("OrderID")

        if not self.numericFeatures :
            raise NumericFeatureNotFoundError(
                "No Numeric Features Found For Arithmetic Mean Calculation."
            )

    def calculateArithmeticMean(self) -> pd.DataFrame :
        meanResults = {
            outFeature : self.dataFrame[outFeature].mean()
            for outFeature in self.numericFeatures
        }

        return pd.DataFrame(
            meanResults.items(),
            columns = ["FeatureName", "ArithmeticMean"]
        ).sort_values(by = "ArithmeticMean", ascending = False)

class RetailSalesAMVisualization :
    @staticmethod
    def plotMeanValues(inMeanDataFrame : pd.DataFrame) -> None :
        plt.figure(figsize = (14, 6))
        plt.bar(
            inMeanDataFrame["FeatureName"],
            inMeanDataFrame["ArithmeticMean"]
        )
        plt.xticks(rotation = 60)
        plt.title("Arithmetic Mean of Retail Sales Numeric Features")
        plt.xlabel("Feature")
        plt.ylabel("Mean Value")
        plt.grid(axis = "y")
        plt.tight_layout()
        plt.show()

    @staticmethod
    def plotCorrelationHeatmap(
        inDataFrame : pd.DataFrame,
        inNumericFeatures : List[str]
    ) -> None :
        correlationMatrix = inDataFrame[inNumericFeatures].corr()

        plt.figure(figsize = (14, 10))
        sns.heatmap(
            correlationMatrix,
            annot = False,
            cmap = "viridis",
            linewidths = 0.5
        )
        plt.title("Retail Sales Feature Correlation Heatmap")
        plt.tight_layout()
        plt.show()

class RetailSalesAMApp :
    @staticmethod
    def run() -> None :
        try :
            inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\001_ArithmeticMean\DataSets\RetailSalesRecords.xlsx"

            retailEngineObject = RetailSalesAMEngine(inFilePath)

            retailEngineObject.loadData()
            retailEngineObject.identifyNumericFeatures()

            meanDataFrame = retailEngineObject.calculateArithmeticMean()

            print(
                "\n----------------Arithmetic Mean Results "
                "(Retail Sales Domain)----------------\n"
            )
            print(meanDataFrame)

            RetailSalesAMVisualization.plotMeanValues(meanDataFrame)
            RetailSalesAMVisualization.plotCorrelationHeatmap(
                retailEngineObject.dataFrame,
                retailEngineObject.numericFeatures
            )

            RetailSalesAMApp.printInterpretation(meanDataFrame)

        except Exception as exceptObject :
            print(f"\nFatal Error! {exceptObject}")

    @staticmethod
    def printInterpretation(inMeanDataFrame : pd.DataFrame) -> None :
        print(
            "\n----------------Data Scientist Interpretation "
            "(Retail AI Context)----------------\n"
        )

        for _, outRow in inMeanDataFrame.iterrows() :
            print(
                f"- Average {outRow['FeatureName']} is "
                f"{outRow['ArithmeticMean']:.2f}, serving as a "
                f"baseline indicator of customer purchasing behavior."
            )

if __name__ == "__main__" :
    RetailSalesAMApp.run()
