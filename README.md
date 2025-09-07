# K-Anonymity Algorithm Implementation

## Project Overview

This project implements and compares two different k-anonymity algorithms for the Adult Census Income dataset. The goal is to protect individual privacy through data anonymization while maintaining data utility for analysis purposes. This work demonstrates the trade-offs between privacy protection and data quality in real-world privacy-preserving data mining.

## Dataset

**Source**: UCI Machine Learning Repository - Adult Dataset (1994 US Census)
- **Training Data**: 32,561 records
- **Features**: 15 attributes including demographic and employment information
- **Target**: Income classification (≤$50K or >$50K)

### Quasi-Identifiers (QIs) Selected for Anonymization
We focused on four attributes that could potentially identify individuals:

1. **Age**: Continuous values (17-90 years)
2. **Education**: 16 categories (Preschool to Doctorate)  
3. **Marital-Status**: 7 categories (Married, Divorced, etc.)
4. **Race**: 5 categories (White, Black, Asian-Pac-Islander, Amer-Indian-Eskimo, Other)

## Step 1: Generalization Hierarchies Design

### Our Approach
We designed Domain Generalization Hierarchies (DGHs) for each QI to enable systematic generalization from specific to general values.

### 1. Age Hierarchy (5 levels)
```
Level 0: Original values (17, 18, 19, ..., 90)
Level 1: 5-year ranges ([17-22), [23-27), [28-32), ...)
Level 2: 10-year ranges ([17-27), [28-37), [38-47), ...)
Level 3: Life stages (Young, Adult, Senior)
Level 4: Complete suppression (*)
```

### 2. Education Hierarchy (5 levels)
```
Level 0: Original 16 categories (Bachelors, Masters, HS-grad, ...)
Level 1: Detailed categories (Advanced, College, High-School, Elementary)
Level 2: Education levels (Higher-Ed, Secondary, Primary)
Level 3: Broad categories (Degree, No-Degree)
Level 4: Complete suppression (*)
```

### 3. Marital-Status Hierarchy (4 levels)
```
Level 0: Original 7 categories (Married-civ-spouse, Divorced, ...)
Level 1: Relationship status (Single, Married, Previously-Married)
Level 2: Partnership status (Partnered, Not-Partnered)
Level 3: Complete suppression (*)
```

### 4. Race Hierarchy (3 levels) - Ethical Design
```
Level 0: Original 5 categories (White, Black, Asian-Pac-Islander, ...)
Level 1: Ethical generalization (Person)
Level 2: Complete suppression (*)
```

**Note**: We deliberately simplified the race hierarchy to avoid creating biased groupings. All races are generalized to "Person" to ensure ethical anonymization.

## Step 2: Algorithm Implementation

We implemented and compared two different k-anonymity algorithms:

### Algorithm 1: Greedy Algorithm (`greedy_algorithm.py`)

**Strategy**: Traditional greedy approach that completely generalizes one QI before moving to the next.

**How it works**:
1. Select the QI with lowest utility loss
2. Generalize it to the maximum level needed
3. Move to the next QI only when the current one is exhausted
4. Continue until k-anonymity is achieved

**Characteristics**:
- Simple and fast
- Tends to over-generalize specific attributes
- May result in complete suppression of some QIs

### Algorithm 2: Balanced Algorithm (`balanced_algorithm.py`)

**Strategy**: Smart heuristic using benefit/cost analysis with balance penalty.

**How it works**:
1. For each possible generalization step, calculate:
   - **Benefit**: Number of k-anonymity violations resolved
   - **Cost**: Increase in information loss
2. Apply balance penalty to prevent over-generalization of single QI
3. Select the generalization with best benefit/cost ratio
4. Distribute generalization evenly across all QIs

**Characteristics**:
- More sophisticated decision-making
- Preserves meaningful information across all QIs
- Better real-world utility

## Step 3: Implementation Details

### Algorithm Parameters
- **Dataset Size**: Full 32,561 records (not sample)
- **K-Value Distribution**: 
  - 70% of records require k=2
  - 20% of records require k=3
  - 5% of records require k=4
  - 5% of records require k=5

### Key Implementation Features
- Variable k-values per record
- No record suppression (100% data preservation)
- Systematic equivalence class management
- Comprehensive metrics calculation

## Step 4: Results and Analysis

### Algorithm Performance Comparison

| Metric | Greedy Algorithm | Balanced Algorithm |
|--------|------------------|-------------------|
| **Dataset Processed** | 32,561 records (100%) | 32,561 records (100%) |
| **Iterations** | 10 | 10 |
| **Suppressed Records** | 0 (0%) | 0 (0%) |
| **Final Equivalence Classes** | 20 | 12 |

### Privacy Metrics Results

**Precision Formula Used**: `Prec(RT) = 1 - (1/|PT| · |NA|) · Σ(hi/|DGHAi|)`

| Algorithm | Overall Distortion | Overall Precision |
|-----------|-------------------|-------------------|
| **Greedy** | 0.562 (56.2%) | **0.396 (39.6%)** |
| **Balanced** | 0.688 (68.8%) | 0.333 (33.3%) |

### Detailed QI Analysis

