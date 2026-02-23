import pandas as pd
import matplotlib.pyplot as plt

class Patient :
    def __init__(self, inName, inAge, inSeverity, inHealthScore):
        self.inName = inName
        self.inAge = inAge
        self.inSeverity = inSeverity
        self.inHealthScore = inHealthScore
    
class HealthCareSystem :
    def __init__(self) :
        self.patients = []
        
    def addPatients(self, inPatient) :
        self.patients.append(inPatient)
        
    def scorePatient(self, inPatient) :
        """Here we are designing the logic for prioritization scoring for the patient: sevearity + health score"""
        return inPatient.inSeverity * 0.7 + inPatient.inHealthScore * 0.3
        
    def makeDecisions(self, inThreshold = 5.0) :
        """This method helps in prioritizing the patient, when the Bias score exceeds the given threshold"""
        outResults = []
            
        for outPatient in self.patients :
            patientScore = self.scorePatient(outPatient)
            priorityDecision = "High Priority" if patientScore >= inThreshold else "Low Priority"
            outResults.append((outPatient.inName, outPatient.inAge, patientScore, priorityDecision))
            
        return outResults
        
class BiasedHealthCareSystem(HealthCareSystem) :
    """This class inherits the actual healthcare system in implementation and inherits the age bias in prioritization"""
    def scorePatient(self, inPatient):
        actualScore = super().scorePatient(inPatient)
            
        """Injecting the age Bias : Reduce the score slightly when the patient is older"""
        if inPatient.inAge > 60 :
            actualScore -= 1.0
        return actualScore
patientData = {
    1: {"name": "Alice", "age": 30, "severity": 7, "healthScore": 3},
    2: {"name": "Bob", "age": 65, "severity": 8, "healthScore": 2},
    3: {"name": "Cathy", "age": 45, "severity": 6, "healthScore": 4},
    4: {"name": "David", "age": 70, "severity": 9, "healthScore": 3},
    5: {"name": "Eva", "age": 25, "severity": 4, "healthScore": 5},
    6: {"name": "Frank", "age": 80, "severity": 7, "healthScore": 4},
    7: {"name": "Grace", "age": 55, "severity": 5, "healthScore": 3},
    8: {"name": "Henry", "age": 40, "severity": 6, "healthScore": 2},
    9: {"name": "Ivy", "age": 62, "severity": 8, "healthScore": 3},
    10: {"name": "Jack", "age": 28, "severity": 5, "healthScore": 4},
    11: {"name": "Kathy", "age": 68, "severity": 7, "healthScore": 3},
    12: {"name": "Leo", "age": 50, "severity": 6, "healthScore": 4},
    13: {"name": "Mona", "age": 38, "severity": 5, "healthScore": 5},
    14: {"name": "Nick", "age": 60, "severity": 7, "healthScore": 3},
    15: {"name": "Olivia", "age": 72, "severity": 9, "healthScore": 4},
    16: {"name": "Paul", "age": 33, "severity": 6, "healthScore": 4},
    17: {"name": "Queen", "age": 75, "severity": 8, "healthScore": 2},
    18: {"name": "Ryan", "age": 27, "severity": 4, "healthScore": 5},
    19: {"name": "Sophia", "age": 64, "severity": 8, "healthScore": 4},
    20: {"name": "Tom", "age": 45, "severity": 6, "healthScore": 3}
}

def resultsVisualizer(inUnbiasedResults, inBiasedResults) :
    unBiasedDataFrame = pd.DataFrame(inUnbiasedResults, columns = ["Name", "Age", "Score", "Decision"])
    biasedDataFrame = pd.DataFrame(inBiasedResults, columns = ["Name", "Age", "Score", "Decision"])
        
    """Logic for categorizing the age groups for easiness of analysis"""
    unBiasedDataFrame["AgeGroup"] = unBiasedDataFrame["Age"].apply(lambda isSenior : "Senior" if isSenior > 60 else "Adult")
    biasedDataFrame["AgeGroup"] = biasedDataFrame["Age"].apply(lambda isSenior : "Senior" if isSenior > 60 else "Adult")
 
    """Logic for counting the number of patients with high priority by age group"""
    unBiasedPriority = unBiasedDataFrame[unBiasedDataFrame["Decision"] == "High Priority"]["AgeGroup"].value_counts()
    biasedPriority = biasedDataFrame[biasedDataFrame["Decision"] == "High Priority"]["AgeGroup"].value_counts()
    
    """Generating the Biased and Unbiased comparision plots"""
    fig, axes = plt.subplots(1, 2, figsize = (12, 5))
    
    axes[0].bar(unBiasedPriority.index, unBiasedPriority.values)
    axes[0].set_title("Unbiased healthcare prioritization")
    axes[0].set_ylabel("Number of high priority patients")
    
    axes[1].bar(biasedPriority.index, biasedPriority.values, color = "orange")
    axes[1].set_title("Biased healthcare prioritization (Age Bias)")
    axes[1].set_ylabel("Number of high priority patients")
    
    plt.suptitle("Impact of age bias on healthcare prioritization decisions", fontsize = 14)
    plt.show()
    
    """Histogram plot for visualizing the score distribution by age group"""
    plt.figure(figsize = (8, 5))
    
    plt.hist(unBiasedDataFrame[unBiasedDataFrame["AgeGroup"] == "Adult"]["Score"], alpha = 0.6, label = "Adult : Unbiased")
    plt.hist(unBiasedDataFrame[unBiasedDataFrame["AgeGroup"] == "Senior"]["Score"], alpha = 0.6, label = "Senior : Unbiased")
    plt.hist(biasedDataFrame[biasedDataFrame["AgeGroup"] == "Senior"]["Score"], alpha = 0.6, label = "Senior : Biased")
    plt.title("Score distributions under age bias and no bias")
    plt.xlabel("Patient Score")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()
    
def main() :
    unBiasedHealthcareSystem = HealthCareSystem()
    biasedHealthcareSystem = BiasedHealthCareSystem()
    
    """Loading the data from the input source (Dictionary) for analysis"""
    for _, outData in patientData.items() :
        outPatient = Patient(outData["name"], outData["age"], outData["severity"], outData["healthScore"])
        unBiasedHealthcareSystem.addPatients(outPatient)
        biasedHealthcareSystem.addPatients(outPatient)
        
    outUnbiasedResults = unBiasedHealthcareSystem.makeDecisions()
    outBiasedResults = biasedHealthcareSystem.makeDecisions()

    resultsVisualizer(outUnbiasedResults, outBiasedResults)
    
if __name__ == "__main__" :
    main()

    