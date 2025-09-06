"""
K-Anonymity Generalization Hierarchies

This module contains the generalization hierarchies for the 4 quasi-identifiers
used in the Adult dataset k-anonymity implementation.

Quasi-Identifiers:
1. Age - Continuous values (17-90) with range-based generalization
2. Education - 16 categories with education level grouping  
3. Marital-Status - 7 categories with relationship status grouping
4. Race - 5 categories with ethnic/majority-minority grouping

Each hierarchy follows the principle of semantic preservation while
providing increasing levels of generalization for privacy protection.
"""

from .age_hierarchy import AgeHierarchy
from .education_hierarchy import EducationHierarchy
from .marital_status_hierarchy import MaritalStatusHierarchy
from .race_hierarchy import RaceHierarchy

__all__ = [
    'AgeHierarchy',
    'EducationHierarchy', 
    'MaritalStatusHierarchy',
    'RaceHierarchy',
    'HierarchyManager'
]

class HierarchyManager:
    """
    Central manager for all generalization hierarchies
    Provides unified interface for k-anonymity algorithm
    """
    
    def __init__(self):
        self.hierarchies = {
            'age': AgeHierarchy(),
            'education': EducationHierarchy(),
            'marital-status': MaritalStatusHierarchy(),
            'race': RaceHierarchy()
        }
        
        self.qi_attributes = list(self.hierarchies.keys())
    
    def generalize_value(self, attribute, value, level):
        """
        Generalize a single attribute value to specified level
        
        Args:
            attribute (str): Quasi-identifier name
            value: Original attribute value
            level (int): Target generalization level
            
        Returns:
            Generalized value
        """
        if attribute not in self.hierarchies:
            raise ValueError(f"Unknown attribute: {attribute}")
            
        return self.hierarchies[attribute].generalize(value, level)
    
    def get_generalization_loss(self, attribute, value, level):
        """
        Calculate information loss for generalizing attribute to level
        
        Returns:
            float: Information loss (0.0-1.0)
        """
        if attribute not in self.hierarchies:
            raise ValueError(f"Unknown attribute: {attribute}")
            
        return self.hierarchies[attribute].get_generalization_loss(value, level)
    
    def get_max_level(self, attribute):
        """Get maximum generalization level for attribute"""
        if attribute not in self.hierarchies:
            raise ValueError(f"Unknown attribute: {attribute}")
            
        return self.hierarchies[attribute].max_level
    
    def get_all_hierarchy_info(self):
        """
        Get complete hierarchy information for documentation
        
        Returns:
            dict: Hierarchy levels for all attributes
        """
        info = {}
        for attr, hierarchy in self.hierarchies.items():
            info[attr] = {
                'max_level': hierarchy.max_level,
                'levels': hierarchy.get_hierarchy_levels()
            }
        return info
