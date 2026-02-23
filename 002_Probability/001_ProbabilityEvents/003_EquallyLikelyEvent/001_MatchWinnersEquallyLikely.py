import pandas as pd
import matplotlib.pyplot as plt

class DataLoader :
    def __init__(self, inFilePath : str):
        self.inFilePath = inFilePath
        self.data = None
        
    def loadData(self) :
        try :
            self.data = pd.read_excel(self.inFilePath)
            print(f"\nData for analysis is loaded successfully...")
        except Exception as exceptObject:
            print(f"Fatal error! Unable to load the excel file : {exceptObject}")
            
        return self.data
    
class ProbabilityCalculator :
    def __init__(self, inData : pd.DataFrame):
        self.inData = inData
        self.probabilities = None
        
    def calculateProbabilities(self) :
        if "Winner" not in self.inData.columns :
            raise ValueError("Fatal Error! The loaded dataset must contain a 'Winner' column")
        
        totalMatches = len(self.inData)
        winningCounts = self.inData["Winner"].value_counts()
        self.probabilities = (winningCounts / totalMatches).reset_index()
        self.probabilities.columns = ["Team", "Probability"]
        
        print(f"\nProbability computations are completed")
        return self.probabilities
    
class probabilityVisualizer :
    def __init__(self, inProbabilities: pd.DataFrame):
        self.inProbabilities = inProbabilities
        
    def plotBarChart(self) :
        plt.figure(figsize = (10, 6))
        plt.bar(self.inProbabilities["Team"], self.inProbabilities["Probability"])
        plt.title("Probability of each team winning (Equally Likely Event)")
        plt.xlabel("Team")
        plt.ylabel("Probability")
        plt.xticks(rotation = 45)
        plt.grid(axis = 'y', linestyle = '--', alpha = 0.7)
        plt.tight_layout()
        plt.show()
        
    def plotPieChart(self) :
        plt.figure(figsize = (8, 8))
        plt.pie(
            self.inProbabilities["Probability"],
            labels = self.inProbabilities["Team"],
            autopct = "%1.2f%%",
            startangle = 90,
            shadow = True
        )
        plt.title("Winning Probabilities distribution across teams")
        plt.show()
        
class ProbabilityAnalysis :
    def __init__(self, inFilePath : str):
        self.inFilePath = inFilePath
        self.dataLoader = DataLoader(inFilePath)
        self.data = None
        self.probabilityCalculator = None
        self.probabilityVisualizer = None
        
    def runapplication(self) :
        self.data = self.dataLoader.loadData()
        
        if self.data is None or self.data.empty :
            print(f"\nFatal Error! There is no data to process..")
            return
        
        print(f"\nSample data for Analysis id loaded....")
        print(self.data.head)
        
        self.probabilityCalculator = ProbabilityCalculator(self.data)
        outProbabilities = self.probabilityCalculator.calculateProbabilities()
        
        print(f"\nPrinting the probability table")
        print(outProbabilities)       
        
        self.probabilityVisualizer = probabilityVisualizer(outProbabilities)
        self.probabilityVisualizer.plotBarChart()
        self.probabilityVisualizer.plotPieChart()
        
if __name__ == "__main__" :
    inMatchesFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\003_EquallyLikelyEvent\DataSets\MatchesData.xlsx"
    inMatchesFileData = ProbabilityAnalysis(inMatchesFilePath)
    inMatchesFileData.runapplication()