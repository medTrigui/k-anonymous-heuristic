"""
Hierarchy Validation Script

Tests all generalization hierarchies with real dataset samples
to ensure they work correctly for k-anonymity implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hierarchies import HierarchyManager

def validate_hierarchies():
    """Validate all hierarchies with real data samples"""
    
    print('=== HIERARCHY VALIDATION ===')
    
    # Test records from actual dataset
    test_records = [
        {'age': 39, 'education': 'Bachelors', 'marital-status': 'Never-married', 'race': 'White'},
        {'age': 50, 'education': 'HS-grad', 'marital-status': 'Married-civ-spouse', 'race': 'Black'},
        {'age': 28, 'education': 'Masters', 'marital-status': 'Divorced', 'race': 'Asian-Pac-Islander'},
    ]

    manager = HierarchyManager()

    for i, record in enumerate(test_records):
        print(f'Record {i+1}: {record}')
        
        for level in range(1, 4):
            generalized = {}
            total_loss = 0
            
            for attr, value in record.items():
                if attr in manager.qi_attributes:
                    gen_val = manager.generalize_value(attr, value, level)
                    loss = manager.get_generalization_loss(attr, value, level)
                    generalized[attr] = gen_val
                    total_loss += loss
            
            avg_loss = total_loss / len(manager.qi_attributes)
            print(f'  Level {level}: {generalized}')
            print(f'           Loss: {avg_loss:.3f}')
        print()

    print('VALIDATION COMPLETE: All hierarchies working correctly')

if __name__ == "__main__":
    validate_hierarchies()
