"""
Race Generalization Hierarchy

Based on data analysis:
- 5 unique race categories
- Distribution: White (27,816), Black (3,124), Asian-Pac-Islander (1,039), 
  Amer-Indian-Eskimo (311), Other (271)
- Highly sensitive attribute requiring ethical generalization

Hierarchy Design Principles:
1. Avoid any potentially biased or discriminatory groupings
2. Immediate generalization to "Person" to eliminate racial distinctions
3. Prioritize privacy and ethical considerations over statistical utility
4. Recognize that any intermediate racial grouping risks perpetuating bias
"""

class RaceHierarchy:
    def __init__(self):
        self.max_level = 2  # Simplified hierarchy due to ethical concerns
        
    def get_hierarchy_levels(self):
        """Returns the complete race hierarchy definition"""
        return {
            0: "specific",               # Original 5 categories
            1: "person",                 # Single category: Person
            2: "suppressed"              # * (completely suppressed)
        }
    
    def generalize(self, race, target_level):
        """
        Generalizes a race value to the specified hierarchy level
        
        Args:
            race (str): Original race value
            target_level (int): Target generalization level (0-2)
            
        Returns:
            str: Generalized race representation
        """
        if target_level == 0:
            return race
        
        elif target_level == 1:
            # All races generalized to "Person" to avoid bias
            return "Person"
        
        elif target_level == 2:
            return "*"  # Completely suppressed
        
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_generalization_loss(self, race, target_level):
        """
        Calculate information loss for generalizing race to target level
        
        Returns:
            float: Information loss (0.0 = no loss, 1.0 = complete loss)
        """
        if target_level == 0:
            return 0.0
        elif target_level == 1:
            return 0.8   # All races -> Person (significant loss but ethically necessary)
        elif target_level == 2:
            return 1.0   # Suppressed
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_category_size(self, generalized_value):
        """
        Get the number of original categories represented by generalized value
        Used for precision calculations
        """
        if generalized_value == "*":
            return 5  # All categories
        elif generalized_value == "Person":
            return 5  # All 5 original categories represented
        else:
            return 1  # Specific category
