## Problem Statement: Compund Event Analysis in Fraud Detection

### Context of the problem :
1. Financial Institutions like Banks and Digital Payments system face continuous challenges in detecting fraudulent transactions.
2. Fraudulent brhavior generally involves multiple risk factors occuring together like
    - International transactions
    - High value amounts
3. To strengthen the fraud detection mechanism, the business environemnt has to analyze how the probability of fraud changes, especially when compound conditions are met, like `the transaction is an international transaction and involved with high value amount`.

### Objective of the Problem Statement :
1. To determine and visualize the `compound probability` of the Fraud in online transactions across multiple years.
2. Analyze the relationship between
    1. `Event A` : Transaction is and International (Country of transaction != country of the customer)
    2. `Event B` : Transaction is of high volume (Amount)
        - This value is given the Institution
        - For example: amount > ₹3,000
    3. `Event C` : Transaction is Fraudulent

### Key Analytical Goal :
1. `P(Fraud)` : Probability of any transaction being fraudulent
2. `P(International)` : Probability of transaction being international
3. `P(HighValue)` : Probability of transaction being high value
4. `P(International ∩ HighValue)` : Probability that a transaction is both international and high value
5. `P(Fraud | International ∩ HighValue)` : Compound Event Probability - Probability that a transaction is fraudulent given that it is both "International and High Value"

### Analytical Tasks :
1. Compute all the individual and compound probabilities for each year.
2. Analyze how the conditional probability P(Fraud | International ∩ HighValue) varies annually
3. Compare "Compound Fraud Probabilities" against "Overall Fraud Rates" to understand the "Bias towards the risky transaction types"
4. Visualize the trends using Line plots for interpretability.

### Expected outcome OR Deliverables :
1. A clear trend visulaization of fraud probability over time
2. Get quantifies insights showing whether "International High-value transactions are significantly more prone to fraud"
3. A foundation for developing "Rule-Based" OR "Probabilistic" fraud alert mechanism in the financial system.