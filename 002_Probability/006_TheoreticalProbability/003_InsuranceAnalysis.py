import pandas as pd

class DataLoadError(Exception) :
    pass

class InvalidFeatureError(Exception) :
    pass

class InvalidValueError(Exception) :
    pass

class ProbabilityEngine :
    def __init__(self, inFilePath : str) :
        self.inFilePath = inFilePath
        self.dataFrame = None

    def loadData(self) -> None :
        try :
            df = pd.read_excel(self.inFilePath)

            if df.empty :
                raise DataLoadError("Fatal Error! Dataset is Empty.")

            self.dataFrame = df

        except FileNotFoundError as fileNotFoundError:
            raise DataLoadError(f"Fatal Error! File not found : {fileNotFoundError}")
        except Exception as exceptObject:
            raise DataLoadError(f"Fatal Error! Unable To Load Excel File : {exceptObject}")

    def validateFeatures(self, inFeatureName : str) -> None :
        if inFeatureName not in self.dataFrame.columns :
            raise InvalidFeatureError(
                f"Fatal Error! Feature '{inFeatureName}' Not Found In Dataset."
            )

    def validateValue(self, inFeatureName : str, inFeatureValue : str) :
        uniqueValues = self.dataFrame[inFeatureName].unique()

        if inFeatureValue not in uniqueValues :
            raise InvalidValueError(
                f"Fatal Error! Value '{inFeatureValue}' Not Found In Feature '{inFeatureName}'."
                f" Available Values Are : {list(uniqueValues)}"
            )

    def conditionalProbability(self,
                               inTargetColumn : str,
                               inTargetValue,
                               inGivenColumn : str,
                               inGivenValue ) -> float :
        if self.dataFrame is None :
            raise DataLoadError("Data Not Loaded. Call 'loadData()' Method First.")

        print(f"\nValidating all the columns and values...")
        self.validateFeatures(inTargetColumn)
        self.validateFeatures(inGivenColumn)
        self.validateValue(inTargetColumn, inTargetValue)
        self.validateValue(inGivenColumn, inGivenValue)

        df = self.dataFrame

        print(f"\nCounting the number of rows with the given condition : P(B)")
        totalGiven = len(df[df[inGivenColumn] == inGivenValue])
        if totalGiven == 0 :
            return 0.0
        print(f"\nCount Joint occurance: P(A and B)")
        jointCount = len(
            df[(df[inGivenColumn] == inGivenValue) &
               (df[inTargetColumn] == inTargetValue)]
        )

        finalProbability = jointCount / totalGiven

        return finalProbability

def main() :
    inFilePath = r"C:\AI&ML\my-AI-ML-journey\Python-AIML\002_Probability\006_TheoreticalProbability\DataSets\InsuranceData.xlsx"

    probabilityEngine = ProbabilityEngine(inFilePath)
    try :
        probabilityEngine.loadData()
        print(f"\nData loaded successfully...")

        print(f"\nScenario 01 : p( ClaimFiled = Yes | AccidentHistory = Yes)")
        scenarioProbability01 = probabilityEngine.conditionalProbability(
                                inTargetColumn = "ClaimFiled",
                                inTargetValue = "Yes",
                                inGivenColumn = "AccidentHistory",
                                inGivenValue = "Yes"
                            )
        print(f"P(ClaimFiled = Yes | AccidentHistory = Yes) = {scenarioProbability01 : .4f}")

        print(f"\nScenario 02 : P(ClaimFiled = Yes | VehicleType = SUV)")
        scenarioProbability02 = probabilityEngine.conditionalProbability(
                                inTargetColumn = "ClaimFiled",
                                inTargetValue = "Yes",
                                inGivenColumn = "VehicleType",
                                inGivenValue = "SUV"
                            )
        print(f"P(ClaimFiled = Yes | VehicleType = SUV) = {scenarioProbability02 : .4f}")

        print(f"\nScenario 03 : P(AccidentHistory = Yes | AgeGroup = Young)")
        scenarioProbability03 = probabilityEngine.conditionalProbability(
                                inTargetColumn = "AccidentHistory",
                                inTargetValue = "Yes",
                                inGivenColumn = "AgeGroup",
                                inGivenValue = "Young"
                            )
        print(f"P(AccidentHistory = Yes | AgeGroup = Young) = {scenarioProbability03 : .4f}")

        print(f"\nScenario 04 : P(InsuranceType = Premium | Region = Urban)")
        scenarioProbability04 = probabilityEngine.conditionalProbability(
                                inTargetColumn = "InsuranceType",
                                inTargetValue = "Premium",
                                inGivenColumn = "Region",
                                inGivenValue = "Urban"
                            )
        print(f"P(InsuranceType = Premium | Region = Urban) = {scenarioProbability04 : .4f}")
    except (DataLoadError, InvalidFeatureError, InvalidValueError) as errObject :
        print(f"\nFatal Error! {str(errObject)}")
    except Exception as exceptObject:
        print(f"\nUnexpected Error! {exceptObject}")

if __name__ == "__main__" :
    main()