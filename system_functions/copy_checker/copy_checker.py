
import json
import os
import time


from system_functions.copy_checker.code_normalization import *
from system_functions.copy_checker.fuzzy_match import FuzzyMatch
from system_functions.copy_checker.visual_html import *

def number_of_text(lines):
    ct = 0
    for i in range(0, len(lines)):
        for j in range(0, len(lines[i])):
            if lines[i][j] not in [' ', '\t']:
                ct = ct + 1
    return ct

def remove_all_space(_list=[[]]):
    """
    input:
        - a 2D list of string 
    output:
        - 2D list of string but all space removed 
    """
    for i in range(0, len(_list)):
        t = _list[i].strip().split()
        t = "".join(t)
        _list[i] = t 
    return _list 

def merge_map(primary_map={}, secondary_map={}):
    """
    # primary_map is the main setblueprint 
    # secondary_map is another blueprint that would be embedded into primary map 
    """
    for key in secondary_map: # line number 
        if primary_map.get(key) is None:
            primary_map[key] = {}
        for key2 in secondary_map[key]: # character number 
            primary_map[key][key2] = secondary_map[key][key2]
    return primary_map 

def matching(alpha=0.7, json_codes={}, space_removed=True, level_threshold=0):
    """
    input:
        - alpha: ratio of weighted matric 
        - json_codes, a json_file 
        - space_removed: True/False, processed or not 
        - level_threshold: How much granularity is used during n x n LCS processing 
    output:
        - json_codes, a n x n json, output for each cell 
    """
    keys = list(json_codes.keys())
    # initialization
    for i in range(0, len(keys)):
        json_codes[i]['match_status'] = []  
        for j in range(0, len(keys)):
            json_codes[i]['match_status'].append([0, None, None, ""]) # Total score, matched entries in normalized code, matched entries in main code, color coded html
    # removing all the space
    if space_removed is True: 
        pass 
        # not going yo press any space related issues here
        """
        for i in range(0, len(keys)):
            json_codes[keys[i]]['code_simplified'] = remove_all_space(_list=json_codes[keys[i]]['code_simplified'])
            json_codes[keys[i]]['code_simplified_var_nor'] = remove_all_space(_list=json_codes[keys[i]]['code_simplified_var_nor'])
        """
        
    f_m = FuzzyMatch() # Fuzzy matcher 
    
    for i in range(0, len(keys)):
         code_simplified1 = json_codes[i]['code_simplified']
         code_simplified_var_nor1 = json_codes[i]['code_simplified_var_nor']
         map_char_dict_real_norm1 = json_codes[i]['map_char_dict_real_norm'] # map 
         for j in range(i+1, len(keys)):
            code_simplified2 = json_codes[j]['code_simplified']
            code_simplified_var_nor2 = json_codes[j]['code_simplified_var_nor']
            map_char_dict_real_norm2 = json_codes[j]['map_char_dict_real_norm'] # map2
            # process function
            print(f"started matching {keys[i]} {keys[j]}")
            # coding syntax matching 
            similarity, all_match_fragments, setblueprint1, setblueprint2, id_off = f_m.process(norm_lines1=code_simplified1, var_norm_lines1=code_simplified_var_nor1, norm_lines2=code_simplified2, var_norm_lines2=code_simplified_var_nor2, 
                        alpha=alpha, level_threshold=level_threshold, map_dict1=map_char_dict_real_norm1, map_dict2=map_char_dict_real_norm2)
            
            print("similarity ", similarity)
            print("all match fragments ", all_match_fragments)
            # comments matching - block comments 
            _,_,t_setblueprint1, t_setblueprint2,id_off = f_m.process(norm_lines1=json_codes[i]['block_comments'], var_norm_lines1=None, norm_lines2=json_codes[j]['block_comments'], var_norm_lines2=None, 
                        alpha=alpha, level_threshold=level_threshold, map_dict1=json_codes[i]['map_block_com'], map_dict2=json_codes[j]['map_block_com'], 
                        created_id_offset=id_off+2, char_match_style="exact")
            setblueprint1 = merge_map(primary_map=setblueprint1, secondary_map=t_setblueprint1)
            setblueprint2 = merge_map(primary_map=setblueprint2, secondary_map=t_setblueprint2)
            # comments matching - single line 
            _,_,t_setblueprint1, t_setblueprint2, id_off = f_m.process(norm_lines1=json_codes[i]['single_line_comments'], var_norm_lines1=None, norm_lines2=json_codes[j]['single_line_comments'], var_norm_lines2=None, 
                        alpha=alpha, level_threshold=level_threshold, map_dict1=json_codes[i]['map_single_com'], map_dict2=json_codes[j]['map_single_com'], 
                        created_id_offset=id_off+2, char_match_style="exact")
            setblueprint1 = merge_map(primary_map=setblueprint1, secondary_map=t_setblueprint1)
            setblueprint2 = merge_map(primary_map=setblueprint2, secondary_map=t_setblueprint2)
            
            json_codes[i]['match_status'][j][0] = similarity 
            json_codes[i]['match_status'][j][1] = all_match_fragments
            json_codes[i]['match_status'][j][2] = setblueprint1
            json_codes[i]['match_status'][j][3] = show_matched_code_with_col(source_code=json_codes[i]['raw_source_code'], setblueprint=setblueprint1)
            
            json_codes[j]['match_status'][i][0] = similarity # similarity score 
            json_codes[j]['match_status'][i][1] = all_match_fragments
            json_codes[j]['match_status'][i][2] = setblueprint2
            json_codes[j]['match_status'][i][3] = show_matched_code_with_col(source_code=json_codes[j]['raw_source_code'], setblueprint=setblueprint2)
    return json_codes

