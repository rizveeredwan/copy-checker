# CopyChecker
This is the python implementation of the published paper *"A Robust Objective Focused Algorithm to Detect Source Code Plagiarism"* published at IEEE Annual Ubiquitous Computing, Electronics & Mobile Communication Conference (UEMCON) 2022. If you use this paper or this repository please cite this work as reference.

---
# News

---

```commandline
16/07/2024 - This algorithm has been modified on (July 16, 2024). Currently, this repository contains a more updated and sophisticated version of the implementation.
```

## Requirements
```
python 3.x
```

## Basic Usage
```
-- see interactive_checker.py for a complete usage 
-- update BASE_DIRECTORY and TRACKER_FILE variable 
-- Run command for windows: python3 interactive_checker.py -ot 0 -b dummy_data_8 -a 0.7 -l 3 -of output_8.csv -f file_status_tracker_8.csv
```
`print_flag` - Prints the matched lines when the programs are detected as suspicious, both for variable normalized and non normalized forms. Two text files are generated in the home directory.

---
