"""
Age Generalization Hierarchy

Based on data analysis:
- Age range: 17-90 years  
- Mean: 38.6, Median: 37
- 25th percentile: 28, 75th percentile: 48

Hierarchy Design Principles:
1. Preserve meaningful life stages
2. Maintain balanced distribution across levels
3. Consider career/demographic significance
"""

class AgeHierarchy:
    def __init__(self):
        self.max_level = 4
        
    def get_hierarchy_levels(self):
        """Returns the complete age hierarchy definition"""
        return {
            0: "specific_age",           # Original values: 17, 18, 19, ..., 90
            1: "five_year_ranges",       # [17-22), [22-27), [27-32), etc.
            2: "ten_year_ranges",        # [17-27), [27-37), [37-47), etc. 
            3: "life_stages",            # Young[17-30), Adult[30-55), Senior[55+)
            4: "suppressed"              # * (completely suppressed)
        }
    
    def generalize(self, age, target_level):
        """
        Generalizes an age value to the specified hierarchy level
        
        Args:
            age (int): Original age value
            target_level (int): Target generalization level (0-4)
            
        Returns:
            str: Generalized age representation
        """
        if target_level == 0:
            return str(age)
        
        elif target_level == 1:
            # 5-year ranges aligned with meaningful boundaries
            if age < 22:
                return "[17-22)"
            elif age < 27:
                return "[22-27)"
            elif age < 32:
                return "[27-32)"
            elif age < 37:
                return "[32-37)"
            elif age < 42:
                return "[37-42)"
            elif age < 47:
                return "[42-47)"
            elif age < 52:
                return "[47-52)"
            elif age < 57:
                return "[52-57)"
            elif age < 62:
                return "[57-62)"
            elif age < 67:
                return "[62-67)"
            elif age < 72:
                return "[67-72)"
            else:
                return "[72+)"
        
        elif target_level == 2:
            # 10-year ranges for broader categorization
            if age < 27:
                return "[17-27)"
            elif age < 37:
                return "[27-37)"
            elif age < 47:
                return "[37-47)"
            elif age < 57:
                return "[47-57)"
            elif age < 67:
                return "[57-67)"
            else:
                return "[67+)"
        
        elif target_level == 3:
            # Life stages based on career/demographic patterns
            if age < 30:
                return "Young"      # Early career, education
            elif age < 55:
                return "Adult"      # Prime working years
            else:
                return "Senior"     # Pre-retirement/retirement
        
        elif target_level == 4:
            return "*"  # Completely suppressed
        
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_generalization_loss(self, age, target_level):
        """
        Calculate information loss for generalizing age to target level
        
        Returns:
            float: Information loss (0.0 = no loss, 1.0 = complete loss)
        """
        if target_level == 0:
            return 0.0
        elif target_level == 1:
            return 0.2  # 5-year range
        elif target_level == 2:
            return 0.4  # 10-year range  
        elif target_level == 3:
            return 0.7  # Life stage
        elif target_level == 4:
            return 1.0  # Suppressed
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")

    def get_range_size(self, generalized_value):
        """
        Get the size of the range for a generalized age value
        Used for precision calculations
        """
        if generalized_value == "*":
            return 74  # Full age range (90-17+1)
        elif generalized_value == "Young":
            return 13  # 30-17
        elif generalized_value == "Adult":
            return 25  # 55-30
        elif generalized_value == "Senior":
            return 36  # 90-55+1
        elif generalized_value.startswith("[") and ")" in generalized_value:
            # Parse range like "[27-37)"
            if "+" in generalized_value:
                return 19  # For ranges like "[72+)" - approximate
            else:
                parts = generalized_value.strip("[]()").split("-")
                return int(parts[1]) - int(parts[0])
        else:
            return 1  # Specific age
