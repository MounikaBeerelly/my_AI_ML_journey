import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TelecomDataLoadError(Exception) :
    pass

class TelecomDataLoader :
    
    def __init__(self, inFilePath):
        self.inFilePath = inFilePath
        
    def loadData(self) :
        try :
            outDataFrame = pd.read_excel(self.inFilePath)
        except Exception as error :
            raise TelecomDataLoadError(str(error))
        
        self._validateData(outDataFrame)
        return outDataFrame
    
    def _validateData(Self, inDataFrame) :
        requiredColumns = [
            "Timestamp",
            "Region",
            "Cell_ID",
            "Total_Calls",
            "Successful_Calls",
            "Call_Drops",
            "Network_Traffic_MB",
            "Signal_Strength_dBm",
            "Latency_ms",
            "Packet_Loss_Percent",
            "Customer_Complaints"
        ]
        
        for outColumn in requiredColumns :
            if outColumn not in inDataFrame.columns :
                raise TelecomDataLoadError(f"Missing Required Column : {outColumn}")
            
        if inDataFrame["Call_Drops"].isnull().any() :
            raise TelecomDataLoadError("Null values found in Call Drops")
        
        if not np.issubdtype(inDataFrame["Call_Drops"].dtype, np.integer) :
            raise TelecomDataLoadError("Call Drops must be Integer")
        
class ProbabilityFrequencyDistributionEngine :
    
    def __init__(self, inCallDropsSeries):
        self.inCallDropsSeries = inCallDropsSeries
        
    def computeDistribution(self) :
        distributionDF = (
            self.inCallDropsSeries
            .value_counts()
            .sort_index()
            .reset_index()
        )
        
        distributionDF.columns = [
            "Call_Drops_Per_Hour",
            "Frequency"
        ]
        
        distributionDF["Probability"] = (
            distributionDF["Frequency"] /
            distributionDF["Frequency"].sum()
        )
        
        return distributionDF
    
class TelecomInsightEngine :
    
    def __init__(self, inDistributionDF):
        self.inDistributionDF = inDistributionDF
        
    def mostLikelyCallDrops(self) :
        return self.inDistributionDF.loc[
            self.inDistributionDF["Probability"].idxmax(),
            "Call_Drops_Per_Hour"
        ]
        
    def highRiskProbability(self, threshold = 5) :
        return self.inDistributionDF.loc[
            self.inDistributionDF["Call_Drops_Per_Hour"] >= threshold,
            "Probability"
        ].sum()
        
    def networkStatus(self) :
        return (
            "Unstable" if self.highRiskProbability() > 0.4 else "Stable"
        )
        
class TelecomVisualization :
    
    @staticmethod 
    def plotProbabilityDistribution(distributionDF) :
        plt.figure()
        plt.bar(
            distributionDF["Call_Drops_Per_Hour"],
            distributionDF["Probability"]
        )
        plt.xlabel("Call Drops Per Hour")
        plt.ylabel("Probability")
        plt.title("Probability Frequency distribution of Telecom Call Drops")
        plt.grid(True)
        plt.show()
        
    def plotFrequencyDistribution(distributionDF) :
        plt.figure()
        plt.plot(
            distributionDF["Call_Drops_Per_Hour"],
            distributionDF["Frequency"],
            marker = "o"
        )
        plt.xlabel("Call Drops Per Hour")
        plt.ylabel("Frequency")
        plt.title("Frequency distribution of Telecom Call Drops")
        plt.grid(True)
        plt.show()
           
def main() :
    try:
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\007_ProbabilityFrequencyDistribution\DataSets\TelecomNetworkrecords.xlsx"
        
        loader = TelecomDataLoader(inFilePath = inFilePath)
        
        telecomDataFrame = loader.loadData()
        distributionengine = ProbabilityFrequencyDistributionEngine(telecomDataFrame["Call_Drops"])
        
        distributionDF = distributionengine.computeDistribution()
        insightsEngine = TelecomInsightEngine(distributionDF)
        
        print("\n----Telecom Probability Frequency Distribution---")
        print(distributionDF.to_string(index = False))
        
        print("Most Likely Call drops per Hour...", insightsEngine.mostLikelyCallDrops())
        print("Network Status : ", insightsEngine.networkStatus())
        
        TelecomVisualization.plotProbabilityDistribution(distributionDF)
        TelecomVisualization.plotFrequencyDistribution(distributionDF)
    except Exception as errorObject :
        print(f"Unexpected System Error.. {errorObject}")
        
if __name__ == "__main__" :
    main()