import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class BankingDataLoadError(Exception) :
    pass

class BankingDataLoader :

    def __init__(self, inFilePath) :
        self.inFilePath = inFilePath

    def loadData(self) :
        try :
            outDataFrame = pd.read_excel(self.inFilePath)
        except Exception as error :
            raise BankingDataLoadError(str(error))

        self._validateData(outDataFrame)
        return outDataFrame

    def _validateData(self, inDataFrame) :
        requiredColumns = [
            "Transaction_Amount",
            "Fraud_Flag"
        ]

        for outColumn in requiredColumns :
            if outColumn not in inDataFrame.columns :
                raise BankingDataLoadError(
                    f"Missing Required Column : {outColumn}"
                )

        if inDataFrame["Transaction_Amount"].isnull().any() :
            raise BankingDataLoadError(
                "Null Values Found in Transaction Amount"
            )

class FraudTransactionFilter :

    def __init__(self, inDataFrame) :
        self.inDataFrame = inDataFrame

    def getFraudTransactions(self) :
        fraudDF = self.inDataFrame[
            self.inDataFrame["Fraud_Flag"] == 1
        ]

        if fraudDF.empty :
            raise BankingDataLoadError(
                "No Fraud Transactions Found"
            )

        return fraudDF

class ProbabilityFrequencyDistributionEngine :

    def __init__(self, inAmountSeries, inNumberOfBins = 10) :
        self.inAmountSeries = inAmountSeries
        self.inNumberOfBins = inNumberOfBins

    def computeDistribution(self) :
        frequency, binEdges = np.histogram(
            self.inAmountSeries,
            bins = self.inNumberOfBins
        )

        classIntervals = [
            f"{int(binEdges[binIndex])} - {int(binEdges[binIndex + 1])}"
            for binIndex in range(len(binEdges) - 1)
        ]

        distributionDF = pd.DataFrame({
            "Class_Interval" : classIntervals,
            "Fraud_Transaction_Count" : frequency
        })

        distributionDF["Probability"] = (
            distributionDF["Fraud_Transaction_Count"] /
            distributionDF["Fraud_Transaction_Count"].sum()
        )

        distributionDF["Cumulative_Probability"] = (
            distributionDF["Probability"].cumsum()
        )

        return distributionDF

class BankingFraudInsightsEngine :

    def __init__(self, inDistributionDF) :
        self.inDistributionDF = inDistributionDF

    def highRiskAmountIntervals(self, threshold = 0.20) :
        return self.inDistributionDF[
            self.inDistributionDF["Probability"] >= threshold
        ]

    def maxFraudRiskInterval(self) :
        return self.inDistributionDF.loc[
            self.inDistributionDF["Probability"].idxmax(),
            "Class_Interval"
        ]

    def fraudCoverageThreshold(self, coverage = 0.80) :
        return self.inDistributionDF[
            self.inDistributionDF["Cumulative_Probability"] >= coverage
        ].iloc[0]["Class_Interval"]

class BankingFraudVisualization :

    @staticmethod
    def plotHistogram(amountSeries) :
        plt.figure()
        plt.hist(amountSeries, bins = 10)
        plt.xlabel("Fraud Transaction Amount")
        plt.ylabel("Count")
        plt.title("Histogram of Fraud Transaction Amounts")
        plt.grid(True)
        plt.show()

    @staticmethod
    def plotProbabilityDistribution(distributionDF) :
        plt.figure()
        plt.plot(
            distributionDF["Class_Interval"],
            distributionDF["Probability"],
            marker = "o"
        )
        plt.xticks(rotation = 45)
        plt.xlabel("Fraud Amount Class Interval")
        plt.ylabel("Probability")
        plt.title("Probability Distribution of Fraud Amounts")
        plt.grid(True)
        plt.show()

    @staticmethod
    def plotCumulativeProbability(distributionDF) :
        plt.figure()
        plt.plot(
            distributionDF["Class_Interval"],
            distributionDF["Cumulative_Probability"],
            marker = "o"
        )
        plt.xticks(rotation = 45)
        plt.xlabel("Fraud Amount Class Interval")
        plt.ylabel("Cumulative Probability")
        plt.title("Cumulative Probability of Fraud Amounts")
        plt.grid(True)
        plt.show()

def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\007_ProbabilityFrequencyDistribution\DataSets\BankTransactionData.xlsx"
        
        loader = BankingDataLoader(inFilePath = inFilePath)
        bankingDataFrame = loader.loadData()

        fraudFilter = FraudTransactionFilter(bankingDataFrame)
        fraudDataFrame = fraudFilter.getFraudTransactions()

        distributionEngine = ProbabilityFrequencyDistributionEngine(
            fraudDataFrame["Transaction_Amount"],
            inNumberOfBins = 10
        )

        distributionDF = distributionEngine.computeDistribution()

        insightsEngine = BankingFraudInsightsEngine(distributionDF) 

        print("\n---------------- Banking Fraud Amount Distribution ----------------\n")
        print(distributionDF.to_string(index = False))

        print("\nHigh Risk Fraud Amount Intervals :\n")
        print(insightsEngine.highRiskAmountIntervals())

        print("\nMaximum Fraud Risk Interval :",
              insightsEngine.maxFraudRiskInterval())

        print(
            "\nAmount Interval Covering 80% Fraud Transactions :",
            insightsEngine.fraudCoverageThreshold()
        )

        BankingFraudVisualization.plotHistogram(
            fraudDataFrame["Transaction_Amount"]
        )

        BankingFraudVisualization.plotProbabilityDistribution(
            distributionDF
        )

        BankingFraudVisualization.plotCumulativeProbability(
            distributionDF
        )

    except BankingDataLoadError as errorObject :
        print("Data Error :", errorObject)

    except Exception as errorObject :
        print("Unexpected System Error :", errorObject)


if __name__ == "__main__" :
    main()      
               