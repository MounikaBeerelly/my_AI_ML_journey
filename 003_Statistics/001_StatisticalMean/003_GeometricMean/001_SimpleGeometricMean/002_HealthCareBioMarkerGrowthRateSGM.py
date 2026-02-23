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

class InvalidBiomarkerRateError(Exception) :
    pass

class GeometricMeanComputationError(Exception) :
    pass

class PatientBiomarkerGeometricMeanEngine :
    """
    Computes Simple Geometric Mean of Biomarker Progression Rates To Analyze Disease Growth Patterns
    """

    def __init__(self, inputFilePath : str) -> None :
        self.inputFilePath = inputFilePath
        self.dataFrame : pd.DataFrame | None = None

        self.requiredColumns = [
            "PatientID",
            "BiomarkerName",
            "TestDate",
            "BiomarkerChangeRate",
            "AgeGroup",
            "DiagnosisStage"
        ]

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Fatal Error! Dataset Not Found At Path : {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError("Fatal Error! Dataset Contains No Records.")

        print("Dataset Loaded Successfully")

    def validateSchema(self) -> None :
        for column in self.requiredColumns :
            if column not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Required Column Missing : {column}"
                )

        print("Dataset Schema Validation Successful")

    def validateRates(self) -> None :
        if (self.dataFrame["BiomarkerChangeRate"] <= -100).any() :
            raise InvalidBiomarkerRateError(
                "Fatal Error! BiomarkerChangeRate Must Be Greater Than -100%"
            )

        print("Biomarker Rate Validation Successful")

    def computeGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            print("\nConverting Percentage Changes To Growth Factors...")
            df["GrowthFactor"] = 1 + (df["BiomarkerChangeRate"] / 100)

            resultDF = (
                df.groupby(["PatientID", "BiomarkerName"])
                .agg(
                    AgeGroup = ("AgeGroup", "first"),
                    DiagnosisStage = ("DiagnosisStage", "first"),
                    Observations = ("TestDate", "count"),
                    GeometricMeanGrowth = (
                        "GrowthFactor",
                        lambda x : np.exp(np.mean(np.log(x)))
                    )
                )
                .reset_index()
            )

            resultDF["GeometricMeanChangeRate"] = (
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
            by="GeometricMeanChangeRate",
            ascending=True
        )

        plt.figure(figsize=(10, max(5, len(plotDF) * 0.4)))

        plt.barh(
            plotDF["BiomarkerName"],
            plotDF["GeometricMeanChangeRate"]
        )

        plt.xlabel("Geometric Mean Change Rate (%)")
        plt.ylabel("Biomarker Name")
        plt.title("Geometric Mean Biomarker Progression")
        plt.tight_layout()
        plt.show()

def main() -> None :
    try :
        inputFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\DataSets\PatientBiomarkerRecords.xlsx"
        
        biomarkerEngine = PatientBiomarkerGeometricMeanEngine(inputFilePath)

        biomarkerEngine.loadDataset()
        biomarkerEngine.validateSchema()
        biomarkerEngine.validateRates()

        resultDF = biomarkerEngine.computeGeometricMean()

        print("\nFinal Geometric Mean Biomarker Output")
        print(resultDF)

        biomarkerEngine.plotGeometricMean(resultDF)

    except (
        DatasetNotFoundError,
        DatasetEmptyError,
        InvalidSchemaError,
        InvalidBiomarkerRateError,
        GeometricMeanComputationError
    ) as knownException :
        print(f"\nApplication Failed : {knownException}")

    except Exception as unknownException :
        print(f"\nUnexpected System Error : {unknownException}")

if __name__ == "__main__" :
    main()
        