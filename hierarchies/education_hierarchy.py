"""
Education Generalization Hierarchy

Based on data analysis:
- 16 unique education levels from Preschool to Doctorate
- Top categories: HS-grad (10,501), Some-college (7,291), Bachelors (5,355)
- Education follows natural progression/grouping by attainment level

Hierarchy Design Principles:
1. Group by education attainment level
2. Preserve semantic meaning (K-12, College, Graduate)
3. Balance privacy vs utility
"""

class EducationHierarchy:
    def __init__(self):
        self.max_level = 4
        
        # Define the original education categories and their logical groupings
        self.education_mapping = {
            # K-12 Education
            "Preschool": "Elementary",
            "1st-4th": "Elementary", 
            "5th-6th": "Elementary",
            "7th-8th": "Middle",
            "9th": "Middle",
            "10th": "High-School",
            "11th": "High-School", 
            "12th": "High-School",
            "HS-grad": "High-School",
            
            # Post-Secondary Education  
            "Some-college": "Some-College",
            "Assoc-voc": "Associate",
            "Assoc-acdm": "Associate", 
            "Bachelors": "Bachelors",
            "Masters": "Graduate",
            "Prof-school": "Graduate",
            "Doctorate": "Graduate"
        }
        
    def get_hierarchy_levels(self):
        """Returns the complete education hierarchy definition"""
        return {
            0: "specific",               # Original 16 categories
            1: "detailed_level",         # 8 levels: Elementary, Middle, High-School, Some-College, Associate, Bachelors, Graduate
            2: "education_level",        # 4 levels: K12, Some-College, College-Degree, Graduate-Degree  
            3: "broad_category",         # 2 levels: No-Degree, Degree
            4: "suppressed"              # * (completely suppressed)
        }
    
    def generalize(self, education, target_level):
        """
        Generalizes an education value to the specified hierarchy level
        
        Args:
            education (str): Original education value
            target_level (int): Target generalization level (0-4)
            
        Returns:
            str: Generalized education representation
        """
        if target_level == 0:
            return education
        
        elif target_level == 1:
            # Detailed education levels (8 categories)
            return self.education_mapping.get(education, education)
        
        elif target_level == 2:
            # Education level grouping (4 categories)
            level_1 = self.education_mapping.get(education, education)
            
            if level_1 in ["Elementary", "Middle", "High-School"]:
                return "K12"
            elif level_1 == "Some-College":
                return "Some-College"
            elif level_1 in ["Associate", "Bachelors"]:
                return "College-Degree"
            elif level_1 == "Graduate":
                return "Graduate-Degree"
            else:
                return "K12"  # Default fallback
        
        elif target_level == 3:
            # Broad categorization (2 categories)
            level_2 = self.generalize(education, 2)
            
            if level_2 in ["K12", "Some-College"]:
                return "No-Degree"
            else:  # College-Degree, Graduate-Degree
                return "Degree"
        
        elif target_level == 4:
            return "*"  # Completely suppressed
        
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_generalization_loss(self, education, target_level):
        """
        Calculate information loss for generalizing education to target level
        
        Returns:
            float: Information loss (0.0 = no loss, 1.0 = complete loss)
        """
        if target_level == 0:
            return 0.0
        elif target_level == 1:
            return 0.15  # Detailed levels (16->8 categories)
        elif target_level == 2:
            return 0.35  # Education levels (16->4 categories)
        elif target_level == 3:
            return 0.65  # Broad categories (16->2 categories)
        elif target_level == 4:
            return 1.0   # Suppressed
        else:
            raise ValueError(f"Invalid hierarchy level: {target_level}")
    
    def get_category_size(self, generalized_value):
        """
        Get the number of original categories represented by generalized value
        Used for precision calculations
        """
        if generalized_value == "*":
            return 16  # All categories
        elif generalized_value in ["No-Degree", "Degree"]:
            return 8   # Half of categories each
        elif generalized_value == "K12":
            return 9   # Preschool through HS-grad
        elif generalized_value in ["Some-College", "College-Degree", "Graduate-Degree"]:
            if generalized_value == "Some-College":
                return 1
            elif generalized_value == "College-Degree": 
                return 3  # Assoc-voc, Assoc-acdm, Bachelors
            else:  # Graduate-Degree
                return 3  # Masters, Prof-school, Doctorate
        elif generalized_value in ["Elementary", "Middle", "High-School", "Associate", "Bachelors", "Graduate"]:
            # Count original categories in each detailed level
            counts = {
                "Elementary": 3,    # Preschool, 1st-4th, 5th-6th
                "Middle": 2,        # 7th-8th, 9th  
                "High-School": 4,   # 10th, 11th, 12th, HS-grad
                "Some-College": 1,  # Some-college
                "Associate": 2,     # Assoc-voc, Assoc-acdm
                "Bachelors": 1,     # Bachelors
                "Graduate": 3       # Masters, Prof-school, Doctorate
            }
            return counts.get(generalized_value, 1)
        else:
            return 1  # Specific category
