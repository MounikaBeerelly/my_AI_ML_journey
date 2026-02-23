import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class DatasetNotFoundError(Exception) :
    pass

class DatasetEmptyError(Exception) :
    pass

class InvalidSchemaError(Exception) :
    pass

class InvalidPurchaseRateError(Exception) :
    pass

class GeometricMeanComputationError(Exception) :
    pass

class CustomerPurchaseGeometricMeanEngine :
    """
    Computes Simple Geometric Mean of Customer Purchase Growth For CLV & Retention Analysis
    """
    def __init__(self, inputFilePath : str) -> None :
        self.inputFilePath = inputFilePath
        self.dataFrame : pd.DataFrame | None = None

        self.requiredColumns = [
            "CustomerID",
            "TransactionMonth",
            "PurchaseGrowthRate",
            "CustomerSegment",
            "Channel",
            "CampaignID"
        ]
    
    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Fatal Error! Dataset Not Found At Path : {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError(
                "Fatal Error! Dataset Contains No Records."
            )

        print("Dataset Loaded Successfully")

    def validateSchema(self) -> None :
        for column in self.requiredColumns :
            if column not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required Column Missing : {column}"
                )

        print("Dataset Schema Validation Successful")

    def validateRates(self) -> None :
        if (self.dataFrame["PurchaseGrowthRate"] <= -100).any() :
            raise InvalidPurchaseRateError(
                "Fatal Error! PurchaseGrowthRate Must Be Greater Than -100%"
            )

        print("Purchase Rate Validation Successful")

    def computeGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            print("\nConverting Percentage Growth To Growth Factors...")
            df["GrowthFactor"] = 1 + (df["PurchaseGrowthRate"] / 100)

            resultDF = (
                df.groupby(["CustomerID", "CustomerSegment"])
                .agg(
                    Channel = ("Channel", "first"),
                    CampaignID = ("CampaignID", "first"),
                    Months = ("TransactionMonth", "count"),
                    GeometricMeanGrowth = (
                        "GrowthFactor",
                        lambda x : np.exp(np.mean(np.log(x)))
                    )
                )
                .reset_index()
            )

            resultDF["GeometricMeanPurchaseGrowth"] = (
                (resultDF["GeometricMeanGrowth"] - 1) * 100
            )

            print("Geometric Mean Computation Completed Successfully")

            return resultDF

        except Exception as exceptObject :
            raise GeometricMeanComputationError(
                f"Fatal Error! GM Computation Failed : {exceptObject}"
            )

    def plotGeometricMean(self, resultDF : pd.DataFrame) -> None :
        plotDF = resultDF.sort_values(
            by="GeometricMeanPurchaseGrowth",
            ascending=True
        )

        plt.figure(figsize=(10, max(5, len(plotDF) * 0.4)))

        plt.barh(
            plotDF["CustomerID"].astype(str),
            plotDF["GeometricMeanPurchaseGrowth"]
        )

        plt.xlabel("Geometric Mean Purchase Growth (%)")
        plt.ylabel("Customer ID")
        plt.title("Customer Purchase Growth (Geometric Mean)")
        plt.tight_layout()
        plt.show()

def main() -> None :
    try :
        inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\DataSets\CustomerPurchaseRecords.xlsx"
        
        purchaseEngine = CustomerPurchaseGeometricMeanEngine(inputFilePath)

        purchaseEngine.loadDataset()
        purchaseEngine.validateSchema()
        purchaseEngine.validateRates()

        resultDF = purchaseEngine.computeGeometricMean()

        print("\nFinal Customer Purchase Geometric Mean Output")
        print(resultDF)

        purchaseEngine.plotGeometricMean(resultDF)

    except (
        DatasetNotFoundError,
        DatasetEmptyError,
        InvalidSchemaError,
        InvalidPurchaseRateError,
        GeometricMeanComputationError
    ) as knownException :
        print(f"\nApplication Failed : {knownException}")

    except Exception as unknownException :
        print(f"\nUnexpected System Error : {unknownException}")

if __name__ == "__main__" :
    main()