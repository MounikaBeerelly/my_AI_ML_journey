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

class InvalidReturnRateError(Exception) :
    pass

class RuntimeMetricComputationError(Exception) :
    pass

class WeightedGeometricMeanComputationError(Exception) :
    pass

class PatientRuntimeWeightedGeometricMeanEngine :
    """
    Computes Runtime Clinical Metrics and Applies Risk-Weighted Geometric Mean for PAtient Biomarker Progression Analytics"""
    def __init__(
        self,
        inputFilePath: str,
        outputFilePath: str
    ) -> None :

        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath

        self.dataFrame: pd.DataFrame | None = None

        self.requiredColumns = [
            "PatientID",
            "PatientName",
            "Year",
            "BiomarkerChangeRate",
            "AgeGroup",
            "RiskCategory"
        ]

    def loadDataset(self) -> None :
        if not os.path.exists(self.inputFilePath) :
            raise DatasetNotFoundError(
                f"Dataset not found at path: {self.inputFilePath}"
            )

        self.dataFrame = pd.read_excel(self.inputFilePath)

        if self.dataFrame.empty :
            raise DatasetEmptyError(
                "Fatal Error! Dataset Contains No Records"
            )

        print("Dataset loaded successfully")

    def validateSchema(self) -> None :
        for outColumns in self.requiredColumns :
            if outColumns not in self.dataFrame.columns :
                raise InvalidSchemaError(
                    f"Fatal Error! Missing Required Column: {outColumns}"
                )

        print("Schema validation successful")

    def validateBiomarkerRates(self) -> None :
        if(self.dataFrame["BiomarkerChangeRate"] <= -100).any() :
            raise InvalidReturnRateError(
                "Fatal Error! BiomarkerChangeRate must be greater than -100%"
            )
        print("BiomarkerRate validation successful")

    def computeRuntimeMetrics(self) -> None :
        try :
            df = self.dataFrame.copy()

            print(f"\nComputing runtime clinical Metrics...")

            print(f"\nTaking the parameters and values for marketcap (simulated by sector and Risk)")

            df["DiseaseSeverityScore"] = df["RiskCategory"].map(
                {
                    "Low": 1.2,
                    "Medium": 1.0,
                    "High": 0.8
                }
            )
            df["VolatalityPercent"] = (
                df.groupby("PatientID")["BiomarkerChangeRate"]
                .transform("std")
                .fillna(4.0)
            )

            df["AgeRiskFactor"] = df["AgeGroup"].map(
                {
                    "18-30": 0.8,
                    "31-45": 1.0,
                    "46-60": 1.2,
                    "60+": 1.5
                }
            )

            df["GrowthFactor"] = (
                1 + (df["BiomarkerChangeRate"] / 100)
            )

            self.dataFrame = df

            print("Runtime clinical metrics computation computed successfully")
        except Exception as exceptObj :
            raise RuntimeMetricComputationError(
                f"Error during runtime metric computation: {exceptObj}"
            )

    def computeWeights(self) -> None :
        print(f"\nComputing dynamic Patient weights...")

        rawWeight = (
            self.dataFrame["DiseaseSeverityScore"] *
            self.dataFrame["AgeRiskFactor"] /
            (1 + self.dataFrame["VolatalityPercent"])
        )

        self.dataFrame["Weight"] = rawWeight / rawWeight.sum()

        print(f"\nDynamic weight Computation completed")

    def computeWeightedGeometricMean(self) -> pd.DataFrame :
        try :
            df = self.dataFrame.copy()

            df["WeightedLogGrowth"] = (
                df["Weight"] * np.log(df["GrowthFactor"])
            )

            resultDF = (
                df.groupby(["PatientID", "PatientName"])
                .agg(
                    Age = ("AgeGroup", "first"),
                    RiskCategory = ("RiskCategory", "first"),
                    TotalWeight = ("Weight", "sum"),
                    WeightedLogSum = ("WeightedLogGrowth", "sum")
                )
                .reset_index()
            )

            resultDF["WeightedGeometricMeanGrowth"] = (
                np.exp(resultDF["WeightedLogSum"])
            )

            resultDF["WeightedGeometricMeanReturnPercent"] = (
                (resultDF["WeightedGeometricMeanGrowth"] - 1) * 100
            )

            print("Weighted Geometric Mean Computation completed successfully")

            return resultDF

        except Exception as exceptObj :
            raise WeightedGeometricMeanComputationError(
                f"Error during weighted geometric mean computation: {str(exceptObj)}"
            )

    def run(self) -> None :
        self.loadDataset()
        self.validateSchema()
        self.validateBiomarkerRates()
        self.computeRuntimeMetrics()
        self.computeWeights()

        resultDF = self.computeWeightedGeometricMean()
        resultDF.to_excel(self.outputFilePath, index=False)

        print(f"\nFinal output saved to: {self.outputFilePath}")

        resultDF.sort_values(
            "WeightedGeometricMeanReturnPercent",
            ascending = False
        ).plot(
            x = "PatientName",
            y = "WeightedGeometricMeanReturnPercent",
            kind = "bar",
            legend = False,
            title = "Weighted Geometric Mean Returns"
        )

        plt.tight_layout()
        plt.show()

if __name__ == "__main__" :
    inFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\PatientBiomarker.xlsx"
    outFilePath = r"C:\AI&ML\AI-ML\Python-AIML\003_Statistics\001_StatisticalMean\003_GeometricMean\002_WeightedGeometricMean\DataSets\EnhancedData\PatientBiomarkerEnhancedData.xlsx"

    engine = PatientRuntimeWeightedGeometricMeanEngine(
        inputFilePath=inFilePath,
        outputFilePath=outFilePath
    )

    engine.run()