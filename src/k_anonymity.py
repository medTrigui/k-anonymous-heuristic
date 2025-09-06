"""
K-Anonymity Implementation for Adult Dataset

Master's thesis implementation of k-anonymity algorithm using generalization hierarchies.
Supports variable k-values per record and minimizes utility loss through greedy heuristics.

Author: Master's Student
Course: Data Privacy
"""

import pandas as pd
import numpy as np
import sys
import os
from collections import defaultdict

# Import hierarchies
sys.path.append('..')
from hierarchies import HierarchyManager


class KAnonymityEngine:
    """
    K-Anonymity algorithm implementation with generalization and suppression.
    
    Features:
    - Variable k-values per record
    - Greedy generalization strategy  
    - Utility loss minimization
    - Comprehensive metrics calculation
    """
    
    def __init__(self):
        self.hierarchy_manager = HierarchyManager()
        self.qi_attributes = ['age', 'education', 'marital-status', 'race']
        self.reset_statistics()
    
    def reset_statistics(self):
        """Reset algorithm statistics"""
        self.stats = {
            'total_records': 0,
            'suppressed_records': 0,
            'iterations': 0,
            'generalizations': {qi: 0 for qi in self.qi_attributes},
            'final_classes': 0,
            'violations_resolved': 0
        }
    
    def load_data(self, file_path, sample_size=None):
        """
        Load Adult dataset with proper column names
        
        Args:
            file_path: Path to adult.data file
            sample_size: Optional limit for testing (None = full dataset)
            
        Returns:
            DataFrame with initialized tracking columns
        """
        columns = [
            'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 
            'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 
            'hours-per-week', 'native-country', 'income'
        ]
        
        df = pd.read_csv(file_path, names=columns, skipinitialspace=True)
        
        if sample_size:
            df = df.head(sample_size)
        
        # Initialize k-values (default k=2, can be modified)
        df['k_value'] = 2
        
        # Initialize generalization tracking
        for qi in self.qi_attributes:
            df[f'{qi}_level'] = 0  # Current generalization level
            df[qi + '_gen'] = df[qi].astype(str)  # Generalized values
        
        df['suppressed'] = False
        self.stats['total_records'] = len(df)
        
        return df
    
    def set_k_values(self, df, k_distribution=None):
        """
        Set k-values for testing different privacy requirements
        
        Args:
            df: Dataset
            k_distribution: Dict {k_value: count} or None for default
        """
        if k_distribution:
            idx = 0
            for k_val, count in k_distribution.items():
                end_idx = min(idx + count, len(df))
                df.loc[idx:end_idx-1, 'k_value'] = k_val
                idx = end_idx
    
    def create_equivalence_classes(self, df):
        """
        Group records by identical QI values
        
        Returns:
            dict: {qi_tuple: [record_indices]}
        """
        classes = defaultdict(list)
        
        for idx, row in df.iterrows():
            if row['suppressed']:
                continue
            
            # Create tuple of current generalized QI values
            qi_tuple = tuple(row[qi + '_gen'] for qi in self.qi_attributes)
            classes[qi_tuple].append(idx)
        
        return dict(classes)
    
    def find_violations(self, df, classes):
        """
        Identify equivalence classes violating k-anonymity
        
        Returns:
            list: Violation details for each problematic class
        """
        violations = []
        
        for qi_tuple, indices in classes.items():
            max_k = df.loc[indices, 'k_value'].max()
            
            if len(indices) < max_k:
                violations.append({
                    'qi_tuple': qi_tuple,
                    'indices': indices,
                    'size': len(indices),
                    'required_k': max_k,
                    'deficit': max_k - len(indices)
                })
        
        return violations
    
    def select_best_generalization(self, df, violations):
        """
        Choose optimal QI to generalize using utility/benefit heuristic
        
        Strategy: Maximize violations fixed per unit of utility loss
        
        Returns:
            str: Best QI to generalize, or None if impossible
        """
        best_qi = None
        best_score = -1
        
        for qi in self.qi_attributes:
            current_level = df[f'{qi}_level'].iloc[0]  # All records same level
            max_level = self.hierarchy_manager.get_max_level(qi)
            
            if current_level >= max_level:
                continue  # Cannot generalize further
            
            # Estimate benefit: number of violations potentially resolved
            benefit = self._estimate_benefit(df, qi, violations)
            
            # Calculate utility cost
            sample_value = df[qi].iloc[0]
            current_loss = self.hierarchy_manager.get_generalization_loss(qi, sample_value, current_level)
            next_loss = self.hierarchy_manager.get_generalization_loss(qi, sample_value, current_level + 1)
            utility_cost = next_loss - current_loss
            
            # Score: benefit per unit cost (higher = better)
            if utility_cost > 0:
                score = benefit / utility_cost
                if score > best_score:
                    best_score = score
                    best_qi = qi
        
        return best_qi
    
    def _estimate_benefit(self, df, qi, violations):
        """
        Estimate how many violations would be resolved by generalizing qi
        
        Simple heuristic: assume generalization helps proportionally
        """
        return max(1, len(violations) // 2)  # Conservative estimate
    
    def apply_generalization(self, df, qi):
        """
        Apply one level of generalization to specified QI
        
        Updates all records with new generalized values
        """
        current_level = df[f'{qi}_level'].iloc[0]
        new_level = current_level + 1
        
        # Update all non-suppressed records
        for idx, row in df.iterrows():
            if not row['suppressed']:
                original_value = row[qi]
                generalized_value = self.hierarchy_manager.generalize_value(qi, original_value, new_level)
                df.at[idx, qi + '_gen'] = generalized_value
                df.at[idx, f'{qi}_level'] = new_level
        
        # Update statistics
        self.stats['generalizations'][qi] = new_level
        
        return new_level
    
    def apply_suppression(self, df, violations):
        """
        Suppress records that cannot be generalized further
        
        Strategy: Suppress smallest equivalence classes first
        """
        suppressed_count = 0
        
        # Sort violations by size (suppress smallest first)
        violations.sort(key=lambda x: x['size'])
        
        for violation in violations:
            indices = violation['indices']
            
            # Mark records as suppressed
            df.loc[indices, 'suppressed'] = True
            suppressed_count += len(indices)
            
            # Set all QI values to suppressed marker
            for qi in self.qi_attributes:
                df.loc[indices, qi + '_gen'] = '*'
        
        self.stats['suppressed_records'] = suppressed_count
        return suppressed_count
    
    def anonymize(self, df, max_iterations=15, verbose=True):
        """
        Main k-anonymity algorithm
        
        Args:
            df: Dataset to anonymize
            max_iterations: Maximum iterations to prevent infinite loops
            verbose: Print progress information
            
        Returns:
            Anonymized dataset
        """
        if verbose:
            print("K-ANONYMITY ALGORITHM")
            print("=" * 50)
            print(f"Records: {len(df)}")
            print(f"QI attributes: {self.qi_attributes}")
            k_dist = df['k_value'].value_counts().sort_index()
            print(f"K-values: {dict(k_dist)}")
            print()
        
        # Main algorithm loop
        for iteration in range(max_iterations):
            self.stats['iterations'] = iteration + 1
            
            # Create equivalence classes and find violations
            classes = self.create_equivalence_classes(df)
            violations = self.find_violations(df, classes)
            
            if verbose:
                print(f"Iteration {iteration + 1}: {len(classes)} classes, {len(violations)} violations")
            
            # Check if k-anonymity achieved
            if not violations:
                if verbose:
                    print("K-anonymity achieved!")
                break
            
            # Select and apply best generalization
            best_qi = self.select_best_generalization(df, violations)
            
            if best_qi is None:
                if verbose:
                    print("No more generalizations possible. Applying suppression.")
                self.apply_suppression(df, violations)
                break
            
            new_level = self.apply_generalization(df, best_qi)
            if verbose:
                print(f"  Generalized {best_qi} to level {new_level}")
        
        # Final cleanup if needed
        final_classes = self.create_equivalence_classes(df)
        final_violations = self.find_violations(df, final_classes)
        
        if final_violations:
            self.apply_suppression(df, final_violations)
        
        self.stats['final_classes'] = len(self.create_equivalence_classes(df))
        self.stats['violations_resolved'] = len(violations) if 'violations' in locals() else 0
        
        if verbose:
            self._print_final_stats()
        
        return df
    
    def _print_final_stats(self):
        """Print algorithm completion statistics"""
        print("\nALGORITHM COMPLETED")
        print("=" * 50)
        print(f"Iterations: {self.stats['iterations']}")
        print(f"Suppressed records: {self.stats['suppressed_records']}")
        print(f"Final equivalence classes: {self.stats['final_classes']}")
        print(f"Generalization levels: {self.stats['generalizations']}")
    
    def get_anonymized_dataset(self, df):
        """
        Extract clean anonymized dataset
        
        Returns:
            DataFrame with only necessary columns and proper naming
        """
        # Select anonymized QI columns
        result_columns = [qi + '_gen' for qi in self.qi_attributes]
        
        # Add other important columns (exclude tracking columns)
        other_cols = ['workclass', 'education-num', 'occupation', 'relationship', 
                     'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 
                     'native-country', 'income']
        
        for col in other_cols:
            if col in df.columns:
                result_columns.append(col)
        
        # Create result dataset
        result_df = df[~df['suppressed']][result_columns].copy()
        
        # Rename generalized columns to original names
        rename_map = {qi + '_gen': qi for qi in self.qi_attributes}
        result_df = result_df.rename(columns=rename_map)
        
        return result_df
    
    def export_results(self, df, output_dir='../output'):
        """Export anonymized dataset and summary statistics"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Export anonymized dataset
        anonymized_df = self.get_anonymized_dataset(df)
        output_file = os.path.join(output_dir, 'anonymized_dataset.csv')
        anonymized_df.to_csv(output_file, index=False)
        
        # Export statistics
        stats_file = os.path.join(output_dir, 'algorithm_stats.txt')
        with open(stats_file, 'w') as f:
            f.write("K-Anonymity Algorithm Results\n")
            f.write("=" * 40 + "\n")
            for key, value in self.stats.items():
                f.write(f"{key}: {value}\n")
        
        print(f"Results exported to {output_dir}")
        return output_file, stats_file


def main():
    """Main execution with sample dataset"""
    engine = KAnonymityEngine()
    
    # Load sample dataset
    df = engine.load_data('../datasets/adult.data', sample_size=200)
    
    # Set diverse k-values for testing
    engine.set_k_values(df, {2: 120, 3: 50, 4: 20, 5: 10})
    
    # Run algorithm
    anonymized_df = engine.anonymize(df)
    
    # Export results
    engine.export_results(anonymized_df)
    
    print("\nK-anonymity implementation completed successfully!")


if __name__ == "__main__":
    main()
