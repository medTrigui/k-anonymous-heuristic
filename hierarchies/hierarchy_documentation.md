# Generalization Hierarchies Documentation

## Overview

This document describes the generalization hierarchies designed for the 4 quasi-identifiers in the Adult Census Income dataset. Each hierarchy is carefully designed based on data analysis and semantic meaning to balance privacy protection with data utility.

## Design Principles

1. **Semantic Preservation**: Generalizations maintain meaningful relationships
2. **Balanced Distribution**: Levels provide reasonable data distribution  
3. **Progressive Generalization**: Each level provides increasing privacy
4. **Domain Knowledge**: Hierarchies reflect real-world categorizations

## Hierarchy Specifications

### 1. Age Hierarchy (4 levels + suppression)

**Data Characteristics:**
- Range: 17-90 years
- Mean: 38.6, Median: 37
- Distribution: Relatively normal with slight right skew

**Hierarchy Levels:**
```
Level 0: Specific Age (73 values)
├── 17, 18, 19, ..., 90

Level 1: 5-Year Ranges (12 ranges)
├── [17-22), [22-27), [27-32), [32-37), [37-42), [42-47)
├── [47-52), [52-57), [57-62), [62-67), [67-72), [72+)

Level 2: 10-Year Ranges (6 ranges)
├── [17-27), [27-37), [37-47), [47-57), [57-67), [67+)

Level 3: Life Stages (3 categories)
├── Young [17-30): Early career, education phase
├── Adult [30-55): Prime working years  
├── Senior [55+): Pre-retirement/retirement

Level 4: Suppressed (1 value)
└── * (Complete suppression)
```

**Information Loss by Level:**
- Level 0: 0.0 (no loss)
- Level 1: 0.2 (5-year ranges)
- Level 2: 0.4 (10-year ranges)
- Level 3: 0.7 (life stages)
- Level 4: 1.0 (suppressed)

### 2. Education Hierarchy (4 levels + suppression)

**Data Characteristics:**
- 16 unique categories from Preschool to Doctorate
- Top categories: HS-grad (32%), Some-college (22%), Bachelors (16%)
- Natural education progression

**Hierarchy Levels:**
```
Level 0: Specific Education (16 categories)
├── Preschool, 1st-4th, 5th-6th, 7th-8th, 9th, 10th, 11th, 12th
├── HS-grad, Some-college, Assoc-voc, Assoc-acdm  
└── Bachelors, Masters, Prof-school, Doctorate

Level 1: Detailed Levels (8 categories)
├── Elementary: Preschool, 1st-4th, 5th-6th
├── Middle: 7th-8th, 9th
├── High-School: 10th, 11th, 12th, HS-grad
├── Some-College: Some-college
├── Associate: Assoc-voc, Assoc-acdm
├── Bachelors: Bachelors
└── Graduate: Masters, Prof-school, Doctorate

Level 2: Education Level (4 categories)
├── K12: Elementary, Middle, High-School
├── Some-College: Some-college
├── College-Degree: Associate, Bachelors
└── Graduate-Degree: Graduate

Level 3: Broad Category (2 categories)
├── No-Degree: K12, Some-College
└── Degree: College-Degree, Graduate-Degree

Level 4: Suppressed (1 value)
└── * (Complete suppression)
```

**Information Loss by Level:**
- Level 0: 0.0 (no loss)
- Level 1: 0.15 (detailed levels)
- Level 2: 0.35 (education levels)
- Level 3: 0.65 (broad categories)
- Level 4: 1.0 (suppressed)

### 3. Marital Status Hierarchy (3 levels + suppression)

**Data Characteristics:**
- 7 unique categories
- Distribution: Married-civ-spouse (46%), Never-married (33%), Divorced (14%)
- Natural relationship status groupings

**Hierarchy Levels:**
```
Level 0: Specific Status (7 categories)
├── Married-civ-spouse, Married-spouse-absent, Married-AF-spouse
├── Never-married
└── Divorced, Separated, Widowed

Level 1: Relationship Status (3 categories)
├── Married: All married variants
├── Single: Never-married
└── Previously-Married: Divorced, Separated, Widowed

Level 2: Partnership Status (2 categories)
├── Partnered: Married
└── Not-Partnered: Single, Previously-Married

Level 3: Suppressed (1 value)
└── * (Complete suppression)
```

**Information Loss by Level:**
- Level 0: 0.0 (no loss)
- Level 1: 0.3 (relationship status)
- Level 2: 0.6 (partnership status)
- Level 3: 1.0 (suppressed)

### 4. Race Hierarchy (3 levels + suppression)

**Data Characteristics:**
- 5 unique categories
- Distribution: White (85%), Black (10%), Asian-Pac-Islander (3%), Others (2%)
- Sensitive attribute requiring careful handling

**Hierarchy Levels:**
```
Level 0: Specific Race (5 categories)
├── White, Black, Asian-Pac-Islander
└── Amer-Indian-Eskimo, Other

Level 1: Ethnic Group (3 categories)
├── White: White
├── Asian: Asian-Pac-Islander  
└── Other-Minority: Black, Amer-Indian-Eskimo, Other

Level 2: Majority/Minority (2 categories)
├── White: White
└── Non-White: All others

Level 3: Suppressed (1 value)
└── * (Complete suppression)
```

**Information Loss by Level:**
- Level 0: 0.0 (no loss)
- Level 1: 0.4 (ethnic groups)
- Level 2: 0.7 (majority/minority)
- Level 3: 1.0 (suppressed)

## Implementation Notes

### Missing Values
- According to the specification, missing values (marked as "?") should be treated as "generalized to the top of hierarchy"
- In our implementation, missing values will be mapped to the suppressed level (*) for each attribute

### Precision Calculation
Each hierarchy class provides methods to calculate the precision (inverse of generalization range size) for use in utility metrics.

### Usage in K-Anonymity Algorithm
The hierarchies are managed through the `HierarchyManager` class which provides:
- Unified interface for all attributes
- Generalization and utility loss calculation
- Integration with the k-anonymity algorithm

## Design Rationale

### Age
- **Life stages** reflect meaningful demographic categories
- **Range sizes** balance privacy with utility
- **Boundaries** align with career/life transitions

### Education  
- **Natural progression** from elementary to graduate level
- **Semantic groupings** preserve educational meaning
- **Balanced categories** maintain statistical utility

### Marital Status
- **Relationship focus** captures primary demographic significance
- **Partnership status** provides meaningful binary classification
- **Social relevance** aligns with demographic analysis needs

### Race
- **Sensitivity awareness** with careful majority/minority handling
- **Census alignment** follows US demographic categorizations
- **Cultural respect** maintains meaningful ethnic distinctions at intermediate levels

These hierarchies provide the foundation for implementing effective k-anonymity while preserving maximum data utility.
