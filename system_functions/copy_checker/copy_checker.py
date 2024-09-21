
import json
import os
import time
import threading



from system_functions.copy_checker.code_normalization import *
from system_functions.copy_checker.fuzzy_match import FuzzyMatch
from system_functions.copy_checker.visual_html import *


def entity_process(i, j, json_codes, alpha=0.5, level_threshold=3, process_result=[]):
    # used for threading here
    f_m = FuzzyMatch()  # Fuzzy matcher
    # coding syntax matching
    similarity, all_match_fragments, setblueprint1, setblueprint2, id_off = f_m.process(norm_lines1=json_codes[i]['code_simplified'],
                                                                                        var_norm_lines1=json_codes[i]['code_simplified_var_nor'],
                                                                                        norm_lines2=json_codes[j]['code_simplified'],
                                                                                        var_norm_lines2=json_codes[j]['code_simplified_var_nor'],
                                                                                        alpha=alpha,
                                                                                        level_threshold=level_threshold,
                                                                                        map_dict1=json_codes[i]['map_char_dict_real_norm'],
                                                                                        map_dict2=json_codes[j]['map_char_dict_real_norm'], char_match_style="exact")
    print("similarity ", similarity)
    print("all match fragments ", all_match_fragments)
    # comments matching - block comments
    _, _, t_setblueprint1, t_setblueprint2, id_off = f_m.process(norm_lines1=json_codes[i]['block_comments'],
                                                                 var_norm_lines1=None,
                                                                 norm_lines2=json_codes[j]['block_comments'],
                                                                 var_norm_lines2=None,
                                                                 alpha=alpha, level_threshold=level_threshold,
                                                                 map_dict1=json_codes[i]['map_block_com'],
                                                                 map_dict2=json_codes[j]['map_block_com'],
                                                                 created_id_offset=id_off + 2, char_match_style="exact")
    setblueprint1 = merge_map(primary_map=setblueprint1, secondary_map=t_setblueprint1)
    setblueprint2 = merge_map(primary_map=setblueprint2, secondary_map=t_setblueprint2)
    # comments matching - single line
    _, _, t_setblueprint1, t_setblueprint2, id_off = f_m.process(norm_lines1=json_codes[i]['single_line_comments'],
                                                                 var_norm_lines1=None,
                                                                 norm_lines2=json_codes[j]['single_line_comments'],
                                                                 var_norm_lines2=None,
                                                                 alpha=alpha, level_threshold=level_threshold,
                                                                 map_dict1=json_codes[i]['map_single_com'],
                                                                 map_dict2=json_codes[j]['map_single_com'],
                                                                 created_id_offset=id_off + 2, char_match_style="exact")
    setblueprint1 = merge_map(primary_map=setblueprint1, secondary_map=t_setblueprint1)
    setblueprint2 = merge_map(primary_map=setblueprint2, secondary_map=t_setblueprint2)
    # 0:i, 1:j,
    process_result.append(i)
    process_result.append(j)
    process_result.append(similarity) # 2
    process_result.append(all_match_fragments) # 3
    process_result.append(setblueprint1) # 4
    process_result.append(setblueprint2) # 5
    return

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

def matching(alpha=0.7, json_codes={}, space_removed=True, level_threshold=0, num_threads=1):
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
    stored_threads = []

    for i in range(0, num_threads):
        stored_threads.append([None, None])
    for i in range(0, len(keys)):
         j = i + 1
         while j < len(keys):
             print("############### ", i, j, len(stored_threads), num_threads)
             print("Threads = ", stored_threads)
             for k in range(0, len(stored_threads)):  # checkness of free ind
                 if stored_threads[k][0] is not None and stored_threads[k][0].is_alive() is False:  # not an alive thread
                     # store old thread's data
                     x, y = stored_threads[k][1][0], stored_threads[k][1][1]
                     json_codes[x]['match_status'][y][0] = stored_threads[k][1][2]
                     json_codes[x]['match_status'][y][1] = stored_threads[k][1][3]
                     json_codes[x]['match_status'][y][2] = stored_threads[k][1][4]
                     json_codes[x]['match_status'][y][3] = show_matched_code_with_col(
                         source_code=json_codes[x]['raw_source_code'], setblueprint=stored_threads[k][1][4])

                     json_codes[y]['match_status'][x][0] = stored_threads[k][1][2]
                     json_codes[y]['match_status'][x][1] = stored_threads[k][1][3]
                     json_codes[y]['match_status'][x][2] = stored_threads[k][1][5]
                     json_codes[y]['match_status'][x][3] = show_matched_code_with_col(
                         source_code=json_codes[y]['raw_source_code'], setblueprint=stored_threads[k][1][5])
                     print("ended ******* ", x, y)
                     stored_threads[k][0], stored_threads[k][1] = None, None
             for k in range(0, len(stored_threads)):  # checkness of free ind
                 if stored_threads[k][0] is None:
                     process_result = []
                     args = (i, j, json_codes, alpha, level_threshold, process_result)
                     thread = threading.Thread(target=entity_process, args=args)
                     stored_threads[k][0] = thread
                     stored_threads[k][1] = process_result
                     thread.start()
                     print("started ", i, j)
                     j += 1  # new object to check within
                     break
    while True:
        free = 0
        for k in range(0, len(stored_threads)):
            if stored_threads[k][0] is None:
                free += 1
            elif stored_threads[k][0].is_alive() is False:
                x, y = stored_threads[k][1][0], stored_threads[k][1][1]
                json_codes[x]['match_status'][y][0] = stored_threads[k][1][2]
                json_codes[x]['match_status'][y][1] = stored_threads[k][1][3]
                json_codes[x]['match_status'][y][2] = stored_threads[k][1][4]
                json_codes[x]['match_status'][y][3] = show_matched_code_with_col(
                    source_code=json_codes[x]['raw_source_code'], setblueprint=stored_threads[k][1][4])

                json_codes[y]['match_status'][x][0] = stored_threads[k][1][2]
                json_codes[y]['match_status'][x][1] = stored_threads[k][1][3]
                json_codes[y]['match_status'][x][2] = stored_threads[k][1][5]
                json_codes[y]['match_status'][x][3] = show_matched_code_with_col(
                    source_code=json_codes[y]['raw_source_code'], setblueprint=stored_threads[k][1][5])
                print("ended ******* ", x, y)
                stored_threads[k][0], stored_threads[k][1] = None, None
                free += 1
        if free == len(stored_threads):
            break
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

    
def start_copy_checking(path_of_files=[], alpha=0.7, level_threshold=0, num_threads=1):
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
    json_codes = matching(alpha=alpha, json_codes=json_codes, space_removed=True, level_threshold=level_threshold, num_threads=num_threads)
    end_time = time.process_time()
    print("completed, processing time : ", end_time-start_time) 
    # print("json_codes ", json_codes)
    return prepare_json_array_to_send(json_codes=json_codes)
    # return json_codes
    
# 31.296875 for 30%
# 15 - 60%
# 3 - 90% 