"""
FIXED K-Anonymity Metrics Calculation

Implements proper distortion and precision metrics by analyzing actual generalized values
instead of looking for non-existent level columns.
"""

import pandas as pd
import numpy as np
import sys
import os

sys.path.append('..')
from hierarchies import HierarchyManager


class PrivacyMetricsFixed:
    """
    Calculate privacy and utility metrics for k-anonymized datasets
    Works with actual generalized values, not level columns
    """
    
    def __init__(self):
        self.hierarchy_manager = HierarchyManager()
        self.qi_attributes = ['age', 'education', 'marital-status', 'race']
    
    def determine_generalization_level(self, qi, generalized_value):
        """
        Determine what generalization level a value represents
        """
        if qi == 'age':
            if generalized_value == '*':
                return 4  # Complete suppression
            elif generalized_value in ['Young', 'Adult', 'Senior']:
                return 3  # Life stages
            elif generalized_value in ['[17-27)', '[28-37)', '[38-47)', '[48-57)', '[58-67)', '[68-77)', '[78-90]']:
                return 2  # 10-year ranges
            elif len(str(generalized_value)) > 3 and '[' in str(generalized_value):
                return 1  # 5-year ranges
            else:
                return 0  # Original values
                
        elif qi == 'education':
            if generalized_value == '*':
                return 4  # Complete suppression
            elif generalized_value in ['Degree', 'No-Degree']:
                return 3  # Broad categories
            elif generalized_value in ['Higher-Ed', 'Secondary', 'Primary']:
                return 2  # Education levels
            elif generalized_value in ['Advanced', 'College', 'High-School', 'Elementary']:
                return 1  # Detailed categories
            else:
                return 0  # Original values
                
        elif qi == 'marital-status':
            if generalized_value == '*':
                return 3  # Complete suppression
            elif generalized_value in ['Partnered', 'Not-Partnered']:
                return 2  # Partnership status
            elif generalized_value in ['Single', 'Married', 'Previously-Married']:
                return 1  # Relationship status
            else:
                return 0  # Original values
                
        elif qi == 'race':
            if generalized_value == '*':
                return 2  # Complete suppression
            elif generalized_value == 'Person':
                return 1  # Ethical generalization
            else:
                return 0  # Original values
        
        return 0  # Default to original
    
    def calculate_distortion(self, original_df, anonymized_df):
        """
        Calculate distortion metric (information loss)
        Based on actual generalized values in the anonymized dataset
        """
        total_distortion = 0.0
        
        for qi in self.qi_attributes:
            if qi in anonymized_df.columns:
                # Sample some values to determine generalization level
                sample_values = anonymized_df[qi].unique()
                
                # Get the generalization level (assume consistent across all records)
                level = self.determine_generalization_level(qi, sample_values[0])
                
                # Calculate distortion for this QI
                qi_distortion = self.hierarchy_manager.get_generalization_loss(qi, None, level)
                total_distortion += qi_distortion
                
                print(f"  {qi.upper()}: Level {level}, Distortion {qi_distortion:.3f}")
        
        # Average distortion across all QIs
        average_distortion = total_distortion / len(self.qi_attributes)
        return average_distortion
    
    def calculate_precision(self, anonymized_df):
        """
        Calculate precision metric using the proper academic formula:
        Prec(RT) = 1 - (1/|PT| · |NA|) · Σ(j=1 to |PT|) Σ(i=1 to |NA|) (hi/|DGHAi|)
        
        Where:
        - PT = Projected Table (anonymized data)
        - NA = set of quasi-identifiers  
        - hi = height of generalization for attribute Ai
        - |DGHAi| = total height of the domain generalization hierarchy for attribute Ai
        """
        num_records = len(anonymized_df)  # |PT|
        num_qi_attributes = len(self.qi_attributes)  # |NA|
        
        total_sum = 0.0
        
        print(f"  Using precision formula: Prec(RT) = 1 - (1/|PT|·|NA|) · Σ(hi/|DGHAi|)")
        print(f"  |PT| = {num_records}, |NA| = {num_qi_attributes}")
        
        for qi in self.qi_attributes:
            if qi in anonymized_df.columns:
                # Get generalization level for this QI
                unique_values = anonymized_df[qi].unique()
                hi = self.determine_generalization_level(qi, unique_values[0])  # height of generalization
                dgh_height = self.hierarchy_manager.get_max_level(qi)  # |DGHAi|
                
                # For each record, add (hi / |DGHAi|) to the sum
                qi_contribution = num_records * (hi / dgh_height) if dgh_height > 0 else 0
                total_sum += qi_contribution
                
                print(f"  {qi.upper()}: hi={hi}, |DGH|={dgh_height}, contribution={qi_contribution}")
        
        # Apply the precision formula
        precision = 1 - (total_sum / (num_records * num_qi_attributes))
        
        print(f"  Total sum = {total_sum}")
        print(f"  Precision = 1 - ({total_sum} / ({num_records} × {num_qi_attributes})) = {precision:.3f}")
        
        return precision
    
    def calculate_qi_distortion(self, original_df, anonymized_df, qi):
        """Calculate distortion for a specific QI"""
        if qi in anonymized_df.columns:
            sample_value = anonymized_df[qi].iloc[0]
            level = self.determine_generalization_level(qi, sample_value)
            return self.hierarchy_manager.get_generalization_loss(qi, None, level)
        return 0.0
    
    def calculate_qi_precision(self, anonymized_df, qi):
        """Calculate precision for a specific QI using the academic formula"""
        if qi in anonymized_df.columns:
            sample_value = anonymized_df[qi].iloc[0]
            hi = self.determine_generalization_level(qi, sample_value)
            dgh_height = self.hierarchy_manager.get_max_level(qi)
            
            # Apply the precision formula for a single QI
            if dgh_height > 0:
                qi_precision = 1 - (hi / dgh_height)
                return qi_precision
        return 1.0
