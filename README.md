# CopyChecker
This is the python implementation of the published paper *"A Robust Objective Focused Algorithm to Detect Source Code Plagiarism"* published at IEEE Annual Ubiquitous Computing, Electronics & Mobile Communication Conference (UEMCON) 2022. If you use this paper or this repository please cite this work as reference.

---

## Basic Usage, 
```
import os
from copy_checker.copy_checker import CopyChecker

obj1 = CopyChecker()
obj1.execute_single_matching(threshold=0.8, alpha=0.7, # Thresholds
                             A=os.path.join('.', 'mini_max1.cpp'), # Program File A
                             B=os.path.join('.', 'mini_max2.cpp'), # Program File B
                             print_flag=True) # Flag to print the matched lines in order
                             
```
`print_flag` - Prints the matched lines when the programs are detected as suspicious, both for variable normalized and non normalized forms. Two text files are generated in the home directory.

`A`, `B` - File paths 

`threshold`, `alpha` - Empirically set parameters to control the similarity metric as stated in the published paper.

---




