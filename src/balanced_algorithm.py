"""
K-Anonymity Implementation - BALANCED HEURISTIC VERSION

Better heuristic that:
1. Balances generalization across ALL QIs instead of exhausting one at a time
2. Uses smarter utility-aware selection with benefit/cost analysis
3. Avoids over-generalization by applying balance penalty

Author: Master's Student
Course: Data Privacy
Implementation: Balanced Algorithm (smart utility-aware selection)
"""

import pandas as pd
import numpy as np
import sys
import os
from collections import defaultdict

sys.path.append('..')
from hierarchies import HierarchyManager


class KAnonymityEngineBalanced:
    """Improved K-Anonymity with better balanced heuristics"""
    
    def __init__(self):
        self.hierarchy_manager = HierarchyManager()
        self.qi_attributes = ['age', 'education', 'marital-status', 'race']
        self.stats = {
            'total_records': 0,
            'suppressed_records': 0,
            'iterations': 0,
            'generalizations': {qi: 0 for qi in self.qi_attributes},
            'final_classes': 0
        }
    
    def load_full_dataset(self, file_path):
        """Load the COMPLETE Adult dataset"""
        columns = [
            'age', 'workclass', 'fnlwgt', 'education', 'education-num', 'marital-status', 
            'occupation', 'relationship', 'race', 'sex', 'capital-gain', 'capital-loss', 
            'hours-per-week', 'native-country', 'income'
        ]
        
        print("Loading FULL Adult dataset...")
        df = pd.read_csv(file_path, names=columns, skipinitialspace=True)
        print(f"Loaded {len(df)} records")
        
        # Initialize with diverse k-values
        total = len(df)
        df['k_value'] = 2  # Default
        df.loc[0:int(total*0.7), 'k_value'] = 2      # 70% need k=2
        df.loc[int(total*0.7):int(total*0.9), 'k_value'] = 3   # 20% need k=3
        df.loc[int(total*0.9):int(total*0.95), 'k_value'] = 4  # 5% need k=4
        df.loc[int(total*0.95):, 'k_value'] = 5       # 5% need k=5
        
        # Initialize tracking
        for qi in self.qi_attributes:
            df[f'{qi}_level'] = 0
            df[qi + '_gen'] = df[qi].astype(str)
        df['suppressed'] = False
        
        self.stats['total_records'] = len(df)
        print("K-value distribution:", dict(df['k_value'].value_counts().sort_index()))
        return df
    
    def create_equivalence_classes(self, df):
        """Group records by QI values"""
        classes = defaultdict(list)
        for idx, row in df.iterrows():
            if not row['suppressed']:
                qi_tuple = tuple(row[qi + '_gen'] for qi in self.qi_attributes)
                classes[qi_tuple].append(idx)
        return dict(classes)
    
    def find_violations(self, df, classes):
        """Find k-anonymity violations"""
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
    
    def estimate_merge_benefit(self, df, qi, violations):
        """
        IMPROVED: Estimate how many violations would be resolved by generalizing qi
        
        This simulates the generalization effect more accurately
        """
        current_level = df[f'{qi}_level'].iloc[0]
        next_level = current_level + 1
        
        # Create a temporary copy to simulate generalization
        temp_df = df.copy()
        
        # Apply generalization to temp data
        for idx, row in temp_df.iterrows():
            if not row['suppressed']:
                original_value = row[qi]
                try:
                    generalized = self.hierarchy_manager.generalize_value(qi, original_value, next_level)
                    temp_df.at[idx, qi + '_gen'] = generalized
                except:
                    # If generalization fails, use suppression
                    temp_df.at[idx, qi + '_gen'] = '*'
        
        # Count how many violations would be resolved
        temp_classes = self.create_equivalence_classes(temp_df)
        temp_violations = self.find_violations(temp_df, temp_classes)
        
        # Benefit = reduction in violations
        benefit = len(violations) - len(temp_violations)
        return max(0, benefit)  # Ensure non-negative
    
    def calculate_utility_cost(self, df, qi):
        """
        Calculate the utility cost of generalizing qi by one level
        
        Uses information loss from hierarchies and considers current state
        """
        current_level = df[f'{qi}_level'].iloc[0]
        next_level = current_level + 1
        max_level = self.hierarchy_manager.get_max_level(qi)
        
        # Avoid complete suppression unless absolutely necessary
        if next_level >= max_level:
            return 100.0  # Very high cost for suppression
        
        # Sample some values to estimate average cost
        sample_indices = df.sample(min(100, len(df))).index
        total_cost = 0
        
        for idx in sample_indices:
            original_value = df.at[idx, qi]
            try:
                current_loss = self.hierarchy_manager.get_generalization_loss(qi, original_value, current_level)
                next_loss = self.hierarchy_manager.get_generalization_loss(qi, original_value, next_level)
                total_cost += (next_loss - current_loss)
            except:
                total_cost += 0.3  # Default cost
        
        avg_cost = total_cost / len(sample_indices)
        
        # Add penalty for imbalanced generalization
        current_levels = [df[f'{other_qi}_level'].iloc[0] for other_qi in self.qi_attributes]
        max_current = max(current_levels)
        if next_level > max_current + 2:  # Penalize if this QI gets too far ahead
            avg_cost *= 2.0
        
        return avg_cost
    
    def select_best_qi_improved(self, df, violations):
        """
        IMPROVED QI selection with balanced utility-aware heuristic
        """
        candidates = []
        
        for qi in self.qi_attributes:
            current_level = df[f'{qi}_level'].iloc[0]
            max_level = self.hierarchy_manager.get_max_level(qi)
            
            if current_level >= max_level:
                continue  # Cannot generalize further
            
            # Calculate benefit (violations resolved)
            benefit = self.estimate_merge_benefit(df, qi, violations)
            
            # Calculate utility cost
            utility_cost = self.calculate_utility_cost(df, qi)
            
            # Score: benefit per unit cost, with balance penalty
            if utility_cost > 0 and benefit > 0:
                score = benefit / utility_cost
                candidates.append({
                    'qi': qi,
                    'benefit': benefit,
                    'cost': utility_cost,
                    'score': score,
                    'current_level': current_level
                })
        
        if not candidates:
            return None
        
        # Sort by score (higher = better)
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        # Additional logic: prefer lower generalization levels for balance
        best_candidates = [c for c in candidates if c['score'] >= candidates[0]['score'] * 0.8]
        
        # Among best candidates, prefer the one with lowest current level (for balance)
        selected = min(best_candidates, key=lambda x: x['current_level'])
        
        return selected['qi'], selected
    
    def apply_generalization(self, df, qi):
        """Apply one level of generalization"""
        current_level = df[f'{qi}_level'].iloc[0]
        new_level = current_level + 1
        
        for idx, row in df.iterrows():
            if not row['suppressed']:
                original_value = row[qi]
                try:
                    generalized = self.hierarchy_manager.generalize_value(qi, original_value, new_level)
                    df.at[idx, qi + '_gen'] = generalized
                except:
                    # Fallback to suppression if generalization fails
                    df.at[idx, qi + '_gen'] = '*'
                
                df.at[idx, f'{qi}_level'] = new_level
        
        self.stats['generalizations'][qi] = new_level
        return new_level
    
    def anonymize_improved(self, df, max_iterations=20):
        """
        Main algorithm with IMPROVED BALANCED heuristic
        """
        print("\nK-ANONYMITY ALGORITHM - IMPROVED BALANCED APPROACH")
        print("=" * 60)
        
        for iteration in range(max_iterations):
            self.stats['iterations'] = iteration + 1
            
            classes = self.create_equivalence_classes(df)
            violations = self.find_violations(df, classes)
            
            if iteration < 8 or iteration % 3 == 0:
                print(f"Iteration {iteration + 1}: {len(classes)} classes, {len(violations)} violations")
                # Show current generalization levels
                levels = {qi: df[f'{qi}_level'].iloc[0] for qi in self.qi_attributes}
                print(f"  Current levels: {levels}")
            
            if not violations:
                print("K-anonymity achieved!")
                break
            
            # Use improved selection
            result = self.select_best_qi_improved(df, violations)
            if result is None:
                print("No beneficial generalizations available")
                break
            
            best_qi, details = result
            new_level = self.apply_generalization(df, best_qi)
            
            if iteration < 8:
                print(f"  Selected {best_qi}: benefit={details['benefit']}, cost={details['cost']:.3f}, score={details['score']:.3f}")
        
        self.stats['final_classes'] = len(self.create_equivalence_classes(df))
        
        print(f"\nALGORITHM COMPLETED")
        print(f"Iterations: {self.stats['iterations']}")
        print(f"Final generalization levels: {self.stats['generalizations']}")
        print(f"Final equivalence classes: {self.stats['final_classes']}")
        
        return df
    
    def export_results(self, df):
        """Export complete results"""
        result_columns = [qi + '_gen' for qi in self.qi_attributes]
        other_cols = ['workclass', 'education-num', 'occupation', 'relationship', 
                     'sex', 'capital-gain', 'capital-loss', 'hours-per-week', 
                     'native-country', 'income']
        result_columns.extend(other_cols)
        
        result_df = df[result_columns].copy()
        rename_map = {qi + '_gen': qi for qi in self.qi_attributes}
        result_df = result_df.rename(columns=rename_map)
        
        output_file = '../output/balanced_results.csv'
        result_df.to_csv(output_file, index=False)
        
        print(f"\nIMPROVED dataset exported: {output_file}")
        print(f"Records: {len(result_df)} (100% preserved)")
        
        # Show sample of results
        print("\nSample of anonymized data:")
        sample_cols = ['age', 'education', 'marital-status', 'race']
        print(result_df[sample_cols].head(10).to_string())


# Test the improved version
if __name__ == "__main__":
    print("K-ANONYMITY IMPROVED IMPLEMENTATION")
    print("=" * 50)
    
    engine = KAnonymityEngineBalanced()
    df = engine.load_full_dataset('../datasets/adult.data')
    result = engine.anonymize_improved(df)
    engine.export_results(result)
    
    print("\nIMPROVED implementation completed!")
    print("This version uses BALANCED generalization instead of exhausting one QI at a time")
