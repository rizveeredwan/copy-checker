# File to write the sanity check functions
import os

from system_functions.copy_checker.code_normalization import *

code_lines, var_replaced_code_lines, map_dict, block_comments, single_line_comments, map_dict_block_com, map_dict_single_com = normalize(os.path.join('.', 'system_functions', 'copy_checker', 'examples', 'temp.py'))
print(code_lines)
print(var_replaced_code_lines)
print(map_dict)
print(block_comments)
print(single_line_comments)
print(map_dict_block_com)
print(map_dict_single_com)