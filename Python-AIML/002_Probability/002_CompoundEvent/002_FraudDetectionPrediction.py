import pandas as pd
import matplotlib.pyplot as plt

class FraudTransaction :
    def __init__(self, inCustomerID, inAmount, inTransactionCountry, inCustomerCountry, inIsFraud) :
        self.inCustomerID = inCustomerID
        self.inAmount = inAmount
        self.inTransactionCountry = inTransactionCountry
        self.inCustomerCountry = inCustomerCountry
        self.inIsFraud = inIsFraud
        
class FraudProbabilityAnalyzer :
    def __init__(self) :
        self.transactions = []
    
    def addTransactions(self, inTransaction) :
        self.transactions.append(inTransaction) 
    
    def calculateProbabilities(self) :
        """This method calculates the compound probabilities for Fraud Events"""
        df = pd.DataFrame([vars(outTransaction) for outTransaction in self.transactions])
        
        """Defining the logic for marking the transactions to get identified for fraud with international and high value"""
        df["IsInternational"] = df.apply(lambda internationalState : internationalState["inTransactionCountry"] != internationalState["inCustomerCountry"], axis = 1) 
        df["IsHighValue"] = df["inAmount"] > 3000
        
        totalTransactions = len(df)
        
        """Calculate the individual probabilities"""
        pFraud = len(df[df["inIsFraud"] == "Yes"]) / totalTransactions
        pInternational = len(df[df["IsInternational"] == True]) / totalTransactions
        pHighValue = len(df[df["IsHighValue"] == True]) / totalTransactions
        
        """finalizing the compound probability event which are International and High value"""
        dfCompound = df[(df["IsInternational"]) & (df["IsHighValue"])]
        pCompound = len(dfCompound) / totalTransactions
        
        """Taking the decision whether the transaction is a Fraud OR not depending on Probability"""
        """Applying conditional Probability Logic : Fraud | (International AND High Value)"""
        if len(dfCompound) > 0 :
            pFraudGivenCompound = len(dfCompound[dfCompound["inIsFraud"] == "Yes"]) / len(dfCompound)
        else :
            pFraudGivenCompound = 0.0
            
        return {
            "P(Fraud)" : round(pFraud, 4),
            "P(International)" : round(pInternational, 4),
            "P(HighValue)" : round(pHighValue, 4),
            "P(International ∩ HighValue)" : round(pCompound, 4),
            "P(Fraud | International ∩ HighValue)" : round(pFraudGivenCompound, 4)
        }
        
def resultsVisualizer(inProbabilities) :
    """function to visualize the compound probability trends across years"""
    df = pd.DataFrame(inProbabilities).T.reset_index()
    df.columns = ["Year", "P(Fraud)", "P(International)", "P(HighValue)", "P(International ∩ HighValue)", "P(Fraud | International ∩ HighValue)"]
    plt.figure(figsize = (10, 6))
    plt.plot(df["Year"], df["P(Fraud | International ∩ HighValue)"], marker = 'o', label = "P(International ∩ HighValue)", color = "red")
    plt.plot(df["Year"], df["P(Fraud)"], marker = 'o', label = "P(Fraud)", color = "blue")
    plt.title("Compound Event Probability Trend : Fraud | (International ∩ High Value)")
    plt.xlabel("Year")
    plt.ylabel("Probability")
    plt.legend()
    plt.grid(True)
    plt.show()

def processSheet(inDataFrame) :
    analyzer = FraudProbabilityAnalyzer()

    for _, outData in inDataFrame.iterrows() :
        outTransaction = FraudTransaction(outData["CustomerID"], outData["Amount"], outData["TransactionCountry"], outData["CustomerCountry"], outData["IsFraud"])
        analyzer.addTransactions(outTransaction)
    
    return analyzer.calculateProbabilities()

def main() :
    try :
        inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\002_CompoundEvent\DataSets\FraudTransactionData.xlsx"
        excelFile = pd.ExcelFile(inFilePath)
    except FileNotFoundError as fileNotFoundError :
        print(f"\nFatal Error! Excel file not foundm please ensure : {fileNotFoundError} exists in the specified path")
        return
    
    allYearProbabilities = {}
    
    for outSheetName in excelFile.sheet_names :
        print(f"Processing year sheet : {outSheetName}")
        sheetDataFrame = pd.read_excel(excelFile, sheet_name = outSheetName)
        yearProbabilities = processSheet(sheetDataFrame)
        allYearProbabilities[outSheetName] = yearProbabilities
        
    resultsVisualizer(allYearProbabilities)
    
if __name__ == "__main__" :
    main()