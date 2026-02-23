import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class BankingDataLoadError(Exception) :
    pass

class BankingDataLoader :
    
    def __init__(self, inFilePath):
        self.inFilePath = inFilePath
        
    def loadData(self) :
        try :
            outDataFrame = pd.read_excel(self.inFilePath)
        except Exception as error :
            raise BankingDataLoader(str(error))
        
        self._validateData(outDataFrame)
        return outDataFrame
    
    def _validateData(Self, inDataFrame) :
        if "Transaction_Amount" not in inDataFrame.columns :
            raise BankingDataLoadError(
                "Missing Required column : Transaction_Amount"
            )
             
        if inDataFrame["Transaction_Amount"].isnull().any() :
            raise BankingDataLoadError(
                "Null values found in Transaction Amount"
            )

class ProbabilityFrequencyDistributionEngine :
    def __init__(self, inTransactionSeries, inNumberOfbins = 10):
        self.inTransactionSeries = inTransactionSeries
        self.inNumberOfBins = inNumberOfbins
    
    def computeDistribution(self) :
        frequency, binEdges = np.histogram(
            self.inTransactionSeries,
            bins = self.inNumberOfBins
        )
        
        classIntervals = [
            f"{round(binEdges[binIndex], 2)} - {round(binEdges[binIndex + 1], 2)}"
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
    
class BankingMLInsightsEngine :
    
    def __init__(self, inDistributionDF):
        self.inDistributionDF = inDistributionDF
        
    def highRiskIntervals(self, threshold = 0.15) :
        return self.inDistributionDF[
            self.inDistributionDF["Probability"] >= threshold
        ]
        
    def maxRiskInterval(self) :
        return self.inDistributionDF.loc[
            self.inDistributionDF["Probability"].idxmax(),
            "Class_Interval"
        ]
        
class BankingVisualization :
    
    @staticmethod
    def plotHistogram(transactionSeries) :
        plt.figure()
        plt.hist(transactionSeries, bins = 10)
        plt.xlabel("Transaction Amount")
        plt.ylabel("Frequency")
        plt.title("Transaction Amount Distribution")
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
        plt.xlabel("Class Interval")
        plt.ylabel("Cumulative Probability")
        plt.title("Cumulative Probability Distribution")
        plt.grid(True)
        plt.show()
        
def main() :
    try : 
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\007_ProbabilityFrequencyDistribution\DataSets\BankTransactionData.xlsx"
        
        loader = BankingDataLoader(inFilePath = inFilePath)
        bankingDataFrame = loader.loadData()
        
        distributionEngine = ProbabilityFrequencyDistributionEngine(
            bankingDataFrame["Transaction_Amount"],
            inNumberOfbins = 10
        )
        
        distributionDF = distributionEngine.computeDistribution()
        
        insightsEngine = BankingMLInsightsEngine(distributionDF)
        
        print("\n----Banking Probability distributionEngine----\n")
        print(distributionDF.to_string(index = False))
        
        print("\nHigh risk class intervals :\n")
        print(insightsEngine.highRiskIntervals())
        
        print("\nMaximum risk Interval :",
              insightsEngine.maxRiskInterval())
        
        BankingVisualization.plotHistogram(
            bankingDataFrame["Transaction_Amount"]
        )
        
        BankingVisualization.plotCumulativeProbability(
            distributionDF
        )
    except BankingDataLoadError as errorObject :
        print("Data Error : ", errorObject)
    except Exception as exceptionObject :
        print("Unexpected System error : ", exceptionObject)
        
if __name__ == "__main__":
    main()