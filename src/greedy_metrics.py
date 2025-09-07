"""
Calculate metrics for the GREEDY K-Anonymity algorithm
"""

import pandas as pd
import sys
import os

sys.path.append('..')
from hierarchies import HierarchyManager
from metrics_fixed import PrivacyMetricsFixed

def main():
    """Calculate and display metrics for greedy algorithm"""
    print("=" * 60)
    print("METRICS CALCULATION - GREEDY ALGORITHM")
    print("=" * 60)
    
    # Load original and anonymized datasets
    print("Loading datasets...")
    original_df = pd.read_csv('../datasets/adult.data', names=[
        'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 
        'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 
        'hours-per-week', 'native-country', 'income'
    ], skipinitialspace=True)
    
    # Use FULL dataset (like greedy algorithm now does)
    # original_df = original_df (already full dataset)
    
    try:
        anonymized_df = pd.read_csv('../output/greedy_results.csv')
    except FileNotFoundError:
        print("ERROR: Greedy anonymized dataset not found. Run k_anonymity_greedy.py first.")
        return
    
    print(f"Original dataset: {len(original_df)} records")
    print(f"Anonymized dataset: {len(anonymized_df)} records")
    print(f"Suppression rate: {1 - len(anonymized_df)/len(original_df):.3f}")
    print()
    
    # Calculate metrics using FIXED calculation
    metrics_calculator = PrivacyMetricsFixed()
    
    # Calculate distortion and precision with FIXED calculation
    print("Calculating distortion by QI:")
    distortion = metrics_calculator.calculate_distortion(original_df, anonymized_df)
    print(f"\nCalculating precision by QI:")
    precision = metrics_calculator.calculate_precision(anonymized_df)
    suppression_rate = 1 - len(anonymized_df) / len(original_df)
    
    # Generate report
    report = f"""
GREEDY K-ANONYMITY ALGORITHM - METRICS REPORT
==============================================

Dataset Information:
- Original records: {len(original_df)}
- Anonymized records: {len(anonymized_df)}
- Suppressed records: {len(original_df) - len(anonymized_df)}
- Suppression rate: {suppression_rate:.3f}

Generalization Analysis:
- Algorithm approach: Greedy (exhaust one QI before trying others)
- Dataset: Full Adult dataset (32,561 records)

Privacy Metrics:
- Overall Distortion: {distortion:.3f}
- Overall Precision: {precision:.3f}
- Suppression Rate: {suppression_rate:.3f}

Individual QI Analysis:
"""
    
    # Add individual QI metrics
    qi_attributes = ['age', 'education', 'marital-status', 'race']
    hm = HierarchyManager()
    
    for qi in qi_attributes:
        if f'{qi}_generalized' in anonymized_df.columns:
            qi_distortion = metrics_calculator.calculate_qi_distortion(original_df, anonymized_df, qi)
            qi_precision = metrics_calculator.calculate_qi_precision(anonymized_df, qi)
            
            report += f"- {qi.upper()}:\n"
            report += f"  * Distortion: {qi_distortion:.3f}\n"
            report += f"  * Precision: {qi_precision:.3f}\n"
    
    report += f"""
Algorithm Characteristics:
- Strategy: Greedy selection (lowest utility loss first)
- Behavior: Completely generalizes one QI before trying others
- Result: Tends to over-generalize age and education to suppression
- Efficiency: Fast but suboptimal utility preservation

Notes:
- Greedy approach prioritizes computational speed over utility
- Results in significant suppression of age and education
- May not be optimal for real-world privacy applications
"""
    
    print(report)
    
    # Save report
    with open('../output/greedy_metrics.txt', 'w') as f:
        f.write(report)
    
    print(f"Metrics report saved to: ../output/greedy_metrics.txt")
    
    return {
        'distortion': distortion,
        'precision': precision,
        'suppression_rate': suppression_rate
    }

if __name__ == "__main__":
    main()
