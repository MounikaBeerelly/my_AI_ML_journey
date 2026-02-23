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

class NetworkDataLoader :

    REQUIRED_COLUMNS = [
        "timestamp",
        "device_id",
        "connection_type",
        "signal_strength",
        "latency_ms",
        "jitter_ms",
        "network_load_percent",
        "packet_success"
    ]

    def __init__(self, inFilePath: str) :
        self.inFilePath = inFilePath
        self.dataFrame: Optional[pd.DataFrame] = None

    def load(self) -> pd.DataFrame :
        try :
            self.dataFrame = pd.read_excel(self.inFilePath)
        except Exception as exceptObject :
            raise DataLoadError(f"Fatal Error! Unable To Load Excel File : {exceptObject}")

        missingColumns = [
            outColumn for outColumn in self.REQUIRED_COLUMNS
            if outColumn not in self.dataFrame.columns
        ]

        if missingColumns :
            raise InvalidDataFormatError(f"Fatal Error! Missing Required Columns : {missingColumns}")

        return self.dataFrame

class NetworkProbabilityExperiment :

    def __init__(self, dataFrame : pd.DataFrame, inTrials : int = 1000) :
        if inTrials <= 0 :
            raise ExperimentConfigurationError("Fatal Error! Trials Must Be A Positive Integer.")

        self.dataFrame = dataFrame
        self.inTrials = inTrials
        self.successProbability : Optional[float] = None
        self.summaryReport : Optional[dict] = None

    def computeEmpiricalProbability(self) :
        try :
            totalRecords = len(self.dataFrame)
            totalSuccess = self.dataFrame["packet_success"].sum()
            self.successProbability = totalSuccess / totalRecords
        except Exception as exceptObject :
            raise InvalidDataFormatError(
                f"Fatal Error! Failed Probability Computation : {exceptObject}"
            )

    def run(self) -> float :
        if self.successProbability is None :
            self.computeEmpiricalProbability()

        successCount = 0

        for _ in range(self.inTrials) :
            if random.random() < self.successProbability:
                successCount += 1

        estimatedProbability = successCount / self.inTrials
        self._generateSummaryReport(estimatedProbability)

        return estimatedProbability

    def _generateSummaryReport(self, estimatedProbability : float) :
        deviceSuccess = (
            self.dataFrame.groupby("device_id")["packet_success"]
            .mean().round(4)
            .to_dict()
        )

        connectionSuccess = (
            self.dataFrame.groupby("connection_type")["packet_success"]
            .mean().round(4)
            .to_dict()
        )

        self.summaryReport = {
            "estimated_probability" : round(estimatedProbability, 4),
            "device_success_rates" : deviceSuccess,
            "connection_success_rates" : connectionSuccess,
            "overall_records" : len(self.dataFrame)
        }

    def getSummaryReport(self) -> dict :
        return self.summaryReport

class NetworkChartGenerator :

    def __init__(self, dataFrame : pd.DataFrame) :
        sns.set(style = "whitegrid")
        self.dataFrame = dataFrame

    def plotSignalStrengthDistribution(self) :
        plt.figure(figsize = (7, 5))
        sns.histplot(self.dataFrame["signal_strength"], kde = True, bins = 40)
        plt.title("Signal Strength Distribution")
        plt.show()

    def plotLatencyVsSuccess(self) :
        plt.figure(figsize = (7, 5))
        sns.scatterplot(
            x = "latency_ms", y = "jitter_ms",
            hue = "packet_success",
            data = self.dataFrame, palette = "coolwarm"
        )
        plt.title("Latency vs Jitter (Success Coloring)")
        plt.show()

    def plotConnectionSuccessRate(self) :
        plt.figure(figsize = (7, 5))
        sns.barplot(
            x = "connection_type", y = "packet_success",
            data = self.dataFrame, estimator = lambda x : sum(x) / len(x)
        )
        plt.title("Connection-Type Success Rate")
        plt.show()

class NetworkExperimentController :

    def __init__(self, inFilePath : str, inTrials : int) :
        self.inFilePath = inFilePath
        self.inTrials = inTrials
        self.dataFrame : Optional[pd.DataFrame] = None
        self.experimentResult : Optional[float] = None
        self.summaryReport : Optional[dict] = None

    def execute(self) :
        try :
            loader = NetworkDataLoader(self.inFilePath)
            self.dataFrame = loader.load()

            experiment = NetworkProbabilityExperiment(self.dataFrame, self.inTrials)
            self.experimentResult = experiment.run()
            self.summaryReport = experiment.getSummaryReport()

            charts = NetworkChartGenerator(self.dataFrame)
            charts.plotSignalStrengthDistribution()
            charts.plotLatencyVsSuccess()
            charts.plotConnectionSuccessRate()

        except Exception as exceptObject:
            print(f"Fatal Error! : {exceptObject}")

    def getSummary(self) :
        return self.summaryReport

def main() :
    import argparse

    print(f"--------------------------Network Probability Experiment Runner--------------------------")

    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\005_Experiments\DataSets\NetworkPacketData.xlsx"
    inTrials = 5000

    controllerObject = NetworkExperimentController(inFilePath, inTrials)
    controllerObject.execute()

    outSummary = controllerObject.getSummary()
    if outSummary :
        print("\n-------------------------Presenting Experiment Summary-------------------------")
        print(f"Estimated Packet Success Probability : {outSummary['estimated_probability']}")
        print(f"Total Records : {outSummary['overall_records']}")
        print("\nSuccess Rate by Device...")

        for outDevice, outRate in outSummary["device_success_rates"].items() :
            print(f"{outDevice} : {outRate}")

        print(f"\nSuccess Rate By Connection Type...")
        for outConnection, outRate in outSummary["connection_success_rates"].items() :
            print(f"{outConnection} : {outRate}")

if __name__ == "__main__" :
    main()