# File to write the sanity check functions
import os

from system_functions.copy_checker.code_normalization import *
from system_functions.database_connectivity import *

"""
code_lines, var_replaced_code_lines, map_dict, block_comments, single_line_comments, map_dict_block_com, map_dict_single_com = normalize(os.path.join('.', 'system_functions', 'copy_checker', 'examples', 'temp.py'))
print(code_lines)
print(var_replaced_code_lines)
print(map_dict)
print(block_comments)
print(single_line_comments)
print(map_dict_block_com)
print(map_dict_single_com)
"""

dc = DatabaseConnectivity(database_name='copy_code_db')

res = dc.create_entry_for_new_zip_submission(db_name="copy_code_db", collection="copy_code_colc",
                                             zip_file_path=os.path.join('.', 'dummy_data.zip'), alpha=0.5,
                                             level_threshold=3, process_status=0,
                                             email_sent=False, submission_time=str(datetime.now()),
                                             completion_time=None, json_data={})
print("what ", res)

"""
dc.update_entry(primary_key='66e1b88b83e25948667e8783', db_name="copy_code_db", collection="copy_code_colc", alpha=0.2, file_path="", level_threshold=3, process_status=1,
                                            email_sent=False, submission_time=None, completion_time=str(datetime.now()), json_data={})
"""
