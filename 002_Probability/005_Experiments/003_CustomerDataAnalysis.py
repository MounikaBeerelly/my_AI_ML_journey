import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
from typing import Optional

class DataLoadError(Exception) :
    pass

class InvalidDataFormatError(Exception) :
    pass

class ExperimentConfigurationError(Exception) :
    pass

class CustomerDataLoader :

    REQUIRED_COLUMNS = [
        "timestamp",
        "user_id",
        "age_group",
        "region",
        "session_duration_sec",
        "ad_impressions",
        "click_through_rate",
        "discount_seen",
        "product_category",
        "converted"
    ]

    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.dataFrame: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame :
        try :
            self.dataFrame = pd.read_excel(self.inFilePath)
        except Exception as exceptObject:
            raise DataLoadError(f"Fatal Error! Unable To Load Excel File : {exceptObject}")

        missingColumns = [
            outColumn for outColumn in self.REQUIRED_COLUMNS
            if outColumn not in self.dataFrame.columns
        ]

        if missingColumns :
            raise InvalidDataFormatError(f"Fatal Error! Missing Required Columns : {missingColumns}")

        return self.dataFrame

class CustomerConversionExperiment :

    def __init__(self, dataFrame : pd.DataFrame, inTrials : int = 1000) :
        if inTrials <= 0:
            raise ExperimentConfigurationError("Fatal Error! Trials Must Be A Positive Integer.")

        self.dataFrame = dataFrame
        self.inTrials = inTrials
        self.conversionProbability: Optional[float] = None
        self.summaryReport: Optional[dict] = None

    def computeEmpiricalProbability(self) :
        try :
            totalRecords = len(self.dataFrame)
            totalConversions = self.dataFrame["converted"].sum()
            self.conversionProbability = totalConversions / totalRecords
        except Exception as exceptObject :
            raise InvalidDataFormatError(
                f"Fatal Error! Failed Probability Computation : {exceptObject}"
            )

    def run(self) -> float :
        if self.conversionProbability is None :
            self.computeEmpiricalProbability()

        successCount = 0

        for _ in range(self.inTrials) :
            if random.random() < self.conversionProbability :
                successCount += 1

        estimatedProbability = successCount / self.inTrials
        self._generateSummaryReport(estimatedProbability)

        return estimatedProbability

    def _generateSummaryReport(self, estimatedProbability : float) :
        ageConversion = (
            self.dataFrame.groupby("age_group")["converted"]
            .mean().round(4)
            .to_dict()
        )

        regionConversion = (
            self.dataFrame.groupby("region")["converted"]
            .mean().round(4)
            .to_dict()
        )

        categoryConversion = (
            self.dataFrame.groupby("product_category")["converted"]
            .mean().round(4)
            .to_dict()
        )

        self.summaryReport = {
            "estimated_conversion_probability" : round(estimatedProbability, 4),
            "conversion_by_age_group" : ageConversion,
            "conversion_by_region" : regionConversion,
            "conversion_by_product_category" : categoryConversion,
            "overall_records" : len(self.dataFrame)
        }

    def getSummaryReport(self) -> dict :
        return self.summaryReport

class CustomerChartGenerator :

    def __init__(self, dataFrame : pd.DataFrame) :
        sns.set(style = "whitegrid")
        self.dataFrame = dataFrame

    def plotConversionDistribution(self) :
        plt.figure(figsize = (7, 5))
        sns.countplot(x="converted", data = self.dataFrame)
        plt.title("Conversion Distribution")
        plt.show()

    def plotSessionDurationVsConversion(self) :
        plt.figure(figsize = (7, 5))
        sns.scatterplot(
            x = "session_duration_sec",
            y = "click_through_rate",
            hue = "converted",
            data = self.dataFrame,
            palette = "coolwarm"
        )
        plt.title("Session Duration Versus CTR (Conversion Coloring)")
        plt.show()

    def plotCategoryConversion(self) :
        plt.figure(figsize = (10, 5))
        sns.barplot(
            x = "product_category",
            y = "converted",
            data = self.dataFrame,
            estimator = lambda x : sum(x) / len(x)
        )
        plt.title("Conversion Rate by Product Category")
        plt.xticks(rotation = 90)
        plt.show()

class CustomerExperimentController :

    def __init__(self, inFilePath : str, inTrials : int) :
        self.inFilePath = inFilePath
        self.inTrials = inTrials
        self.dataFrame : Optional[pd.DataFrame] = None
        self.experimentResult : Optional[float] = None
        self.summaryReport : Optional[dict] = None

    def execute(self) :
        try :
            loader = CustomerDataLoader(self.inFilePath)
            self.dataFrame = loader.load()

            experiment = CustomerConversionExperiment(self.dataFrame, self.inTrials)
            self.experimentResult = experiment.run()
            self.summaryReport = experiment.getSummaryReport()

            charts = CustomerChartGenerator(self.dataFrame)
            charts.plotConversionDistribution()
            charts.plotSessionDurationVsConversion()
            charts.plotCategoryConversion()

        except Exception as exceptObject :
            print(f"Fatal Error! : {exceptObject}")

    def getSummary(self) :
        return self.summaryReport

def main():
    print(f"--------------------------Customer Conversion Experiment Runner--------------------------")

    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\005_Experiments\DataSets\CustomerConversionData.xlsx"
    inTrials = 5000

    controllerObject = CustomerExperimentController(inFilePath, inTrials)
    controllerObject.execute()

    outSummary = controllerObject.getSummary()

    if outSummary :
        print("\n-------------------------Presenting Experiment Summary-------------------------")
        print(f"Estimated Conversion Probability : {outSummary['estimated_conversion_probability']}")
        print(f"Total Records : {outSummary['overall_records']}")

        print("\nConversion Rate by Age Group...")
        for age, rate in outSummary["conversion_by_age_group"].items():
            print(f"{age} : {rate}")

        print("\nConversion Rate by Region...")
        for region, rate in outSummary["conversion_by_region"].items():
            print(f"{region} : {rate}")

        print("\nConversion Rate by Product Category...")
        for category, rate in outSummary["conversion_by_product_category"].items():
            print(f"{category} : {rate}")


if __name__ == "__main__":
    main()
