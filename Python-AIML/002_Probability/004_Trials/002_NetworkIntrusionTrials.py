import os
import pandas as pd
import matplotlib.pyplot as plt
import random
from typing import List
from tabulate import tabulate

class DataLoadingError(Exception) :
    pass

class InvalidTrialError(Exception) :
    pass

class NetworkRecord :
    def __init__(
        self,
        request_id : str,
        is_intrusion : bool,
        packet_size_kb : float,
        protocol : str,
        server_id : str,
        timestamp
    ) :
        self.request_id = request_id
        self.is_intrusion = is_intrusion
        self.packet_size_kb = packet_size_kb
        self.protocol = protocol
        self.server_id = server_id
        self.timestamp = timestamp
        
class NetworkDataSet : 
    REQUIRED_COLUMNS = {
        "request_id",
        "is_intrusion",
        "packet_size_kb",
        "protocol",
        "server_id",
        "timestamp"
    }
    
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.records : List[NetworkRecord] = []
    
    def load(self) -> None :
        try :
            df = pd.read_excel(self.inFilePath)
        except Exception as exceptObject :
            raise DataLoadingError(f"Fatal Error! Failed to read the excel file : {exceptObject}\n")
        
        if not self.REQUIRED_COLUMNS.issubset(df.columns) :
            missingColumns = self.REQUIRED_COLUMNS - set(df.columns)
            raise DataLoadingError(f"Fatal Error! Missing the Required columns for analysis : {missingColumns}\n")
        
        for _, outRecord in df.iterrows() :
            networkRecord = NetworkRecord(
                request_id = str(outRecord["request_id"]),
                is_intrusion = bool(outRecord["is_intrusion"]),
                packet_size_kb = float(outRecord["packet_size_kb"]),
                protocol = str(outRecord["protocol"]),
                server_id = str(outRecord["server_id"]),
                timestamp = outRecord["timestamp"]
            )
            self.records.append(networkRecord)
            
    def getIntrusionProbability(self) -> float :
        if not self.records :
            raise DataLoadingError("Fatal Error! Network Dataset is empty...")
        
        intrusionCount = sum(1 for outRecord in self.records if outRecord.is_intrusion) 
        return intrusionCount / len(self.records)
    
    def getServerWiseProbabilities(self) -> dict :
        networkDataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        outStatistics = networkDataFrame.groupby("server_id")["is_intrusion"].mean().to_dict()
        return outStatistics
    
    def getProtocolWiseProbabilities(self) -> dict :
        networkDataFrame = pd.DataFrame([vars(outRecord) for outRecord in self.records])
        outStatistics = networkDataFrame.groupby("protocol")["is_intrusion"].mean().to_dict()
        return outStatistics
    
class ProbabilityTrial :
    def __init__(self, inProbability : float):
        if not (0 <= inProbability <= 1) :
            raise InvalidTrialError("Fatal Error! Probability must be in between 0 and 1")
        self.inProbability = inProbability
        
    def run(self) -> bool :
        return random.random() < self.inProbability
    
class TrialRunner :
    def __init__(self, inNumTrials : int, inTrial : ProbabilityTrial):
        if inNumTrials <= 0 :
            raise InvalidTrialError("Fatal Error! The input for number of trials must be positive")
        
        self.inNumTrials = inNumTrials
        self.inTrial = inTrial
        self.trialResults : List[bool] = []
        
    def executeTrials(self) -> None :
        for _ in range(self.inNumTrials) :
            trialOutCome = self.inTrial.run()
            self.trialResults.append(trialOutCome)
    
    def generateSummary(self) -> dict :
        intrusionCount = sum(self.trialResults)
        
        return {
            "totalTrials" : self.inNumTrials,
            "intrusionCount" : intrusionCount,
            "benignCount" : self.inNumTrials - intrusionCount,
            "estimatedIntrusionProbability" : intrusionCount / self.inNumTrials
        }
        
class NetworkingCharts :
    
    @staticmethod
    def plotServerWiseIntrusions(serverWiseStats : dict) -> None :
        servers = list(serverWiseStats.keys())
        probabilities = list(serverWiseStats.values())
        
        plt.figure(figsize = (10,5))
        plt.bar(servers, probabilities)
        plt.title("Server-wise Intrusion Probabilities")
        plt.xlabel("Server ID")
        plt.ylabel("Intrusion Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
    @staticmethod
    def plotProtocolWiseIntrusions(protocolWiseStats : dict) -> None :
        protocols = list(protocolWiseStats.keys())
        probabilities = list(protocolWiseStats.values())
        
        plt.figure(figsize = (10, 5))
        plt.bar(protocols, probabilities, color = "orange")
        plt.title("Protocol-Wise Intrusion Probabilities")
        plt.xlabel("Protocol")
        plt.ylabel("Intrusion Probability")
        plt.grid(axis = "y", linestyle = "--", alpha = 0.6)
        plt.tight_layout()
        plt.show()
        
def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\004_Trials\DataSets\NetworkLogs.xlsx"
        networkingData = NetworkDataSet(inFilePath)
        networkingData.load()
        
        intrusionProbability = networkingData.getIntrusionProbability()
        print(f"\nOverall Intrusion Probability is : {intrusionProbability : .4f}")
        
        serverProbability = networkingData.getServerWiseProbabilities()
        print(f"\nDisplaying Server-Wise Intrusion Probabilities...")
        outTable = [[outServer, f"{outProbability : .4f}"] for outServer, outProbability in serverProbability.items()]
        print(tabulate(outTable, headers = ["Server ID", "Probability"], tablefmt = "pretty", stralign ="right"))        
            
        protocolProbability = networkingData.getProtocolWiseProbabilities()
        print(f"\nDisplaying Protocol-Wise Intrusion Probabilities...")
        outTable = [[outProtocol, f"{outProbability : .4f}"] for outProtocol, outProbability in serverProbability.items()]
        print(tabulate(outTable, headers = ["Protocol", "Probability"], tablefmt = "pretty", stralign ="right"))        
        
        trial = ProbabilityTrial(inProbability = intrusionProbability)
        runner = TrialRunner(inNumTrials = 5000, inTrial = trial)
        runner.executeTrials()
        
        summary = runner.generateSummary()
        print("\nSimulated Trial Summary ...")
        outTable = [[outTrialKey, outValue] for outTrialKey, outValue in summary.items()]
        print(tabulate(outTable, headers = ["Name", "Value"], tablefmt = "pretty", stralign ="left"))        

        NetworkingCharts.plotServerWiseIntrusions(serverProbability)
        NetworkingCharts.plotProtocolWiseIntrusions(protocolProbability)
    except DataLoadingError as dataLoadingError :
        print(f"\nFatal Error! Encountered Issue While Loading The Data : {dataLoadingError}")
    except InvalidTrialError as invalidTrialError :
        print("\nFatal Error! Encountered Issue While Conducting The Trials: {invalidTrialError}")
    except Exception as exceptObject :
        print("\nFatal Error! Encountered Unexpected Error While Executing The Application...")
        print(f"Message From The Application : {exceptObject}")
        
if __name__ == "__main__":
    main()