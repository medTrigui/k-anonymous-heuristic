# K-Anonymity Algorithm Implementation

## Project Overview

This project implements a heuristic algorithm to ensure k-anonymity for the Adult Census Income dataset from the UCI Machine Learning Repository. The goal is to protect individual privacy while maintaining data utility through generalization and suppression techniques.

## Objectives

### Core Requirements
- **Dataset**: Adult Census Income dataset (UCI ML Repository)
- **Quasi-Identifiers**: 4 attributes to anonymize
  1. `age` (continuous)
  2. `education` (16 categories)
  3. `marital-status` (7 categories) 
  4. `race` (5 categories)
- **K-Anonymity**: Ensure each record appears at least k times in equivalence classes
- **Missing Values**: Treated as "generalized to top of hierarchy"
- **Variable K**: Each record can specify different k values

### Implementation Tasks

#### 1. Generalization Hierarchies
Define hierarchical structures for each quasi-identifier:
- **Age**: Continuous → Age ranges → Broader ranges
- **Education**: Specific degrees → Education levels → General categories
- **Marital Status**: Specific status → Grouped status → General categories
- **Race**: Specific races → Ethnic groups → General categories

#### 2. Heuristic Algorithm
Implement k-anonymity algorithm with:
- Generalization and/or suppression techniques
- Utility loss minimization
- Support for variable k values per record
- Equivalence class management

#### 3. Metrics Calculation
Calculate and report:
- **Distortion**: Measure of information loss
- **Precision**: Measure of data quality preservation

## Project Structure

```
k-anonymous-heuristic/
├── datasets/           # Original dataset files
│   ├── adult.data     # Training data (32,561 records)
│   ├── adult.test     # Test data (16,283 records)
│   └── adult.names    # Dataset description
├── src/               # Source code
├── hierarchies/       # Generalization hierarchy definitions
├── output/           # Anonymized datasets and results
├── docs/             # Documentation and analysis
├── tests/            # Unit tests
└── README.md         # This file
```

## Dataset Information

- **Source**: 1994 US Census Bureau
- **Records**: 48,844 total (train: 32,561, test: 16,283)
- **Task**: Predict if income >$50K or ≤$50K
- **Attributes**: 15 total (14 features + 1 target)

### Quasi-Identifiers for Anonymization
1. **Age**: Continuous values (16-90)
2. **Education**: 16 categories from Preschool to Doctorate
3. **Marital-Status**: 7 categories of marital status
4. **Race**: 5 racial categories

## Implementation Plan

### Phase 1: Setup and Analysis
- [x] Project structure creation
- [x] Dataset exploration and understanding
- [ ] Detailed data analysis and preprocessing

### Phase 2: Hierarchy Design
- [ ] Design age generalization hierarchy
- [ ] Design education generalization hierarchy  
- [ ] Design marital-status generalization hierarchy
- [ ] Design race generalization hierarchy

### Phase 3: Algorithm Implementation
- [ ] Core k-anonymity algorithm
- [ ] Generalization functions
- [ ] Suppression mechanisms
- [ ] Utility optimization heuristics

### Phase 4: Evaluation
- [ ] Distortion metric calculation
- [ ] Precision metric calculation
- [ ] Performance analysis
- [ ] Result documentation

## Deliverables

1. **Input Dataset**: Original adult.data and adult.test files
2. **Output Dataset**: Anonymized versions with k-anonymity guaranteed
3. **Source Code**: Complete implementation in chosen programming language
4. **Hierarchies**: Formal definitions of generalization hierarchies
5. **Metrics**: Distortion and precision results with analysis

## Getting Started

1. Ensure you have the dataset files in the `datasets/` directory
2. Review the generalization hierarchies in `hierarchies/`
3. Run the anonymization algorithm from `src/`
4. Check results in `output/` directory

## References

- [UCI Adult Dataset](https://archive.ics.uci.edu/ml/datasets/Adult)
- [Original Dataset Description](https://archive.ics.uci.edu/ml/machine-learning-databases/adult/old.adult.names)
- K-anonymity research papers and implementation guidelines
