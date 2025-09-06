"""
Marital Status Generalization Hierarchy

Based on data analysis:
- 7 unique marital status categories
- Distribution: Married-civ-spouse (14,976), Never-married (10,683), Divorced (4,443)
- Natural grouping by relationship/partnership status

Hierarchy Design Principles:
1. Group by partnership status and history
2. Preserve meaningful relationship categorizations
3. Consider social/demographic significance
"""

class MaritalStatusHierarchy:
    def __init__(self):
        self.max_level = 3  # Shorter hierarchy due to fewer categories
        
    def get_hierarchy_levels(self):
        """Returns the complete marital status hierarchy definition"""
        return {
            0: "specific",               # Original 7 categories
            1: "relationship_status",    # 3 categories: Married, Single, Previously-Married
            2: "partnership_status",     # 2 categories: Partnered, Not-Partnered  
            3: "suppressed"              # * (completely suppressed)
        }
    
    def generalize(self, marital_status, target_level):
        """
        Generalizes a marital status value to the specified hierarchy level
        
        Args:
            marital_status (str): Original marital status value
            target_level (int): Target generalization level (0-3)
            
        Returns:
            str: Generalized marital status representation
        """
        if target_level == 0:
            return marital_status
        
        elif target_level == 1:
            # Relationship status grouping (3 categories)
            if marital_status in ["Married-civ-spouse", "Married-spouse-absent", "Married-AF-spouse"]:
                return "Married"
            elif marital_status == "Never-married":
                return "Single"
            elif marital_status in ["Divorced", "Separated", "Widowed"]:
                return "Previously-Married"
            else:
                return "Single"  # Default fallback
        
        elif target_level == 2:
            # Partnership status (2 categories)
            level_1 = self.generalize(marital_status, 1)
            
            if level_1 == "Married":
                return "Partnered"
            else:  # Single, Previously-Married
                return "Not-Partnered"
        
        elif target_level == 3:
            return "*"  # Completely suppressed
        
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_generalization_loss(self, marital_status, target_level):
        """
        Calculate information loss for generalizing marital status to target level
        
        Returns:
            float: Information loss (0.0 = no loss, 1.0 = complete loss)
        """
        if target_level == 0:
            return 0.0
        elif target_level == 1:
            return 0.3   # Relationship status (7->3 categories)
        elif target_level == 2:
            return 0.6   # Partnership status (7->2 categories)
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
            return 7  # All categories
        elif generalized_value in ["Partnered", "Not-Partnered"]:
            if generalized_value == "Partnered":
                return 3  # All married variants
            else:  # Not-Partnered
                return 4  # Never-married + previously married (3)
        elif generalized_value in ["Married", "Single", "Previously-Married"]:
            if generalized_value == "Married":
                return 3  # Married-civ-spouse, Married-spouse-absent, Married-AF-spouse
            elif generalized_value == "Single":
                return 1  # Never-married
            else:  # Previously-Married
                return 3  # Divorced, Separated, Widowed
        else:
            return 1  # Specific category
