import pandas as pd
import matplotlib.pyplot as plt

class WeatherRecord :
    def __init__(self, inDate, inCity, inTemperature, inHumidity, inCondition) :
        self.inDate = inDate,
        self.inCity = inCity
        self.inTemperature = inTemperature
        self.inHumidity = inHumidity
        self.inCondition = inCondition
        
class WeatherEventSystem :
    def __init__(self):
        self.weatherRecords = []
        
    def addRecord(self, inRecord) :
        self.weatherRecords.append(inRecord)
    
    def calculateProbability(self, inCondition = "Rain") :
        """This method calculated the probability of a given weather event defaulted as Rain"""
        totalRecords = len(self.weatherRecords)
        if totalRecords == 0 :
            return 0.0
        
        matchingRecords = len([outWeatherRecord for outWeatherRecord in self.weatherRecords if outWeatherRecord.inCondition == inCondition]) 
        eventProbability = matchingRecords / totalRecords
        return eventProbability
    
def visualizeProbability(inProbabilityDict) :
    """This method visualizes the probabilities of weather events across years and Cities"""
    outDataFrame = pd.DataFrame(inProbabilityDict).T
    outDataFrame.plot(kind = "bar", figsize = (12, 6))
    plt.title("Probability of Rain across Cities (Multi-year)")
    plt.ylabel("Probability of Rain")
    plt.xlabel("Year")
    plt.legend(title = "City")
    plt.grid(True)
    plt.show()
        
def processYearSheet(inDataFrame) :
    """This method loads year-wise data and computes probabilities per city"""
    cityProbability = {}
    
    for outCity in inDataFrame["City"].unique() :
        cityData = inDataFrame[inDataFrame["City"] == outCity]
        weatherSystem = WeatherEventSystem()
        for _, outRow in cityData.iterrows() :
            cityRecord = WeatherRecord(outRow["Date"], outRow["City"], outRow["Temperature"],outRow["Humidity"], outRow["Condition"],)
            weatherSystem.addRecord(cityRecord)
            
        cityProbability[outCity] = weatherSystem.calculateProbability(inCondition = "Rain")
        
    return cityProbability

def main() :
    try :
        """Process to read multiple sheets from a single excel book"""
        excelFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\001_SimpleEvent\DataSets\weatherData.xlsx"
        excelFile = pd.ExcelFile(excelFilePath)
    except FileNotFoundError as fileNotFoundError :
        print(f"\nThe coresponding excel file not found in the : {excelFilePath}, please ensure the file exists : [fileNotFoundError]")
        return
    
    allYearProbabilities = {}
    
    for outSheetName in excelFile.sheet_names :
        print(f"\nProcessing the weather data for the year : {outSheetName}")
        yearDataFrame = pd.read_excel(excelFile, sheet_name = outSheetName)
        yearlyProbabilities = processYearSheet(yearDataFrame)
        allYearProbabilities[outSheetName] = yearlyProbabilities
        
    """Calling the process for visualization of the probabilities"""
    visualizeProbability(allYearProbabilities)
    
if __name__ == "__main__" :
    main()
    