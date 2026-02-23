import pandas as pd
import matplotlib.pyplot as plt

class Customer :
    def __init__(self, inName, inIncome, inCreditScore, inLoanAmount, inLocation) :
        self.inName = inName
        self.inIncome = inIncome
        self.inCreditScore = inCreditScore
        self.inLoanAmount = inLoanAmount
        self.inLocation = inLocation
        
class LoanApprovalSystem :
    def __init__(self) :
        self.customers = []
        
    def addCustomers(self, inCustomer) :
        self.customers.append(inCustomer)
    
    def scoreCustomer(self, inCustomer) :
        """Here we are designing the logic for loan scoring : Income + cedit score - loan amount influence"""
        return (inCustomer.inIncome * 0.4 + inCustomer.inCreditScore * 0.5) - (inCustomer.inLoanAmount * 0.1)
    
    def makeDecisions(self, inThreshold = 50.0) :
        """This method helps in approving the loan when the base score exceeds the given threshold"""
        outResults = []
        
        for outCustomer in self.customers :
            customerScore = self.scoreCustomer(outCustomer)
            loanDecision = "Approved" if customerScore >= inThreshold else "Rejected"
            outResults.append((outCustomer.inName, outCustomer.inLocation, customerScore, loanDecision))
            
        return outResults
    
class BiasedLoanApprovalSystem(LoanApprovalSystem) :
    """This class inherits the actual loan approval system in implementation and introduces the location bias in decision making"""
    
    def scoreCustomer(self, inCustomer) :
        actualScore = super().scoreCustomer(inCustomer)
        
        """Injecting the location bias: Reduce the score slightly when the customer is from rural area"""
        if inCustomer.inLocation == "Rural" :
            actualScore -= 5.0
            
        return actualScore

def resultsVisualizerMultiYear(inResultDict) :
    """Visualizes multi-year loan bias trends"""
    fig, axes = plt.subplots(1, 2, figsize = (14, 6))

    for year, results in inResultDict.items() :
        unbiasedDF = pd.DataFrame(results["unbiased"], columns = ["Name", "Location", "Score", "Decision"])
        biasedDF = pd.DataFrame(results["biased"], columns = ["Name", "Location", "Score", "Decision"])

        unbiasedApprovals = unbiasedDF[unbiasedDF["Decision"] == "Approved"]["Location"].value_counts()
        biasedApprovals = biasedDF[biasedDF["Decision"] == "Approved"]["Location"].value_counts()
    
        axes[0].bar(unbiasedApprovals.index, unbiasedApprovals.values, alpha = 0.6, label = f"{year} Unbiased")
        axes[1].bar(biasedApprovals.index, biasedApprovals.values, alpha = 0.6, label = f"{year} Biased")
            
    axes[0].set_title("Unbiased loan approvals (across years)")
    axes[0].set_ylabel("Number of approved loans")
    axes[0].legend()
                                                                  
    axes[1].set_title("Biased loan approvals (across years)")
    axes[1].set_ylabel("Number of approved loans")
    axes[1].legend()  
        
    plt.suptitle("Impact of location bias on loan approvals across yars", fontsize = 14)
    plt.show()
        
        
    """Visualizing score distributions under Bias and no bias"""
    plt.figure(figsize = (8, 5))
    for year, results in inResultDict.items() :
        biasedDF = pd.DataFrame(results["biased"], columns = ["Name", "Location", "Score", "Decision"])
        plt.hist(biasedDF[biasedDF["Location"] == "Rural"]["Score"], alpha = 0.4, label = f"Rural {year} Biased")
        plt.hist(biasedDF[biasedDF["Location"] == "Urban"]["Score"], alpha = 0.4, label = f"Urban {year} Biased")
          
    plt.title("Score distribution comparison (Biased scenario over years)")    
    plt.xlabel("Customer Score")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

def processSheet(inDataFrame) :
    unBiasedSystem = LoanApprovalSystem()
    biasedSystem = BiasedLoanApprovalSystem()
    
    for _, outData in inDataFrame.iterrows() :
        outCustomer = Customer(outData["Name"], outData["Income"], outData["CreditScore"], outData["LoanAmount"], outData["Location"])
        unBiasedSystem.addCustomers(outCustomer)
        biasedSystem.addCustomers(outCustomer)
        
    outUnbiasedResults = unBiasedSystem.makeDecisions()
    outBiasedResults = biasedSystem.makeDecisions()
    
    return outUnbiasedResults, outBiasedResults

def main() :
    
    try :
        """Process to read multiple sheets from a single excel workbook"""
        excelFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\001_BiasConcept\DataSets\CustomerLoadData.xlsx"
        excelFile = pd.ExcelFile(excelFilePath)
    except FileNotFoundError as fileNotFoundError :
        print(f"\nThe coresponding excel file not found in the : {excelFilePath}")
        return
    except Exception as exceptionObject :
        print(f"\nFatal error! Encountered abnormally : {exceptionObject}")
        return
    
    """Initializing a dictionary object for storing year-wise results"""
    allYearResults = {} 
    
    for outSheetName in excelFile.sheet_names :
        print(f"\nNow processing the year sheet : {outSheetName}")
        sheetDataFrame = pd.read_excel(excelFile, sheet_name = outSheetName)
        outUnbiased, outBiased = processSheet(sheetDataFrame)
        allYearResults[outSheetName] = {
                                        "unbiased" : outUnbiased,
                                        "biased" : outBiased
                                        }
        
        """Initiating the visualizing module for all the year results"""
        resultsVisualizerMultiYear(allYearResults)
        
if __name__ == "__main__" :
    main()