def source_code_mapped_array(raw_code=[], setblueprint={}):
    data = []
    for i in range(0, len(raw_code)):
        for j in range(0, len(raw_code[i])):
            class_label = -1 # no label has been found
            if setblueprint.get(i) is not None and setblueprint[i].get(j) is not None:
                class_label = setblueprint[i].get(j) 
            data.append([raw_code[i][j], class_label]) # word and label
    return data 

def prepare_json_array_to_send(json_codes={}, path_of_files=[]):
    msg_json = []
    keys = list(json_codes.keys())
    for i in range(0, len(keys)):
        msg_json.append([]) # a list created for ith entry 
        for j in range(0, len(keys)):
            similarity = 0.0 
            code_1 = []
            code_2 = []
            msg_json[i].append([similarity, code_1, code_2]) 
    for i in range(0, len(keys)):
        print(f"matching {i}th : {keys[i]}")
        ent_i = keys[i]
        msg_json[ent_i][ent_i][0] = similarity
        #msg_json[ent_i][ent_i][1] = source_code_mapped_array(raw_code=json_codes[ent_i]['raw_source_code'], setblueprint=json_codes[ent_i]['match_status'][ent_i][2]) 
        #msg_json[ent_i][ent_i][2] = source_code_mapped_array(raw_code=json_codes[ent_i]['raw_source_code'], setblueprint=json_codes[ent_i]['match_status'][ent_i][2]) 
        for j in range(i+1, len(keys)):
            ent_j = keys[j]
            similarity = json_codes[ent_i]['match_status'][ent_j][0] 
            code_1 = source_code_mapped_array(raw_code=json_codes[ent_i]['raw_source_code'], setblueprint=json_codes[ent_i]['match_status'][ent_j][2]) 
            code_2 = source_code_mapped_array(raw_code=json_codes[ent_j]['raw_source_code'], setblueprint=json_codes[ent_j]['match_status'][ent_i][2])
            msg_json[ent_i][ent_j][0] = similarity
            msg_json[ent_i][ent_j][1] = code_1
            msg_json[ent_i][ent_j][2] = code_2

            msg_json[ent_j][ent_i][0] = similarity
            msg_json[ent_j][ent_i][1] = code_2
            msg_json[ent_j][ent_i][2] = code_1 
    return msg_json

    
def start_copy_checking(path_of_files=[], alpha=0.7, level_threshold=0):
    """
    input
        - path_of_files as a list 
        - alpha: for weighted metric 
        - level_threshold: 0 (simple), 1 (30% similarity matching), 2 (60% similarity matching), 3 (90% similarity matching)
    output
        - json object as scores, as a 2D type json {0: {0: score, 1: score, 2: value, 3: value, ...}, 1:{0: score, 1: score, 2: score}} 
        - A 2d array output i th row , jth entry [similarity, code 1 labeled, code 2 labeled]
    """
    json_codes = {}
    for i in range(0, len(path_of_files)):
        json_codes[i] = {}
        json_codes[i]['code_simplified'] = []
        json_codes[i]['code_simplified_var_nor'] = []
        json_codes[i]['map_char_dict_real_norm'] = None 
        json_codes[i]['block_comments'] = []
        json_codes[i]['single_line_comments'] = []
        json_codes[i]['map_block_com'] = None 
        json_codes[i]['map_single_com'] = None 
        if os.path.exists(path_of_files[i]):
            json_codes[i]['code_simplified'], json_codes[i]['code_simplified_var_nor'], json_codes[i]['map_char_dict_real_norm'], json_codes[i]['block_comments'], json_codes[i]['single_line_comments'], json_codes[i]['map_block_com'], json_codes[i]['map_single_com'] = normalize(code_file=path_of_files[i])
            json_codes[i]['raw_source_code'] = read_exact_lines(code_file=path_of_files[i])
    print("initiating")
    start_time = time.process_time()
    json_codes = matching(alpha=alpha, json_codes=json_codes, space_removed=True, level_threshold=level_threshold)
    end_time = time.process_time()
    print("completed, processing time : ", end_time-start_time)
    # print("json_codes ", json_codes)
    return prepare_json_array_to_send(json_codes=json_codes)
    # return json_codes
    
# 31.296875 for 30%
# 15 - 60%
# 3 - 90% 