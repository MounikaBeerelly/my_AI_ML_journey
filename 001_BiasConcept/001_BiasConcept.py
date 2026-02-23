import pandas as pd
import matplotlib.pyplot as plt

class Applicant :
    def __init__(self, inName, inExperience, inEducation, inGender) :
        self.inName = inName
        self.inExperience = inExperience
        self.inEducation = inEducation
        self.inGender = inGender
    
class HiringSystem :
    def __init__(self) :
        self.applicants = []
        
    def addApplicants(self, inApplicant) :
        self.applicants.append(inApplicant)
        
    def scoreApplicant(self, inApplicant) :
        """Here we are designing the logic for base scoring for the applicant: Experience + Education"""
        return inApplicant.inExperience * 0.6 + inApplicant.inEducation * 0.4
    
    def makeDecisions(self, inThreshold = 5.0) :
        """This method helps in hiring the Employee, when the base score exceeds the given threshold"""
        outResults = []
        
        for outApplicant in self.applicants :
            applicantScore = self.scoreApplicant(outApplicant)
            hiringDecision = "Hired" if applicantScore >= inThreshold else "Rejected"
            outResults.append((outApplicant.inName, outApplicant.inGender, applicantScore, hiringDecision))
        return outResults
    
class BiasedHiringSystem(HiringSystem) :
    """This class Inherits the actual hiring system in implmentation and introduces the Gender Bias in decision making"""
    
    def scoreApplicant(self, inApplicant) :
        actualScore = super().scoreApplicant(inApplicant)
        
        """Injecting the Gender Bias : Reduce the score slightly when the gender is female for hiring"""
        if inApplicant.inGender == "Female" :
            actualScore -= 1.0
            
        return actualScore
         
applicantData = {
    1: {"name": "Alice", "experience": 6, "education": 4, "gender": "Female"},
    2: {"name": "Bob", "experience": 7, "education": 5, "gender": "Male"},
    3: {"name": "Cathy", "experience": 8, "education": 3, "gender": "Female"},
    4: {"name": "David", "experience": 5, "education": 4, "gender": "Male"},
    5: {"name": "Eva", "experience": 4, "education": 5, "gender": "Female"},
    6: {"name": "Frank", "experience": 9, "education": 4, "gender": "Male"},
    7: {"name": "Grace", "experience": 3, "education": 3, "gender": "Female"},
    8: {"name": "Henry", "experience": 2, "education": 2, "gender": "Male"},
    9: {"name": "Ivy", "experience": 7, "education": 5, "gender": "Female"},
    10: {"name": "Jack", "experience": 8, "education": 3, "gender": "Male"},
    11: {"name": "Kathy", "experience": 5, "education": 4, "gender": "Female"},
    12: {"name": "Leo", "experience": 6, "education": 2, "gender": "Male"},
    13: {"name": "Mona", "experience": 7, "education": 4, "gender": "Female"},
    14: {"name": "Nick", "experience": 4, "education": 3, "gender": "Male"},
    15: {"name": "Olivia", "experience": 8, "education": 5, "gender": "Female"},
    16: {"name": "Paul", "experience": 6, "education": 5, "gender": "Male"},
    17: {"name": "Queen", "experience": 9, "education": 4, "gender": "Female"},
    18: {"name": "Ryan", "experience": 3, "education": 4, "gender": "Male"},
    19: {"name": "Sophia", "experience": 5, "education": 5, "gender": "Female"},
    20: {"name": "Tom", "experience": 2, "education": 3, "gender": "Male"}
}

def resultsVisualizer(inUnbiasedResults, inBiasedResults) :
    unBiasedDataFrame = pd.DataFrame(inUnbiasedResults, columns = ["Name", "Gender", "Score", "Decision"])
    biasedDataFrame = pd.DataFrame(inBiasedResults, columns = ["Name", "Gender", "Score", "Decision"])
    
    """Count the number of employees hired by gender"""
    unBiasedHires = unBiasedDataFrame[unBiasedDataFrame["Decision"] == "Hired"]["Gender"].value_counts()
    biasedHires = biasedDataFrame[biasedDataFrame["Decision"] == "Hired"]["Gender"].value_counts()
    
    """Generating the Biased and Unbiased comparison counts"""
    fig, axes = plt.subplots(1, 2, figsize = (12, 5))
    
    axes[0].bar(unBiasedHires.index, unBiasedHires.values)
    axes[0].set_title("Unbiased Hiring Results")
    axes[0].set_ylabel("Number of Hires")
    
    axes[1].bar(biasedHires.index, biasedHires.values, color = "orange")
    axes[1].set_title("Biased Hiring Results")
    axes[1].set_ylabel("Number of Hires")
    
    plt.suptitle("Impact of gender bias on hiring decisions", fontsize = 14)
    plt.show()
    
    """Histogram plot for visualizing the score distribution by gender"""
    plt.figure(figsize = (8, 5))
    
    plt.hist(unBiasedDataFrame[unBiasedDataFrame["Gender"] == "Male"]["Score"], alpha = 0.6, label = "Male : Unbiased")
    plt.hist(unBiasedDataFrame[unBiasedDataFrame["Gender"] == "Female"]["Score"], alpha = 0.6, label = "Female : Unbiased")
    plt.hist(biasedDataFrame[biasedDataFrame["Gender"] == "Female"]["Score"], alpha = 0.6, label = "Female : Biased")
    plt.suptitle("Score distribution under Bias and No Bias")
    plt.xlabel("Applicant Score")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()
    
def main() :
    unBiasedHiringSystem = HiringSystem()
    biasedHiringSystem = BiasedHiringSystem()
    
    """Loading the data from the dictionary for analysis"""
    for _, outData in applicantData.items() :
        outApplicant = Applicant(outData["name"], outData["experience"], outData["education"], outData["gender"])
        unBiasedHiringSystem.addApplicants(outApplicant)
        biasedHiringSystem.addApplicants(outApplicant)
        
    outUnbiasedResults = unBiasedHiringSystem.makeDecisions()
    outBiasedResults = biasedHiringSystem.makeDecisions()
    
    resultsVisualizer(outUnbiasedResults, outBiasedResults)
        
if __name__ == "__main__" :
    main()