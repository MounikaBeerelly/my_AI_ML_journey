import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import random
from typing import Optional

class DataLoadError(Exception) :
    pass

class InvalidDataFormatError(Exception) :
    pass

class ExperimentconfigurationError(Exception) :
    pass

class SensorDataLoader :
    
    REQUIRED_COLUMNS = [
        "timestamp",
        "machine_id",
        "sensor_value_primary",
        "sensor_value_secondary",
        "temperature_c",
        "humidity_percent",
        "vibration_level",
        "threshold_primary",
        "threshold_secondary",
        "label"
    ]
    
    def __init__(self, inFilePath : str):
        self.inFilePath = inFilePath
        self.dataFrame : Optional[pd.DataFrame] = None
        
    def load(self) -> pd.DataFrame :
        try :
            self.dataFrame = pd.read_excel(self.inFilePath)
        except Exception as exceptObject :
            raise DataLoadError(f"Fatal Error! unable to load Excel file : {exceptObject}")
        
        missingcolumns = [
            outColumn for outColumn in self.REQUIRED_COLUMNS 
            if outColumn not in self.dataFrame.columns
        ]
        
        if missingcolumns :
            raise InvalidDataFormatError(
                f"Fatal Error! Missing required column : {missingcolumns}"
            )
        
        return self.dataFrame
    
class ProbabilityExperiment :
    def __init__(self, dataFrame : pd.DataFrame, inTrials : int = 1000):
        if inTrials <= 0 :
            raise ExperimentconfigurationError(
                "Fatal Error! Trials must be a positive integer."
            )
            
        self.dataFrame = dataFrame
        self.inTrials = inTrials
        self.passProbability : Optional[float] = None
    
    def computeEmpiricalProbability(self) -> None :
        try :
            totalRecords = len(self.dataFrame)
            totalPasses = self.dataFrame["label"].sum()
            self.passProbability = totalPasses / totalRecords
        except Exception as exceptObject :
            raise InvalidDataFormatError(
                f"Fatal Error! Failed Probability Computation : {exceptObject}"
            )
            
    def run(self) -> float :
        if self.passProbability is None :
            self.computeEmpiricalProbability()
            
        successCount = 0
        
        for _ in range(self.inTrials) :
            if random.random() < self.passProbability :
                successCount += 1
                
        estimatedProbability = successCount / self.inTrials
        return estimatedProbability
        
class ChartGenerator :
    def __init__(self, dataFrame : pd.DataFrame):
        sns.set(style = "whitegrid")
        self.dataFrame = dataFrame
        
    def plotSensorDistributions(self) :
        plt.figure(figsize = (14, 6))
        plt.subplot(1, 2, 1)
        sns.histplot(self.dataFrame["sensor_value_primary"], kde = True, bins = 40)
        plt.title("Primary Sensor value Distribution")
        
        plt.subplot(1, 2, 2)
        sns.histplot(self.dataFrame["sensor_value_secondary"], kde = True, bins = 40)
        plt.title("Secondary Sensor Value distriibution")
        
        plt.show()
        
    def plotPassFailDistributions(self) :
        plt.figure(figsize = (6, 5))
        sns.countplot(x = "label", data = self.dataFrame)
        plt.title("Pass versus Fail Distribution")
        plt.show()
        
    def plotPassRateByMachine(self) :
        plt.figure(figsize = (14, 5))
        sns.barplot(
            x = "machine_id",
            y = "label",
            data = self.dataFrame,
            estimator = lambda x : sum(x) / len(x)
        )
        plt.title("Pass Rate by Machine")
        plt.xticks(rotation = 90)
        plt.show()
        
    def plotEnvironmentVersusPass(self) :
        plt.figure(figsize = (14, 6))
       
        plt.subplot(1, 2, 1)
        sns.scatterplot(
            x = "temperature_c",
            y = "sensor_value_primary",
            hue = "label",
            data = self.dataFrame,
            palette = "coolwarm"
        )
        plt.title("Temperature versus Sensor Primary")
        
        plt.subplot(1, 2, 2)
        sns.scatterplot(
            x = "vibration_level",
            y = "sensor_value_primary",
            hue = "label",
            data = self.dataFrame,
            palette = "coolwarm"
        )
        plt.title("Vibration versus Sensor Primary")
        
        plt.show()   
        
    def plotTimeSeriesTrends(self) :
        sorted_df = self.dataFrame.sort_values("timestamp")
        
        plt.figure(figsize = (15, 6))
        sns.lineplot(
            x = "timestamp",
            y = "sensor_value_primary",
            data = sorted_df
        )
        plt.title("Sensor Primary Over Time")
        plt.xticks(rotation = 45)
        plt.show()
        
class ExperimentController :
    def __init__(self, inFilePath : str, inTrials : int):
        self.inFilePath = inFilePath
        self.inTrials = inTrials
        self.dataFrame : Optional[pd.DataFrame] = None
        self.experiment_result : Optional[float] = None
        
    def execute(self) -> None :
        try :
            loader = SensorDataLoader(self.inFilePath)
            self.dataFrame = loader.load()
            
            experiment = ProbabilityExperiment(self.dataFrame, self.inTrials)
            self.experiment_result = experiment.run()
            
            chart_gen = ChartGenerator(self.dataFrame)
            chart_gen.plotSensorDistributions()
            chart_gen.plotPassFailDistributions()
            chart_gen.plotPassRateByMachine()
            chart_gen.plotEnvironmentVersusPass()
            chart_gen.plotTimeSeriesTrends()
        except (DataLoadError, InvalidDataFormatError, ExperimentconfigurationError) as exceptObject :
            print(f"Fatal Error! : {exceptObject}")
        except Exception as exceptObject :
            print(f"Unexpected Error! : {exceptObject}")
            
    def get_result(self) -> Optional[float] :
        return self.experiment_result
    
if __name__ == "__main__" :
    
    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\005_Experiments\DataSets\SensorQualityData.xlsx"
    
    controller = ExperimentController(
        inFilePath = inFilePath,
        inTrials = 5000
    )
    
    controller.execute()
    
    finalResult = controller.get_result()
    
    if finalResult is not None :
        print(f"\nEstimated Probability of Product passing QC : {finalResult : .4f}")