import operator
import os
import re
import csv
import sys
from system_functions.copy_checker.match_source_with_norm import *


def read_csv_file(file_name, lang="java"):
        # reading from csv file 
        print("language ", lang, file_name)
        _list = []
        placement_position = {}
        with open(file_name, 'r') as f:
            csv_lines = csv.DictReader(f)
            for row in csv_lines:
                if row[lang] == "1":
                    _list.append(row['id']) 
                    placement_position[row['id']] = row['type']       
        return _list, placement_position

def read_code_file(code_file = ""):
    # reading the code file, all spaces from before and after are stripped 
    with open(code_file, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            lines[i] = lines[i].strip()
    return lines

def read_exact_lines(code_file=""):
    with open(code_file, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            # lines[i] = lines[i].rstrip('\n') # only new lines are removed from the end of each line 
            #lines[i] = lines[i] 
            # print(lines[i])
            pass 
    return lines

def write_code_file(code_lines, file_name):
    f = open(file_name, 'w')
    for i in range(0, len(code_lines)):
        f.write(code_lines[i]+'\n')
    return

def is_valid_variable_name(variable_name):
    return variable_name.isidentifier()

def is_proper_number(_string):
    try:
        v = int(_string)
        return True 
    except Exception as e:
        return False 
    
def is_proper_operator(_string, rule_json):
    for i in range(len(_string)):
        if _string[i] in rule_json['operator']:
            continue 
        else:
            return False 
    return True 

def make_single_space_separation_for_line(normal_line=""):
    # Ex a    b -> a b
    t = normal_line.strip().split()
    t = " ".join(t)
    t = t.strip()
    return t 

def shift_left(code_lines=[], start_shift=3):
    # 3->2,4->3, 5->4, etc 
    for i in range(start_shift, len(code_lines)):
        code_lines[i-1] = code_lines[i]
    del code_lines[-1] # removing the last one 
    return code_lines 

def consisting_the_expected_placements(code_lines=[], rule_json = {}, checking_type = "operator"):
    # ex: a + \b -> a + b
    i = 0 
    while i < len(code_lines):
        temp = code_lines[i].split()
        op = False 
        for j in range(0, len(temp)):
            verdict = None 
            if checking_type == "operator":
                verdict = is_proper_operator(_string=temp[j], rule_json=rule_json) 
            else:
                if rule_json['placement_positions'][checking_type].get(temp[j]) is not None:
                    verdict = True 
            if verdict is True: # an operator is found 
                op_type = None 
                if rule_json['placement_positions'][checking_type].get(temp[j]) is not None: # Fully present as operator
                    op_type = rule_json['placement_positions'][checking_type].get(temp[j])
                elif rule_json['placement_positions'][checking_type].get(temp[j][-1]) is not None: # decision on last character 
                    op_type = rule_json['placement_positions'][checking_type].get(temp[j][-1])
                elif rule_json['placement_positions'][checking_type].get(temp[j][0]) is not None: # decision on first character 
                    op_type = rule_json['placement_positions'][checking_type].get(temp[j][0])
                else:
                    continue 
                if op_type is not None: # B, UF, UB
                    #print(temp[j], rule_json['operator_expects'].get(temp[j]), rule_json['operator_expects'].get(temp[j][-1]), rule_json['operator_expects'].get(temp[j][0]))
                    if op_type == "B" : # something should be in front and after it
                        if j == 0 and i >= 1: # nothing is in front of it, which is also a problem, merging it to previous statement  
                            code_lines[i-1] = code_lines[i-1] + " " + code_lines[i].strip() 
                            code_lines = shift_left(code_lines = code_lines, start_shift=i+1)
                            op = True 
                            i = i-1
                            break 
                        if (j+1) >= len(temp) and (i+1) < len(code_lines): # nothing afterwards which is a problem, unexpected line break, fetching the next line
                            code_lines[i] = code_lines[i] + " " + code_lines[i+1].strip()
                            code_lines = shift_left(code_lines = code_lines, start_shift=i+2)
                            op = True 
                            break            
                    if op_type == "UF":
                        if (j+1) >= len(temp) and (i+1) < len(code_lines): # nothing afterwards which is a problem, unexpected line break, fetching the next line
                            code_lines[i] = code_lines[i] + " " + code_lines[i+1].strip()
                            code_lines = shift_left(code_lines = code_lines, start_shift=i+2)
                            op = True 
                            break       
                    if op_type == "UB":
                        if j == 0 and i >= 1: # nothing is in front of it, which is also a problem, merging it to previous statement  
                            code_lines[i-1] = code_lines[i-1] + " " + code_lines[i].strip() 
                            code_lines = shift_left(code_lines = code_lines, start_shift=i+1)
                            op = True 
                            i = i-1
                            break       
        if op is False: # no operation next line 
            i += 1 
    return code_lines


def combining_operators(_string, rule_json, max_op_length=2):
    i = 0
    f_string = ""
    while i < len(_string):
        f = ""
        best_ans = None
        for j in range(0, max_op_length):
            if (i+j) >= len(_string):
                break 
            f = f + _string[i+j]
            if f in rule_json['operator']:
                best_ans = f 
        i += len(best_ans)
        f_string = f_string + " " + best_ans 
    return f_string


def creating_space_around_operator(code_lines=[], rule_json={}):
    # example: a+b -> a + b
    updated_code_lines = []
    for i in range(0, len(code_lines)):
        j = 0
        temp = ""
        while j < len(code_lines[i]):
            if code_lines[i][j] in rule_json['operator']:
                merged_operator =  code_lines[i][j]
                j += 1
                while j < len(code_lines[i]):
                    if code_lines[i][j] == ' ' or code_lines[i][j] == '\t': # space is fine
                        j += 1
                    elif code_lines[i][j] in rule_json['operator']: # an operator has been encountered, merged operator 
                        # option 1
                        merged_operator += code_lines[i][j]
                        j += 1 
                    else: # not an operator 
                        break 
                ss = combining_operators(_string=merged_operator, rule_json=rule_json, max_op_length=2)
                merged_operator = ss 
                temp = temp + " " + merged_operator + " " 
            else:
                temp = temp + code_lines[i][j]
                j += 1
        temp = make_single_space_separation_for_line(normal_line=temp)
        updated_code_lines.append(temp)
    return updated_code_lines

def first_bracket_paranthesis_closure(_string=[], starting_idx=0):
    # (...) finding
    ct = 0 
    for i in range(starting_idx, len(_string)):
        for k in range(0, len(_string[i])):
            if _string[i][k] == '(':
                ct += 1
            if _string[i][k] == ')':
                ct -= 1 
                if ct == 0: # paranthesis balanced 
                    return i, k  
    return None, None 

def shift_right(code_lines=[], idx=0):
    if idx >= len(code_lines):
        code_lines.append([])
        return code_lines
    j = len(code_lines)-1
    while j >= idx: # shifting from idx 
        if j == (len(code_lines)-1):
            code_lines.append([])
        code_lines[j+1] = code_lines[j]
        j -= 1
    return code_lines


def properly_conditioning_fragments(code_lines=[], branching_keywords = ['if', 'else if', 'elif', 'for', 'while'], lang="java", rule_json={}):
    if lang == "python":
        return code_lines # no one liner and brackets
    i = 0 
    stack_history = []
    while i < len(code_lines):
        temp = code_lines[i].strip().split()
        op = False 
        for j in range(0, len(temp)):
            if temp[j] in branching_keywords: # should have a starting bracket { (java, c, c++) as early as possible or semicolon (java,c,c++)
                word, pos = first_bracket_paranthesis_closure(_string=temp, starting_idx=j)
                if word is not None and pos is not None: # in some word, the paranthesis has closed 
                    # need to search for semicolon or opening brackets, at least one should be found
                    # else this should not be in the same line, breaking required to the next line 
                    no_op_req = None 
                    brk_pos = None 
                    for k in range(word+1, len(temp)): # searcing for the presence of a new line 
                        if '{' in temp[k][0]: # as string, there can be a bundle together
                            no_op_req = True # good thing 
                            break 
                        if is_valid_variable_name(temp[k]) or temp[k] in rule_json['name_keywords'] or temp[k] in rule_json['library_keywords'] or temp[k] in rule_json['generic_keywords'] or temp[k][0] in rule_json['operator']:
                            # something started without bracket: problem 
                            no_op_req = False # needs an operation
                            brk_pos = k # breaking position of the line 
                            break 
                    if no_op_req is None: # no verdict is found still, a bracket might be in the next line or already one liner has been avoided  
                        continue 
                    if no_op_req is True: # surely no operation is required , { is found 
                        continue # start with next j 
                    if no_op_req is False: # it must need an operation, one liner has been used 
                        # Going to add a new line here 
                        brancher = temp[j]
                        new_temp = temp[brk_pos:]
                        new_temp = " ".join(new_temp)
                        new_temp = new_temp.strip() # new line make 

                        temp = temp[0:brk_pos]
                        temp = " ".join(temp)
                        temp = temp.strip() # old line formation  
                        # insert as a new line
                        # print("prev ", len(code_lines), code_lines[i])
                        if len(new_temp) > 0 and len(temp) > 0:
                            code_lines[i] = temp
                            code_lines = shift_right(code_lines=code_lines, idx=i+1)
                            #print("now ", len(code_lines), i+1)
                            #print("temp ", temp)
                            #print("new temp ", new_temp)
                            #print("brancher ", brancher)
                            code_lines[i+1] = new_temp 
                            op = True 
                            temp = temp.split(' ') # for consistency of the else portion following
                        break  
            else: # normal thing it can be anything 
                pass 
        if op is False:
            i += 1 
        else:
            sen = " ".join(temp) # normal merge
            sen = sen.strip().split() # find the raw elements 
            sen = " ".join(sen) # simple join
            sen = sen.strip() # redundant spaces 
            code_lines[i] = sen 
    return code_lines 

def removing_single_line_comment(code_lines=[], lang="java"):
    if lang in ["java", 'c', 'c++']:
        sign = '//'
    elif lang in ['python']:
        sign = '#'
    store_comments = []
    updated_code_lines = []
    for i in range(0, len(code_lines)):
        temp = code_lines[i].strip().split()
        comment = ""
        rem_string = ""
        for j in range(0, len(temp)):
            if sign in temp[j]:
                if temp[j][0] == sign[0]: # in front
                    #print(temp)
                    comment = temp[j:]
                    comment = " ".join(comment)
                    comment = comment.strip()
                    store_comments.append(comment) # [i, comment]
                elif  temp[j][-1] == sign[0]: # at last 
                    #print(temp)
                    rem_string += " " + temp[j][0:-len(sign)] # last one/two character avoiding 
                    comment = temp[j:]
                    comment = " ".join(comment)
                    comment = comment.strip()
                    store_comments.append(comment) # [i, comment]
                break   
            else:
                rem_string = rem_string + " " + temp[j]  
        rem_string = rem_string.strip()
        if len(rem_string) > 0:
            rem_string = rem_string.strip().split()
            rem_string = " ".join(rem_string)
            updated_code_lines.append(rem_string.strip())
    return updated_code_lines, store_comments 

def remove_block_of_comments(code_lines=[], lang="java"):
    start_sym, en_sym = '/*', '*/'
    ct = 0 
    updated_code_lines = []
    store_comments = []
    for i in range(0, len(code_lines)):
        temp = code_lines[i].strip().split()
        f_string = ""
        comment = ""
        for j in range(0, len(temp)):
            if start_sym in temp[j]:
                if ct == 0 and temp[j][-1] == '*' and temp[j][-2] == '/':
                    f_string += temp[j][0:-2] # Found at last so something should come 
                ct += 1  
            elif en_sym in temp[j]:
                ct -= 1 
                if ct == 0 and temp[j][1] == '/' and temp[j][0] == '*':
                    f_string += temp[j][2:]
            else:
                if ct == 0: # no on going block comment 
                    f_string = f_string + " " + temp[j]
                else:
                    comment = comment + " " + temp[j] 
        f_string = f_string.strip()
        comment = comment.strip()
        if len(f_string) > 0:
            updated_code_lines.append(f_string)
        if len(comment) > 0:
            store_comments.append(comment) # [i, comment]
    return updated_code_lines, store_comments

def new_line_addition(code_lines=[], delim='{', maps = {'{': '\n{\n', '}': '\n}\n', ';': ';\n'}):
    # if delim in '{', '[' -> it will be in a single line 
    # if delim in '; add a new line after it 
    i = 0 
    updated_code_lines = []
    while i < len(code_lines):
        code_lines[i] = code_lines[i].strip()
        temp = code_lines[i].replace(delim, maps[delim])
        temp = temp.strip().split('\n')
        for j in range(0, len(temp)):
            temp[j] = temp[j].strip()
            if len(temp[j]) > 0:
                updated_code_lines.append(temp[j])
        i += 1
    return updated_code_lines


def search_in_var_history(var_history, variable, cur_timestamp, stack_history):
    if var_history.get(variable) is not None:
        if cur_timestamp == -1:
            return var_history[variable][0][0] # just the first one
        save = -1
        idx = -1
        j = 0 
        for i in range(0, len(stack_history)):
            tim = stack_history[i][1]
            while j < len(var_history[variable]):
                if var_history[variable][j][1] > tim: # exceeding limit 
                    break 
                idx = j # within bound and scope
                j += 1 
        if idx != -1:
            return var_history[variable][idx][0] # the mapped variable 
    return None 

def identify_blocks_in_variable_tracking(temp=[], starting_idx=0, op_to_consider="<"):
    """
    input - 
    temp - I am working on this as a list 
    starting_idx - start matching from here 
    op_to_consider = {, <,  (, [
    output - 
    return None, where did not match expectation 
    else return the ending ptr 
    """
    block_open = ['<', '{', '[', '('] 
    block_close =  ['>', '}', ']', ')'] 
    opener_sign = None 
    closer_sign = None 
    for i in range(0, len(block_open)):
        if block_open[i] in op_to_consider: # to handle <<, the first element is being considered
            opener_sign = block_open[i] 
            closer_sign = block_close[i]
            break 
    if opener_sign is None:
        return None 
    cnt  = 0 
    for i in range(starting_idx, len(temp)):
        if opener_sign in temp[i]:
            cnt += 1
        if closer_sign in temp[i]:
            cnt -= 1
        if cnt == 0:
            return i # where is ending 
    return None # it does not create blocks 

def replace_all_var_not_tagged(code_lines=[], rule_json={}, blueprint={}):
    # replacing the variables that could not be replaced with var alike keywords 
    for i in range(0, len(code_lines)):
        temp = code_lines[i].strip().split()
        lib_keyword_found = False 
        to_be_changed = []
        for j in range(0, len(temp)):
            if temp[j] in rule_json['library_keywords']: # a library related keyword is found, this line is special 
                lib_keyword_found = True
                continue 
            if temp[j] in rule_json['name_keywords'] or temp[j] in rule_json['custom_keywords'] or temp[j] == 'CUSTOM_OOP_WORD' or temp[j] in rule_json['generic_keywords']:
                continue # this can not be continued, a given keyword there  
            if blueprint[i][j] == 0 and is_valid_variable_name(temp[j]) is True: # not been replaced 
                to_be_changed.append([j, temp[j]])
        if lib_keyword_found is False:
            for j in range(0, len(to_be_changed)):
                temp[to_be_changed[j][0]] = "MISC_VAR" # miscellenious var 
                blueprint[i][to_be_changed[j][0]] = 1 
        _string = " ".join(temp)
        _string = _string.strip()
        code_lines[i] = _string 
    return code_lines 

def normalize_var_in_code (code_lines=[], rule_json={}, lang="java", oop_keywords=['struct', 'class'], ITR_THRESHOLD = 100):
    stack_history = [] # stack history of brackets 
    stack_history_cp = []
    blueprint = []
    # A binary blueprint of the variables 
    for i in range(0, len(code_lines)):
        blueprint.append([])
        temp = code_lines[i].strip().split()
        for j in range(0, len(temp)):
            blueprint[-1].append(0)
    var_history = {} # track the history of the variables 
    rule_json['custom_keywords'] = [] 
    max_itr = 0
    while max_itr <= ITR_THRESHOLD:
        new_dec = False  
        bracket_timestamp = 0 
        bracket_timestamp2 = 0 
        stack_history = []
        stack_history_cp = []
        stack_history.append(['START', bracket_timestamp])
        stack_history_cp.append(['START', bracket_timestamp2])
        for i in range(0, len(code_lines)):
            temp = code_lines[i].strip().split()
            # First try map the variables 
            for j in range(0, len(temp)):
                # timestamp calculation 
                if '{' in temp[j]:
                    bracket_timestamp += 1
                    stack_history.append(['{', bracket_timestamp])
                if '}' in temp[j]:
                    stack_history.pop() # removing a timestamp 
                if temp[j] in rule_json['name_keywords'] or temp[j] in rule_json['custom_keywords'] or temp[j] == 'CUSTOM_OOP_WORD': # map all the variables here 
                    k = j+1
                    if temp[j] in rule_json['custom_keywords']: # Forcing class/struct names to be changed 
                        temp[j] = 'CUSTOM_OOP_WORD'
                        if len(stack_history) == 0:
                            tim = -1
                        else:
                            tim = stack_history[-1][1]
                        res = search_in_var_history(var_history=var_history, variable=temp[j], cur_timestamp=tim, stack_history=stack_history) 
                        if res is not None:
                            temp[j] = res # normalizing it with prior naming 
                            blueprint[i][j] = 1 # its set properly
                    while k < len(temp):
                        k_prime = identify_blocks_in_variable_tracking(temp=temp, starting_idx=k, op_to_consider=temp[k][0])
                        if k_prime is not None: # matched the segment, so moved the ptr < ... >, { ... }, [ ... ]
                            k = k_prime+1
                            continue 
                        elif temp[k][0] == ',': # multiple variable name possibility 
                            k += 1
                            continue 
                        elif temp[k] in rule_json['operator']: # ++, +, -, *, 
                            k += 1 
                            continue 
                        elif is_proper_number(temp[k]) is True: # its a number moving forward
                            k += 1
                            continue 
                        if blueprint[i][k] == 0 and is_valid_variable_name(temp[k]) is True: # potential variable candidate that has not been mapped prior 
                            if temp[k] not in rule_json['name_keywords'] and temp[k] not in rule_json['library_keywords'] and temp[k] not in rule_json['generic_keywords'] and temp[k] not in rule_json['custom_keywords']:
                                # a proper variable not present in keywords 
                                blueprint[i][k] = 1 # mapped variable 
                                if var_history.get(temp[k]) is None:
                                    var_history[temp[k]] = []

                                if temp[j] in rule_json['name_keywords'] and temp[j] in oop_keywords: #class, struct -> CUSTOM_OOP_WORD
                                    var_history[temp[k]].append(["CUSTOM_OOP_WORD", stack_history[-1][1]]) # saving history for future usage
                                    if temp[k] not in rule_json['custom_keywords']: # CLass C , C becomes a new custom keyword and we say C -> CUSTOM_OOP_WORD
                                        rule_json['custom_keywords'].append(temp[k])
                                    temp[k] = 'CUSTOM_OOP_WORD'
                                    new_dec = True # history updated 
                                elif  temp[j] in rule_json['name_keywords']: # int, float, double, etc -> INT, FLOAT, DOUBLE etc 
                                    var_history[temp[k]].append([temp[j].upper(), stack_history[-1][1]])
                                    temp[k] = temp[j].upper()
                                    new_dec = True # history updated
                                elif temp[j] in rule_json['custom_keywords']: # CUSTOM_VAR 
                                    var_history[temp[k]].append(["CUSTOM_VAR", stack_history[-1][1]])
                                    temp[k] = "CUSTOM_VAR"
                                    new_dec = True # history updated
                                elif temp[j]  == "CUSTOM_OOP_WORD": # CUSTOM_VAR
                                    var_history[temp[k]].append(["CUSTOM_VAR", stack_history[-1][1]])
                                    temp[k] = "CUSTOM_VAR"
                                    new_dec = True # history updated
                                k += 1
                            else: # something that is some sort of keyword, can't continue further 
                                break 
                        else:
                            break # something other than that, not allowed to continue to be mapped 
            # second try, mapping existing already declared variables
            for j in range(0, len(temp)):
                # timestamp calculation 
                if '{' in temp[j]:
                    bracket_timestamp2 += 1
                    stack_history_cp.append(['{', bracket_timestamp2])
                if '}' in temp[j]:
                    stack_history_cp.pop() # removing a timestamp
                if is_valid_variable_name(temp[j]) and blueprint[i][j] == 0: # variable that has not been mapped, check history and extract info 
                    if temp[j] not in rule_json['name_keywords'] and temp[j] not in rule_json['library_keywords'] and temp[j] not in rule_json['generic_keywords'] and temp[j] not in rule_json['custom_keywords']:
                        # proper variable, lets search in its history 
                        if len(stack_history_cp) == 0:
                            tim = -1
                        else:
                            tim = stack_history_cp[-1][1]
                        res = search_in_var_history(var_history=var_history, variable=temp[j], cur_timestamp=tim, stack_history=stack_history_cp)
                        if res is not None:
                            temp[j] = res # normalizing it with prior naming 
                            blueprint[i][j] = 1 # its set properly 
            _string = " ".join(temp)
            _string = _string.strip()
            code_lines[i] = _string # no history updated 
        if new_dec is False:
            break 
    # print(var_history)
    # iterating over the whole list of strings, if blueprint is not set and no 
    # replacing dynamically created variables or untracked variables 
    code_lines = replace_all_var_not_tagged(code_lines=code_lines, rule_json=rule_json, blueprint=blueprint)
    return code_lines
                
    
def space_wise_clean_code(file_name = ""):
    """
    -input:
        file_name: file path
    -output
        a list of clean code lines 
    """
    # getting a space wise clean code 
    code_lines = []
    if os.path.exists(os.path.join(file_name)):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            for i in range(0, len(lines)):
                l = lines[i].strip().split()
                if len(l) > 0:
                    temp = " ".join(l)
                    temp = temp.strip()
                    if len(temp) > 0:
                        code_lines.append(temp) 
    return code_lines

 
def normalize(code_file=""):
    print(f'code_file {code_file}')
    root_path = os.path.join('.', 'system_functions')
    rule_json = {}
    lang = os.path.basename(code_file).split('.')[1] #c, cpp, java 
    if lang == "cpp":
        lang = "c++"
    if lang == "py":
        lang = "python" 
    if lang == "java":
        lang = "java"
    # print(lang) 
    # B: binary, UF: Unary forward placement, UB: Unary backward placement,
    placement_position1, placement_position2, placement_position3 = None, None, None 
    rule_json['operator'], placement_position1 = read_csv_file(file_name=os.path.join(root_path, 'copy_checker', 'resource', 'operator_list.csv'), lang=lang)
    rule_json['operator'].append(',') # special addition
    placement_position1[','] = 'B' 

    maps = {'{': '\n{\n', '}': '\n}\n', ';': ';\n'}
    rule_json['library_keywords'], placement_position2 = read_csv_file(file_name=os.path.join(root_path, 'copy_checker', 'resource', 'library_keywords.csv'), lang=lang)
    rule_json['name_keywords'],placement_position3 = read_csv_file(file_name=os.path.join(root_path, 'copy_checker', 'resource', 'name_keywords.csv'), lang=lang) # These creates variables
    rule_json['generic_keywords'],placement_position4 = read_csv_file(file_name=os.path.join(root_path, 'copy_checker', 'resource', 'generic_keywords.csv'), lang=lang) # for, while, if, etc 
    
    rule_json['placement_positions'] = {}
    rule_json['placement_positions']['operator'] = placement_position1
    rule_json['placement_positions']['library_keywords'] = placement_position2
    rule_json['placement_positions']['name_keywords'] = placement_position3
    rule_json['placement_positions']['generic_keywords'] = placement_position4
    
    #print(rule_json)
    # code_lines = read_code_file(code_file=code_file)
    main_given_code_lines = read_exact_lines(code_file= code_file)
    # 0: just making single space 
    code_lines = space_wise_clean_code(file_name = code_file)
    #print(len(code_lines))

    # 1: clearing up operator placements with spaces, to properly understand them, merging if they are side by side  
    code_lines = creating_space_around_operator(code_lines=code_lines, rule_json=rule_json)
    # print("START STATUS ", code_lines)

    # 2: multi line comment removal
    code_lines, block_comments = remove_block_of_comments(code_lines=code_lines, lang="java")

    # 3: single line comment removal 
    code_lines, single_line_comments = removing_single_line_comment(code_lines=code_lines, lang=lang)

    
    #print(store_comments1, store_comments2)
    #4: consisting all the binary operators, name_keywords, library_keywords, generic ones expectations - to have their respective operands infront, behind or both 
    code_lines = consisting_the_expected_placements(code_lines=code_lines, rule_json = rule_json, checking_type="operator")
    code_lines = consisting_the_expected_placements(code_lines=code_lines, rule_json = rule_json, checking_type="name_keywords")
    code_lines = consisting_the_expected_placements(code_lines=code_lines, rule_json = rule_json, checking_type="generic_keywords")
    code_lines = consisting_the_expected_placements(code_lines=code_lines, rule_json = rule_json, checking_type="library_keywords")

    
    
    # 5: Adding {} for proper curly brace enclosure
    code_lines = properly_conditioning_fragments(code_lines=code_lines, 
                                                 branching_keywords = ['if', 'else if', 'elif', 'for', 'while'], lang="java", rule_json=rule_json)
    # 6: Variable replaced code line 
    var_replaced_code_lines = code_lines.copy()
    var_replaced_code_lines = normalize_var_in_code(code_lines=var_replaced_code_lines, rule_json=rule_json, lang="java",  oop_keywords=['struct', 'class', 'new'])
    
    # x : The last new line breaking, block by block 
    code_lines = new_line_addition(code_lines=code_lines, delim='{', maps = maps)
    code_lines = new_line_addition(code_lines=code_lines, delim=';', maps = maps)
    #write_code_file(code_lines=code_lines, file_name=os.path.join('.', 'submitted_assignments', 'normalized.txt'))
    #print(len(code_lines))
    
    var_replaced_code_lines = new_line_addition(code_lines=var_replaced_code_lines, delim='{', maps = maps)
    var_replaced_code_lines = new_line_addition(code_lines=var_replaced_code_lines, delim=';', maps = maps)
    #write_code_file(code_lines=var_replaced_code_lines, file_name=os.path.join('.', 'submitted_assignments', 'var_replaced_normalized.txt'))
    #print(len(var_replaced_code_lines))
    # print("came ei porjonto ", code_lines)
    already_mapped_sr = {}
    map_dict, already_mapped_sr = map_source_norm(source_code_lines=main_given_code_lines, norm_code_lines = code_lines, already_mapped_sr=already_mapped_sr)
    # print("block comments single line comments", block_comments, single_line_comments)
    map_dict_block_com, already_mapped_sr = map_source_norm(source_code_lines=main_given_code_lines, norm_code_lines = block_comments, already_mapped_sr=already_mapped_sr)
    map_dict_single_com, already_mapped_sr = map_source_norm(source_code_lines=main_given_code_lines, norm_code_lines = single_line_comments, already_mapped_sr=already_mapped_sr)
    # print("map_dict_single_com ", map_dict_single_com)
    # print_matched_fragments(source_code_lines=main_given_code_lines, norm_code_lines=code_lines, map_dict=map_dict)
    return code_lines, var_replaced_code_lines, map_dict, block_comments, single_line_comments, map_dict_block_com, map_dict_single_com
    
    
if __name__ == '__main__':
    normalize(code_file=os.path.join('.', 'problem_descriptions', '11', 'teacher_solution', 'solution', 'Problem.java'))

   
   

