import os
import matplotlib.pyplot as plt
import pandas as pd

class DataFileNotFoundError(Exception) : 
    pass

class InvalidFileFormatError(Exception) :
    pass

class DataNotLoadedError(Exception) :
    pass

class EmptyDatasetError(Exception) :
    pass

class MissingColumnError(Exception) :
    pass

class ExpectedValueCalculator :
    requiredColumns = [
        "Sale ID",
        "Discount (%)",
        "Category",
        "Region",
        "Product Type",
        "Channel",
        "Cost (USD)",
        "Sales Revenue (USD)",
        "Profit (USD)"
    ]
    
    def __init__(self, inFilePath):
        self.inFilePath = inFilePath
        self.data = None
        
        
    # Data file validation
    def validateDataFile(self) :
        try:
            if not os.path.exists(self.inFilePath) :
                raise DataFileNotFoundError(
                    f"\nFatal Error! Dataset file not found : {self.inFilePath}\n"
                )
                
            if not self.inFilePath.endswith(".xlsx") :
                raise InvalidFileFormatError (
                    f"\nFatal Error! Only .xslx Excel files are Accepted\n"
                )
                
        except Exception as exceptObject :
            print(f"\nFatal Error! File validation failed : {exceptObject}\n")
            raise
        
    def validateRequiredColumns(self) :
        missingColumns = [
            outColumn for outColumn in self.requiredColumns if outColumn not in self.data.columns
        ]
        if missingColumns :
            raise MissingColumnError(
                f"\nFatal Error! Missing required columns : {missingColumns}\n"
            )
            
    def loadData(self) :
        try : 
            self.validateDataFile()
            self.data = pd.read_excel(self.inFilePath)
            
            if self.data.empty :
                raise EmptyDatasetError("\nFata Error! DatasetLoaded is empty\n")
            
            self.validateRequiredColumns()
            
            print(f"\nDataset loaded successfully from : {self.inFilePath}\n")
            
        except Exception as exceptObject :
            print(f"\nFata Error! Error loading dataset : {exceptObject}\n")
            raise
        
    def calculateExpectedValue(self) :
        """
        This method computes the following constructs
        1. Revenue Based Probability
        2. Expected Value Contribution
        3. Cumulative Probability
        4. Profit Margin
        5. Cost Efficiency Ratio
        """
        
        try :
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Data not loaded - cannot compute expected value\n"
            )
                
            totalRevenue = self.data["Sales Revenue (USD)"].sum()
                
            self.data["Probability"] = (
                self.data["Sales Revenue (USD)"] / totalRevenue
            )
                
            self.data["Contribution To EV (Weighted)"] = (
                self.data["Sales Revenue (USD)"] * self.data["Probability"]
            )
                
            self.data["Cumulative Probability"] = self.data["Probability"].cumsum()
                
            self.data["Profit Margin (%)"] = (
                (self.data["Profit (USD)"] / self.data["Sales Revenue (USD)"]) * 100
            )
                
            self.data["Revenue-Cost Ratio"] = (
                self.data["Sales Revenue (USD)"] / self.data["Cost (USD)"]
            )
                
            self.data["Weighted Probability"] = (
                self.data["Profit (USD)"] * self.data["Probability"]
            )
                
            expectedValue = self.data["Contribution To EV (Weighted)"].sum()
                
            return expectedValue, totalRevenue
            
        except Exception as exceptObject :
            print(f"\nFatal Error! Error computing expected value : {exceptObject}\n")
            raise
        
    
    def addHelperColumns(self) :
        try :
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Dataset not loaded : cannot add helper columns\n"
                )
                
            print(f"\nHelper Column for : Normalized Revenue (0-1)")
            maxRevenue = self.data["Sales Revenue (USD)"].max()
            self.data["Normalized Revenue"] = (
                self.data["Sales Revenue (USD)"] / maxRevenue
            )
            
            print(f"\nHelper Column for : Calculating the discount impact score (Discount * Profit Margin)")
            self.data["Discount Impact Score"] = (
                self.data["Discount (%)"] * self.data["Profit Margin (%)"] 
            )   
            
            print(f"\nHelper Column for : Calculating the Profit Efficiency (Profit per USD cost)")
            self.data["Profit Efficiency"] = (
                self.data["Profit (USD)"] / self.data["Cost (USD)"]
            )
            
            print(f"\nHelper Column for : Calculating the Ranking Columns")
            self.data["Revenue Rank"] = self.data["Sales Revenue (USD)"].rank(ascending = False)
            self.data["Profit Rank"] = self.data["Profit (USD)"].rank(ascending = False)
        except Exception as exceptObject :
            print(f"\nFatal Error! Error in adding Helper columns : {exceptObject}\n")
            raise
        
    def generateSummary(self) :
        try:
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Dataset not loaded : cannot generate summary\n"
                )
                
            print(f"------------------------Business Intellisense summary-----------------------")
            print(f"\nTop Regions by Revenue...")
            print(self.data.groupby("Region")["Sales Revenue (USD)"].sum()) 
            print(f"\nTop Categories by Profit...")
            print(self.data.groupby("Category")["Profit (USD)"].sum()) 
            print(f"\nChannel Contribution...")
            print(self.data.groupby("Channel")["Sales Revenue (USD)"].sum())
        except Exception as exceptObject :
            print(f"\nFatal Error! Error Generating Summary Report : {exceptObject}\n")
            raise
        
    def showData(self, inMessage = "Displaying Dataset") :
        try : 
            if self.data is None :
                raise DataNotLoadedError(
                    f"\nFatal Error! Dataset not loaded : Cannot Display Records\n"
                )
                
            print(f"\n{inMessage}")
            print(self.data.to_string(index = False))
            print("\n")
            
        except Exception as exceptObject :
            print(f"\nFatal Error! Error Displaying Records : {exceptObject}\n")
            raise
        
    def saveModifiedData(self, outputPath) :
        try :
            if self.data is None :
                raise DataNotLoadedError(
                    "\nFatal Error! No Modified Data To Save\n"
                )

            self.data.to_excel(outputPath, index = False)
            print(f"\nModified Enhanced Dataset Saved At : {outputPath}\n")

        except Exception as exceptObject :
            print(f"\nFatal Error! Error Saving Output File : {exceptObject}\n")
            raise 
        
