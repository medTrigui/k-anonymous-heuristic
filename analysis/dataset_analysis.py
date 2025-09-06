"""
Adult Dataset Analysis Script

Analyzes the Adult Census Income dataset to understand the distribution
of quasi-identifiers for k-anonymity hierarchy design.
"""

import pandas as pd
import numpy as np

def analyze_dataset():
    """Analyze the Adult dataset for hierarchy design"""
    
    # Load the dataset
    columns = ['age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 
               'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 
               'hours-per-week', 'native-country', 'income']

    df = pd.read_csv('datasets/adult.data', names=columns, skipinitialspace=True)

    print('=== ADULT DATASET ANALYSIS ===')
    print(f'Total records: {len(df)}')
    print()

    # Analyze quasi-identifiers
    qi_attributes = ['age', 'education', 'marital-status', 'race']
    
    for attr in qi_attributes:
        print(f'=== {attr.upper()} ANALYSIS ===')
        
        if attr == 'age':
            print(f'Range: {df[attr].min()} - {df[attr].max()}')
            print(f'Mean: {df[attr].mean():.1f}')
            print(f'Median: {df[attr].median():.1f}')
            print(f'Unique values: {df[attr].nunique()}')
            print('Distribution (percentiles):')
            print(df[attr].describe())
        else:
            print(f'Unique values: {df[attr].nunique()}')
            print('Value counts:')
            print(df[attr].value_counts())
        print()

    # Check for missing values
    print('=== MISSING VALUES ===')
    for attr in qi_attributes:
        missing = (df[attr] == '?').sum()
        print(f'{attr}: {missing} missing values')
    print()

if __name__ == "__main__":
    analyze_dataset()
