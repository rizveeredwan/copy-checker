ignore_characters = ['\n', ' ', '\t', '\b', '{', '}']
def req_char(a, b):
    if a.lower() == b.lower():
        return True
    if a in ignore_characters:
        return True 
    return False 

def act_char(text=""):
    ct = 0 
    for i in range(0, len(text)):
        ct += char_validity(text[i])
    return ct 

def char_validity(char):
    if char not in ignore_characters:
        return 1 
    else:
        return 0 

def only_word_parse(text=""):
    _list = []
    ongoing = ""
    for i in range(0, len(text)):
        if text[i] in ignore_characters:
            if ongoing != "":
                _list.append(ongoing)
                ongoing = ""
            _list.append(text[i])
        else:
            ongoing = ongoing + text[i] 
    if ongoing != "":
        _list.append(ongoing)
    return _list 

def find_char_idx_from_word(text=[], cur_word_idx=0):
    ptr = 0
    for i in range(0, cur_word_idx):
        ptr += len(text[i]) 
    return ptr-1 # i have seen upto this index 

def string_match(pattern="", text="", st_idx=0):
    flag = False 
    for i in range(0, len(pattern)):
        if (st_idx+i) < len(text) and text[st_idx+i] == pattern[i]:
            flag = True 
        else:
            flag = False 
            break 
    return flag 

def word_by_word_match(text1=[], st1=0, en1=0, text2=[], st2=0, en2=0, norm_line=0, source_line=0, already_mapped_sr={}):
    """
    text1, should be specially tokenized, keeping space and adjacent characters separately, i moves word by word 
    text2 is a single string, j moves character by character 
    already_mapped_sr denotes which character of the source code has already been mapped 
    """
    text1_ptr = find_char_idx_from_word(text=text1, cur_word_idx=st1)
    i = st1 
    j = st2 
    matched_pairs = {}
    while i <= en1 and j <= en2:
        if text1[i] in ignore_characters:
            text1_ptr += len(text1[i])
            i += 1
            continue 
        while j <= en2:
            if text2[j] in ignore_characters:
                j += 1
                continue 
            if already_mapped_sr.get(source_line) is not None and already_mapped_sr[source_line].get(j) is not None:
                j += 1 # this character of the source code is already mapped 
                continue 
            flag = string_match(pattern=text1[i], text=text2, st_idx=j)
            if flag is True: # string matching 
                # fully word matched, now make the character by character matching
                for k in range(0, len(text1[i])):
                    text1_ptr += 1
                    matched_pairs[text1_ptr] = j 
                    if already_mapped_sr.get(source_line) is None:
                        already_mapped_sr[source_line] = {}
                    already_mapped_sr[source_line][j] = [norm_line, text1_ptr]
                    j += 1  
                i += 1
                break 
            else: # string did not match 
                return i, j+1, matched_pairs, already_mapped_sr
    return i, j, matched_pairs, already_mapped_sr


def character_map(text1="", st1=0, en1=0, text2="", st2=0, en2=0):
    """
    - trying to match with text2 characters 
    - all valid characters should get mapped 
    - from the source code, I won't delete anything, a subset must be present in the normalized code but not adding something  (except for {, }) that 
        ain't in the source code 
    """
    j = st2 
    matched_pairs = {}
    i = st1 
    # print(f"st1 = {st1} en1 = {en1} st2 = {st2} en2 = {en2}")
    while i <= en1 and j<=en2:
        if text1[i] in ignore_characters:
            i += 1 
            continue 
        while j <= en2:
            if text2[j] in ignore_characters:
                j += 1
                continue
            if text1[i].lower() in text2[j].lower():
                matched_pairs[i] = j 
                i += 1
                j += 1 
                break  
            else:
                return i, j+1, matched_pairs # valid character did not match (i should match with someone, lets try with increase j)
    return i, j, matched_pairs


def map_source_norm(source_code_lines=[], norm_code_lines = [], already_mapped_sr={}):
    i, j, i_mv_ptr, j_mv_ptr = 0, 0, 0, 0 
    map_dict = {}
    while i < len(norm_code_lines) and j < len(source_code_lines):
        # print("i j ", i, j, len(norm_code_lines), len(source_code_lines), norm_code_lines[i], source_code_lines[j], i_mv_ptr, len(source_code_lines[i]), j_mv_ptr, len(source_code_lines[j]))
        # print(f"{i} {i_mv_ptr} {j} {j_mv_ptr} {norm_code_lines[i]} {source_code_lines[j]}")
        sparse_norm_code_lines = only_word_parse(text=norm_code_lines[i])
        # print("parallel lines ", sparse_norm_code_lines, norm_code_lines[i], source_code_lines[j])
        i_mv_ptr, j_mv_ptr, matched_pairs, already_mapped_sr = word_by_word_match(text1=sparse_norm_code_lines, st1=i_mv_ptr, en1=len(sparse_norm_code_lines)-1, text2=source_code_lines[j], 
                                                          st2=j_mv_ptr, en2=len(source_code_lines[j])-1, norm_line=i, source_line=j, already_mapped_sr=already_mapped_sr)
        #print("i_mv_ptr j_mv_ptr ",i_mv_ptr, j_mv_ptr)
        #print("matched_pairs ", matched_pairs)
        if map_dict.get(i) is None:
            map_dict[i] = {}
        for new_ent in matched_pairs:
            map_dict[i][new_ent] = [j, matched_pairs[new_ent]]
        if i_mv_ptr >= len(sparse_norm_code_lines):
            i += 1 
            i_mv_ptr = 0 
        if j_mv_ptr >= len(source_code_lines[j]):
            j += 1
            j_mv_ptr = 0  
    # print_matched_fragments(norm_code_lines=norm_code_lines, map_dict=map_dict)
    return map_dict, already_mapped_sr


def return_char_num_in_main_code(map_dict={}, line_no_in_norm=0, char_number=0):
    """
    - trying to find, which character matched in the real code with the normalized code for a particular line's particular character 
    """
    if map_dict.get(line_no_in_norm) is not None and map_dict[line_no_in_norm].get(char_number) is not None:
            return map_dict[line_no_in_norm][char_number] 
    else:
        return None  # nothing matched
    
def print_matched_fragments(norm_code_lines=[], map_dict={}):
    for i in range(0, len(norm_code_lines)):
        for j in range(0, len(norm_code_lines[i])):
            if norm_code_lines[i][j] in ignore_characters:
                continue 
            val = map_dict.get(i).get(j) # ith line, jth character 
            print(i, j, "val = ", val, norm_code_lines[i][j], len(norm_code_lines[i][j]))

if __name__ == '__main__':
    text1 = "int a = 10"
    text2 = "int A = 10"