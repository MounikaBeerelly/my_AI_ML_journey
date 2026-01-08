### Statistical Mean
- The `Statistical Mean` is a measure of `central tendency` that represents the `central or typical value` of a dataset.
- For a dataset with n observations :
$$
\text{Mean} = \frac{\sum_{i=1}^{n} x_i}{n}
$$

### When should you use Mean ?
- Data is symmetrical
- No extreme outliers
- Interval or ration scale data
- you need mathematical modeling

### Types of Statistical Means 
1. Arithmetic Mean --> Use General Data
2. Weighted Mean --> Importance Based
3. Geometric Mean --> Growth Rate oriented data
4. Harmonic Mean --> Rates & Ratios
5. Root Mean Square (RMS) Mean --> Signals and Errros
6. Trimmed Mean --> Outlier Resistant
7. Winsorized Mean --> Risk Analysis
8. Sample Mean --> Estimation
9. Population Mean --> Complete Data
10. Moving Mean --> Time Series
11. Expected Mean --> Probability

### What is Arithmetic Mean (AM) ?
- The Arithmetic Mean (AM) is the sum of all numerical observations divided by the number of observations.
- It represents the central value around which the data is distributed.
#### How many ways we can implement Arithmetic Mean?
- Arithmetic Mean applied on Ungrouped data.
- Arithmetic Mean applied on grouped (Frequency) data.
- Population Arithmetic Mean
- Sample Arithmetic Mean

#### Important Properties of Arithmetic Mean :
- Zero Deviation property
- Linear Transformation Property
- Combined Mean Formula 

### What is Weighted Mean ?
- The `Weighted Mean` is a measure of central tendency where `each observation contributes proportionally according to its assigned weight`.
- Weighted Mean reflects `relative importance, frequency, or reliability` of each value.

## Understanding the Concept of Geometric Mean :
- The `Geometric Mean (GM)` is a type of average that represents the `central tendency of multiplicative or proportional data`.
- Geometric Mean instead of adding values (As in Arithmetic Mean), it multiplies values and takes a root.
- General Formula : **GM = $\sqrt[n]{x_1 \times x_2 \times \cdots \times x_n}$**

- Logarithmetic Form (used in ML & Big data) :
$$
\text{GM} = \exp\left(\frac{1}{n}\sum_{i=1}^{n} \ln(x_i)\right)
$$

#### When to use Geometrical Mean :
1. Values are positive
2. Data is Multiplicative by nature
3. When we have percentages, rations and growth factors are existing
#### Types in GM ? 
1. Simple Geometric Mean
2. Weighted Geometric Mean
3. Log-Geometric Mean