class ExpectedValuesCharts :
    @staticmethod
    def plotRevenueByRegion(inData) :
        plt.figure(figsize = (8,4))
        inData.groupby("Region")["Sales Revenue (USD)"].sum().plot(kind = "bar")
        plt.title("Total Revenue by Region")
        plt.xlabel("Region")
        plt.ylabel("Revenue (USD)")
        plt.grid(axis = 'y')
        plt.show()
        
    @staticmethod
    def plotProfitByCategory(inData) :
        plt.figure(figsize = (8,4))
        inData.groupby("Category")["Profit (USD)"].sum().plot(kind = "bar")
        plt.title("Total Profit by Product Category")
        plt.xlabel("Category")
        plt.ylabel("Profit (USD)")
        plt.grid(axis = 'y')
        plt.show()
        
    @staticmethod
    def plotChannelContribution(inData) :
        plt.figure(figsize = (8,4))
        inData.groupby("Channel")["Sales Revenue (USD)"].sum().plot(kind = "pie", autopct = "%1.1f%%")
        plt.title("Sales Contribution by Channel")
        plt.ylabel("")
        plt.show()
        
    @staticmethod
    def plotProbabilityDistribution(inData) :
        plt.figure(figsize = (10,4))
        plt.plot(inData["Sale ID"], inData["Probability"], marker = "o")
        plt.title("Probability Distribution (Revenue-based)")
        plt.xlabel("Sale ID")
        plt.ylabel("Probability")
        plt.grid()
        plt.show()
        
    @staticmethod
    def plotEVContribution(inData) :
        plt.figure(figsize = (10,4))
        plt.bar(inData["Sale ID"], inData["Contribution To EV (Weighted)"])
        plt.title("Weighted EV Contribution Per Transaction")
        plt.xlabel("Sale ID")
        plt.ylabel("EV Contribution")
        plt.grid(axis = 'y')
        plt.show()
        
    @staticmethod
    def plotProfitMarginDistribution(inData) :
        plt.figure(figsize = (10,4))
        plt.plot(inData["Sale ID"], inData["Profit Margin (%)"])
        plt.title("Profit Mamrgin (%) Distribution")
        plt.xlabel("Sale ID")
        plt.ylabel("Profit MArgin (%)")
        plt.grid()
        plt.show()
        
def main() :
    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\ExpectedValue\DataSets\SalesDataRecords.xlsx"
    outFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\ExpectedValue\DataSets\OutData\OutSalesData.xlsx"
    
    try :
        expectedValueCalculator = ExpectedValueCalculator(inFilePath)
        
        expectedValueCalculator.loadData()
        expectedValueCalculator.showData("Displaying the original extended dataset")
        
        expectedValue, totalRevenue = expectedValueCalculator.calculateExpectedValue()
        
        print(f"\n--------------------Expected Values Analysis Summary-------------------")
        print(f"\nTotal Revenue (USD) : {totalRevenue : .2f}")
        print(f"\nExpected Value (USD) : {expectedValue : .2f}")
        
        expectedValueCalculator.showData(
            "Displaying Enhanced DataSet with EV-Related Columns"
        )
        
        expectedValueCharts = ExpectedValuesCharts()
        expectedValueCharts.plotRevenueByRegion(expectedValueCalculator.data)
        expectedValueCharts.plotProfitByCategory(expectedValueCalculator.data)
        expectedValueCharts.plotChannelContribution(expectedValueCalculator.data)
        expectedValueCharts.plotProbabilityDistribution(expectedValueCalculator.data)
        expectedValueCharts.plotEVContribution(expectedValueCalculator.data)
        expectedValueCharts.plotProfitMarginDistribution(expectedValueCalculator.data)
        
        expectedValueCalculator.saveModifiedData(outFilePath)
    except Exception as exceptObject :
        print(f"\nApplication Terminated : Reason : {exceptObject}")
        
if __name__ == "__main__" :
    main()