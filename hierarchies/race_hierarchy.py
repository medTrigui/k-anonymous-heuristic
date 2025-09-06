"""
Race Generalization Hierarchy

Based on data analysis:
- 5 unique race categories
- Distribution: White (27,816), Black (3,124), Asian-Pac-Islander (1,039), 
  Amer-Indian-Eskimo (311), Other (271)
- Sensitive attribute requiring careful generalization

Hierarchy Design Principles:
1. Respect demographic/cultural significance
2. Handle majority vs minority distinctions appropriately  
3. Maintain statistical utility while protecting privacy
4. Consider US Census categorizations
"""

class RaceHierarchy:
    def __init__(self):
        self.max_level = 3  # Shorter hierarchy due to sensitivity and fewer categories
        
    def get_hierarchy_levels(self):
        """Returns the complete race hierarchy definition"""
        return {
            0: "specific",               # Original 5 categories
            1: "ethnic_group",           # 3 categories: White, Asian, Other-Minority
            2: "majority_minority",      # 2 categories: White, Non-White
            3: "suppressed"              # * (completely suppressed)
        }
    
    def generalize(self, race, target_level):
        """
        Generalizes a race value to the specified hierarchy level
        
        Args:
            race (str): Original race value
            target_level (int): Target generalization level (0-3)
            
        Returns:
            str: Generalized race representation
        """
        if target_level == 0:
            return race
        
        elif target_level == 1:
            # Ethnic group classification (3 categories)
            if race == "White":
                return "White"
            elif race == "Asian-Pac-Islander":
                return "Asian"
            elif race in ["Black", "Amer-Indian-Eskimo", "Other"]:
                return "Other-Minority"
            else:
                return "Other-Minority"  # Default fallback
        
        elif target_level == 2:
            # Majority vs minority classification (2 categories)
            if race == "White":
                return "White"
            else:  # All non-White categories
                return "Non-White"
        
        elif target_level == 3:
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
            return 0.4   # Ethnic groups (5->3 categories)
        elif target_level == 2:
            return 0.7   # Majority/minority (5->2 categories)
        elif target_level == 3:
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
        elif generalized_value in ["White", "Non-White"]:
            if generalized_value == "White":
                return 1  # Just White
            else:  # Non-White
                return 4  # Black, Asian-Pac-Islander, Amer-Indian-Eskimo, Other
        elif generalized_value in ["White", "Asian", "Other-Minority"]:
            if generalized_value == "White":
                return 1  # White
            elif generalized_value == "Asian":
                return 1  # Asian-Pac-Islander
            else:  # Other-Minority
                return 3  # Black, Amer-Indian-Eskimo, Other
        else:
            return 1  # Specific category
