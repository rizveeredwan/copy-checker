import os
from copy_checker.calculate_similarity import CalculateSimilarity

obj1 = CalculateSimilarity()
obj1.execute_matching(threshold=0.8, alpha=0.7,  # Thresholds
                      A=os.path.join('.', 'mini_max1.cpp'),  # Program File A
                      B=os.path.join('.', 'mini_max2.cpp'),  # Program File B
                      print_flag=True)  # Flag to print the matched lines in order
