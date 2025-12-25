import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class EcommerceDataLoadError(Exception) :
    pass

class EcommerceDataLoader :

    def __init__(self, inFilePath) :
        self.inFilePath = inFilePath

    def loadData(self) :
        try :
            outDataFrame = pd.read_excel(self.inFilePath)
        except Exception as error :
            raise EcommerceDataLoadError(str(error))

        self._validateData(outDataFrame)
        return outDataFrame

    def _validateData(self, inDataFrame) :
        if "Delivery_Delay_Days" not in inDataFrame.columns :
            raise EcommerceDataLoadError(
                "Missing Required Column : Delivery_Delay_Days"
            )

        if inDataFrame["Delivery_Delay_Days"].isnull().any() :
            raise EcommerceDataLoadError(
                "Null Values Found in Delivery Delay Days"
            )

        if not np.issubdtype(
            inDataFrame["Delivery_Delay_Days"].dtype,
            np.integer
        ) :
            raise EcommerceDataLoadError(
                "Delivery Delay Days Must Be Integer"
            )

class ProbabilityFrequencyDistributionEngine :
    def __init__(self, inDelaySeries, inNumberOfBins = 7) :
        self.inDelaySeries = inDelaySeries
        self.inNumberOfBins = inNumberOfBins

    def computeDistribution(self) :
        frequency, binEdges = np.histogram(
            self.inDelaySeries,
            bins = self.inNumberOfBins
        )

        classIntervals = [
            f"{int(binEdges[binIndex])} - {int(binEdges[binIndex + 1])}"
            for binIndex in range(len(binEdges) - 1)
        ]

        distributionDF = pd.DataFrame({
            "Class_Interval" : classIntervals,
            "Frequency" : frequency
        })

        distributionDF["Probability"] = (
            distributionDF["Frequency"] /
            distributionDF["Frequency"].sum()
        )

        distributionDF["Cumulative_Probability"] = (
            distributionDF["Probability"].cumsum()
        )

        return distributionDF

class EcommerceMLInsightsEngine :

    def __init__(self, inDistributionDF) :
        self.inDistributionDF = inDistributionDF

    def highDelayRiskIntervals(self, threshold = 0.15) :
        return self.inDistributionDF[
            self.inDistributionDF["Probability"] >= threshold
        ]

    def maxDelayRiskInterval(self) :
        return self.inDistributionDF.loc[
            self.inDistributionDF["Probability"].idxmax(),
            "Class_Interval"
        ]

class EcommerceVisualization :
    @staticmethod
    def plotHistogram(delaySeries) :
        plt.figure()
        plt.hist(delaySeries, bins = 7)
        plt.xlabel("Delivery Delay (Days)")
        plt.ylabel("Frequency")
        plt.title("Delivery Delay Distribution (Histogram)")
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
        plt.xlabel("Class Interval (Days)")
        plt.ylabel("Probability")
        plt.title("Probability Frequency Distribution of Delivery Delays")
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
        plt.xlabel("Class Interval (Days)")
        plt.ylabel("Cumulative Probability")
        plt.title("Cumulative Probability of Delivery Delays")
        plt.grid(True)
        plt.show()

def main() :
    try :
        inFilePath = r""
     
        loader = EcommerceDataLoader(inFilePath = inFilePath)
        ecommerceDataFrame = loader.loadData()

        distributionEngine = ProbabilityFrequencyDistributionEngine(
            ecommerceDataFrame["Delivery_Delay_Days"],
            inNumberOfBins = 7
        )

        distributionDF = distributionEngine.computeDistribution()

        insightsEngine = EcommerceMLInsightsEngine(distributionDF)   
        
        print("\n---------------- E-Commerce Delivery Delay Distribution ----------------\n")
        print(distributionDF.to_string(index = False))

        print("\nHigh Delay Risk Class Intervals :\n")
        print(insightsEngine.highDelayRiskIntervals())

        print("\nMaximum Delay Risk Interval :",
              insightsEngine.maxDelayRiskInterval())

        EcommerceVisualization.plotHistogram(
            ecommerceDataFrame["Delivery_Delay_Days"]
        )

        EcommerceVisualization.plotProbabilityDistribution(
            distributionDF
        )

        EcommerceVisualization.plotCumulativeProbability(
            distributionDF
        )

    except EcommerceDataLoadError as errorObject :
        print("Data Error :", errorObject)

    except Exception as errorObject :
        print("Unexpected System Error :", errorObject)
        
if __name__ == "__main__" :
    main()
