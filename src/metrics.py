"""
K-Anonymity Metrics Calculation

Implements distortion and precision metrics for evaluating k-anonymity algorithm performance.
Based on standard privacy-preserving data mining metrics.

Author: Master's Student
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append('..')
from hierarchies import HierarchyManager


class PrivacyMetrics:
    """
    Calculate privacy and utility metrics for k-anonymized datasets
    
    Metrics implemented:
    - Distortion: Information loss due to generalization
    - Precision: Data quality preservation measure
    - Suppression rate: Percentage of suppressed records
    """
    
    def __init__(self):
        self.hierarchy_manager = HierarchyManager()
        self.qi_attributes = ['age', 'education', 'marital-status', 'race']
    
    def calculate_distortion(self, original_df, anonymized_df):
        """
        Calculate distortion metric (information loss)
        
        Distortion = Average information loss across all QI attributes
        
        Args:
            original_df: Original dataset
            anonymized_df: Anonymized dataset with generalization levels
            
        Returns:
            float: Distortion value [0, 1] where 0 = no loss, 1 = complete loss
        """
        total_distortion = 0.0
        
        for qi in self.qi_attributes:
            # Get generalization level for this QI
            if f'{qi}_level' in anonymized_df.columns:
                level = anonymized_df[f'{qi}_level'].iloc[0]  # All records same level
            else:
                level = 0  # No generalization
            
            # Calculate information loss for this QI
            sample_value = original_df[qi].iloc[0]
            qi_distortion = self.hierarchy_manager.get_generalization_loss(qi, sample_value, level)
            
            total_distortion += qi_distortion
        
        # Average across all QI attributes
        return total_distortion / len(self.qi_attributes)
    
    def calculate_precision(self, anonymized_df):
        """
        Calculate precision metric (granularity preservation)
        
        Precision = Average precision across all QI attributes
        Precision per QI = 1 / (generalization_range_size)
        
        Returns:
            float: Precision value [0, 1] where 1 = highest precision
        """
        total_precision = 0.0
        
        for qi in self.qi_attributes:
            # Get current generalization level
            if f'{qi}_level' in anonymized_df.columns:
                level = anonymized_df[f'{qi}_level'].iloc[0]
            else:
                level = 0
            
            # Calculate precision based on hierarchy level
            if level == 0:
                qi_precision = 1.0  # No generalization = full precision
            else:
                # Precision decreases with generalization level
                max_level = self.hierarchy_manager.get_max_level(qi)
                qi_precision = (max_level - level) / max_level
            
            total_precision += qi_precision
        
        # Average across all QI attributes
        return total_precision / len(self.qi_attributes)
    
    def calculate_suppression_rate(self, original_df, anonymized_df):
        """
        Calculate percentage of suppressed records
        
        Returns:
            float: Suppression rate [0, 1]
        """
        if 'suppressed' in anonymized_df.columns:
            suppressed_count = anonymized_df['suppressed'].sum()
        else:
            suppressed_count = 0
        
        return suppressed_count / len(original_df)
    
    def calculate_utility_loss(self, distortion, suppression_rate):
        """
        Calculate combined utility loss metric
        
        Utility Loss = weighted combination of distortion and suppression
        
        Returns:
            float: Overall utility loss [0, 1]
        """
        # Weight generalization vs suppression (suppression typically worse)
        generalization_weight = 0.6
        suppression_weight = 0.4
        
        return (generalization_weight * distortion + 
                suppression_weight * suppression_rate)
    
    def analyze_equivalence_classes(self, anonymized_df):
        """
        Analyze distribution of equivalence class sizes
        
        Returns:
            dict: Class size statistics
        """
        if 'suppressed' in anonymized_df.columns:
            active_df = anonymized_df[~anonymized_df['suppressed']]
        else:
            active_df = anonymized_df
        
        # Group by generalized QI values
        qi_cols = [qi + '_gen' if qi + '_gen' in active_df.columns else qi 
                  for qi in self.qi_attributes]
        
        if all(col in active_df.columns for col in qi_cols):
            groups = active_df.groupby(qi_cols).size()
            
            return {
                'total_classes': len(groups),
                'min_size': groups.min(),
                'max_size': groups.max(),
                'avg_size': groups.mean(),
                'median_size': groups.median(),
                'size_distribution': groups.value_counts().sort_index().to_dict()
            }
        else:
            return {'error': 'Missing generalized columns'}
    
    def verify_k_anonymity(self, anonymized_df):
        """
        Verify that k-anonymity is satisfied
        
        Returns:
            dict: Verification results
        """
        if 'suppressed' in anonymized_df.columns:
            active_df = anonymized_df[~anonymized_df['suppressed']]
        else:
            active_df = anonymized_df
        
        violations = []
        
        # Group by QI values
        qi_cols = [qi + '_gen' if qi + '_gen' in active_df.columns else qi 
                  for qi in self.qi_attributes]
        
        if all(col in active_df.columns for col in qi_cols):
            for qi_values, group in active_df.groupby(qi_cols):
                max_k = group['k_value'].max() if 'k_value' in group.columns else 2
                if len(group) < max_k:
                    violations.append({
                        'qi_values': qi_values,
                        'size': len(group),
                        'required_k': max_k
                    })
        
        return {
            'is_k_anonymous': len(violations) == 0,
            'violations': len(violations),
            'violation_details': violations
        }
    
    def generate_comprehensive_report(self, original_df, anonymized_df, algorithm_stats=None):
        """
        Generate comprehensive privacy and utility analysis report
        
        Returns:
            dict: Complete metrics report
        """
        report = {
            'dataset_info': {
                'original_records': len(original_df),
                'anonymized_records': len(anonymized_df[~anonymized_df.get('suppressed', False)]),
                'qi_attributes': self.qi_attributes
            },
            
            'privacy_metrics': {
                'distortion': self.calculate_distortion(original_df, anonymized_df),
                'precision': self.calculate_precision(anonymized_df),
                'suppression_rate': self.calculate_suppression_rate(original_df, anonymized_df)
            },
            
            'utility_metrics': {},
            'equivalence_classes': self.analyze_equivalence_classes(anonymized_df),
            'k_anonymity_verification': self.verify_k_anonymity(anonymized_df)
        }
        
        # Calculate combined utility loss
        report['utility_metrics']['utility_loss'] = self.calculate_utility_loss(
            report['privacy_metrics']['distortion'],
            report['privacy_metrics']['suppression_rate']
        )
        
        # Add algorithm statistics if provided
        if algorithm_stats:
            report['algorithm_performance'] = algorithm_stats
        
        return report
    
    def export_report(self, report, output_dir='../output', filename='privacy_metrics_report.txt'):
        """Export detailed metrics report to file"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("K-ANONYMITY PRIVACY METRICS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            # Dataset info
            f.write("DATASET INFORMATION\n")
            f.write("-" * 20 + "\n")
            for key, value in report['dataset_info'].items():
                f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Privacy metrics
            f.write("PRIVACY METRICS\n")
            f.write("-" * 15 + "\n")
            for key, value in report['privacy_metrics'].items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.4f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Utility metrics
            f.write("UTILITY METRICS\n")
            f.write("-" * 15 + "\n")
            for key, value in report['utility_metrics'].items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.4f}\n")
                else:
                    f.write(f"{key}: {value}\n")
            f.write("\n")
            
            # Equivalence classes
            f.write("EQUIVALENCE CLASS ANALYSIS\n")
            f.write("-" * 26 + "\n")
            eq_stats = report['equivalence_classes']
            if 'error' not in eq_stats:
                f.write(f"Total classes: {eq_stats['total_classes']}\n")
                f.write(f"Size range: {eq_stats['min_size']} - {eq_stats['max_size']}\n")
                f.write(f"Average size: {eq_stats['avg_size']:.2f}\n")
                f.write(f"Median size: {eq_stats['median_size']:.2f}\n")
            else:
                f.write(f"Error: {eq_stats['error']}\n")
            f.write("\n")
            
            # K-anonymity verification
            f.write("K-ANONYMITY VERIFICATION\n")
            f.write("-" * 23 + "\n")
            verification = report['k_anonymity_verification']
            f.write(f"K-anonymous: {verification['is_k_anonymous']}\n")
            f.write(f"Violations: {verification['violations']}\n")
            
            if verification['violations'] > 0:
                f.write("Violation details:\n")
                for i, violation in enumerate(verification['violation_details'][:5]):  # Show first 5
                    f.write(f"  {i+1}. Size {violation['size']}, Required k={violation['required_k']}\n")
        
        print(f"Metrics report exported to: {filepath}")
        return filepath


def main():
    """Test metrics calculation with sample data"""
    # This would typically be called after running the k-anonymity algorithm
    print("Privacy Metrics Calculator")
    print("Use this module after running k_anonymity.py")


if __name__ == "__main__":
    main()