#### Greedy Algorithm Results:
- **Age**: Level 4/4 → Complete suppression (`*`) - **Total information loss**
- **Education**: Level 3/4 → "Degree"/"No-Degree" - Useful categories
- **Marital-Status**: Level 2/3 → "Partnered"/"Not-Partnered" - Good utility
- **Race**: Level 0/2 → Original values preserved - **Bias risk**

#### Balanced Algorithm Results:
- **Age**: Level 3/4 → "Adult"/"Young"/"Senior" - **Meaningful categories**
- **Education**: Level 3/4 → "Degree"/"No-Degree" - Same as greedy
- **Marital-Status**: Level 2/3 → "Partnered"/"Not-Partnered" - Same as greedy  
- **Race**: Level 1/2 → "Person" - **Ethical generalization**

## Key Findings and Analysis

### 1. The Metrics Paradox
**Important Discovery**: The greedy algorithm shows "better" mathematical metrics (higher precision 0.396 vs 0.333), but this is **misleading**.

**Why Greedy's Better Metrics Are Deceptive**:
- Achieves higher precision by completely destroying age information (precision 0.000)
- Preserves race information perfectly (precision 1.000) but creates bias risks
- Creates imbalanced anonymization with extreme information loss in one attribute

**Why Balanced's Lower Metrics Represent Better Design**:
- Lower precision reflects ethical choice to generalize race to "Person"
- Maintains meaningful age categories instead of complete suppression
- Provides better real-world utility despite higher mathematical distortion

### 2. Real-World Utility Comparison

**For Data Analysis Purposes**:
- **Greedy**: Age data is completely unusable (`*` provides no insight)
- **Balanced**: Age data remains meaningful for demographic analysis

**For Ethical Compliance**:
- **Greedy**: Preserves racial categories that could introduce bias in downstream analysis
- **Balanced**: Eliminates race-based bias through ethical "Person" generalization

### 3. Algorithm Trade-offs

| Aspect | Greedy Algorithm | Balanced Algorithm |
|--------|------------------|-------------------|
| **Computational Speed** | Faster (simpler logic) | Moderate (more complex) |
| **Mathematical Metrics** | Better (misleading) | Lower (but more honest) |
| **Real-world Utility** | Poor (age destroyed) | Excellent (age preserved) |
| **Ethical Considerations** | Concerning (race bias) | Strong (bias elimination) |
| **Recommended Use** | Quick prototypes only | Production applications |

## Conclusions

### Main Takeaways

1. **Metrics Don't Tell the Whole Story**: Mathematical metrics alone can be misleading in privacy applications. The greedy algorithm's "better" precision comes at the cost of completely destroying age information.

2. **Balanced Generalization is Superior**: The balanced algorithm demonstrates that distributing generalization across all QIs produces more useful anonymized data, even if mathematical metrics appear worse.

3. **Ethical Considerations Matter**: Our race hierarchy design shows that ethical considerations must override mathematical optimization. The balanced algorithm's ethical handling of race is more important than achieving better precision scores.

4. **Context-Aware Privacy**: Different applications may require different approaches, but for most real-world scenarios, the balanced algorithm provides better utility and ethical compliance.

### Recommendations

**For Academic Research**: Use the balanced algorithm as it demonstrates advanced privacy-preserving techniques with ethical considerations.

**For Industry Applications**: The balanced algorithm is recommended for production use due to its superior utility preservation and bias elimination.

**For Future Work**: Consider extending the balanced algorithm with additional optimization techniques while maintaining the ethical framework established in this implementation.

## Project Structure

```
k-anonymous-heuristic/
├── datasets/              # UCI Adult dataset files
├── hierarchies/           # DGH implementations for all QIs
├── src/                   # Algorithm implementations
│   ├── greedy_algorithm.py      # Greedy k-anonymity implementation
│   ├── balanced_algorithm.py    # Balanced k-anonymity implementation
│   ├── metrics_fixed.py         # Proper metrics calculation
│   ├── greedy_metrics.py        # Greedy algorithm metrics
│   └── balanced_metrics.py      # Balanced algorithm metrics
├── output/               # Results and analysis
│   ├── greedy_results.csv       # Greedy algorithm output (32,561 records)
│   ├── balanced_results.csv     # Balanced algorithm output (32,561 records)
│   ├── comparison.md            # Detailed algorithm comparison
│   └── summary.md               # Executive summary
├── docs/                 # LaTeX documentation
└── analysis/             # Data exploration scripts
```

## Getting Started

1. **Run Greedy Algorithm**: `python src/greedy_algorithm.py`
2. **Run Balanced Algorithm**: `python src/balanced_algorithm.py`
3. **Calculate Metrics**: `python src/greedy_metrics.py` and `python src/balanced_metrics.py`
4. **View Results**: Check `output/` directory for anonymized datasets and analysis

## Technical Implementation

- **Language**: Python 3.x
- **Key Libraries**: pandas, numpy
- **Metrics**: Academic standard precision formula implementation
- **Testing**: Comprehensive validation with full UCI Adult dataset
- **Documentation**: Complete LaTeX specifications for all hierarchies

This project demonstrates the importance of considering both mathematical metrics and real-world utility in privacy-preserving data mining, showing that ethical considerations and practical utility often outweigh pure mathematical optimization.