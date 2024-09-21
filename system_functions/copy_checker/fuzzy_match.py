import os
import functools

#print(os.getcwd())
#print(os.path.exists('file_matcher'))


from system_functions.file_matcher.lcs import LCS
from system_functions.copy_checker.match_source_with_norm import *

alpha_param = 0.7
ignoring_characters = ['{', '}']


def func_sort_pair(x, y):
    global alpha_param
    sc_x = alpha_param * x[3] + (1.0-alpha_param) * x[5]
    sc_y = alpha_param * y[3] + (1.0-alpha_param) * y[5]
    if sc_x > sc_y:
        return -1
    if sc_x < sc_y:
        return 1
    return 0


class FuzzyMatch:
    def __init__(self):
        self.lcs_module = LCS()
        self.dp = {}
        self.pairs = []
        self.match_results = []
        self.alpha = 1.0

    def print_lines(self, lines):
        for i in range(0, len(lines)):
            print(lines[i])

    def print_arr(self, lcs_print_array):
        for i in range(0, len(lcs_print_array)):
            # print("i = ",i)
            for j in range(0, len(lcs_print_array[i])):
                print(lcs_print_array[i][j][0])

    def make_single_string_rem_spc(self, _string):
        t = _string.split()
        t = "".join(t)
        return t

    def make_char_dict(self, temp):
        data_dict = {}
        for i in range(0, len(temp)):
            if temp[i] in ignoring_characters:
                continue
            if data_dict.get(temp[i]) is None:
                data_dict[temp[i]] = 0
            data_dict[temp[i]] += 1
        return data_dict

    def heuristic_match_betweek_two_dict(self, data_dict_i={}, data_dict_j={}):
        tot_common = 0
        LEN1 = 0
        for key in data_dict_i:
            mt = 0
            LEN1 += data_dict_i[key]
            if data_dict_j.get(key) is not None:
                mt = min(data_dict_i[key], data_dict_j[key])
            tot_common += mt
        LEN2 = 0
        for key in data_dict_j:
            LEN2 += data_dict_j[key]
        return tot_common, LEN1, LEN2

    def process_n_sq_match(self, base_output, found_output, level_threshold=0, small_match_val=0.0001, print_interval=1000):
        """
        input:
            level_threshold: 0 -> fully granular, 1-> at least 30% character presence, 2->at least 60% character presence, 3-> at least 90% character presence 
        """
        # compute LCS (n^2) based on heuristics 
        level_threshold_vec = [0, 0.25, 0.5, 0.75, 0.9, 1.00]
        lcs_results_array = {}
        self.pairs.clear()
        temp_base_output, temp_found_output = [], []
        temp_base_output = base_output
        temp_found_output = found_output

        for i in range(0, len(temp_base_output)):
            lcs_results_array[i] = {}
            for j in range(0, len(temp_found_output)):
                lcs_results_array[i][j] = []
        M, N = None, None
        LEN_TEMP_BASE = len(temp_base_output)
        LEN_TEMP_FOUND = len(temp_found_output)
        ct = 0
        all_data_dict_base = []
        all_data_dict_found = []
        for i in range(0, LEN_TEMP_BASE):
            all_data_dict_base.append(self.make_char_dict(temp=temp_base_output[i]))
        for i in range(0, LEN_TEMP_FOUND):
            all_data_dict_found.append(self.make_char_dict(temp=temp_found_output[i]))
        for i in range(0, LEN_TEMP_BASE):
            _m = temp_base_output[i]
            for j in range(0, LEN_TEMP_FOUND):
                _n = temp_found_output[j]
                tot_common, LEN1, LEN2 = self.heuristic_match_betweek_two_dict(data_dict_i=all_data_dict_base[i], data_dict_j=all_data_dict_found[j])
                if LEN1 == 0 or LEN2 == 0:
                    lcs_results_array[i][j] = [small_match_val*tot_common, small_match_val, 1, None]
                    continue
                opt1 = tot_common / (LEN1*1.0)
                opt2 = tot_common / (LEN2*1.0)
                max_opt = max(opt1, opt2)
                max_length = max(1, max(len(_m), len(_n)))
                if max_opt < level_threshold_vec[level_threshold]: # less than expectations
                    res = tot_common
                    lcs_results_array[i][j] = [small_match_val*tot_common, small_match_val, max_length, None] # very insignificant matching weight * min_matching
                else:
                    # print(i, j, temp_base_output[i], temp_found_output[j])
                    res, matches = self.lcs_module.begin_matching(M=_m, N=_n) # maximum matching, matched characters' indexes
                    # arr = self.lcs_module.return_copy_of_dp()
                    lcs_results_array[i][j] = [res, res*1.0/max_length, max_length, matches] # maximum match, normalizing, total length of the string
                ct += 1
                if print_interval !=-1 and ct % print_interval == 0:
                    print(f"completed {ct} pairs among {LEN_TEMP_BASE * LEN_TEMP_FOUND} threshold considered {level_threshold_vec[level_threshold]}")
                # self.pairs.append([i, j, res, max(res/len(_m),len(_n))])
        # print(lcs_results_array)
        # print("stat ", len( base_output), len(found_output), M, N)
        # self.memory_clear()
        # res = self.sorting_based_solution()
        # self.print_matched_pairs(base=base_output, found=found_output)
        # print("verdict ",verdict)
        return lcs_results_array # res vs new thing

    def place_uid_in_source_code(self, map_dict={}, setblueprint={}, norm_code_line=0, uid=0):
        # all the characters of the line (in normalized code) are considered found 
        # print("length ", len(setblueprint))
        if map_dict.get(norm_code_line) is not None:
            for key in map_dict[norm_code_line]: # 1:3: [5 th line, 7th character]
                try:
                    _line = map_dict[norm_code_line][key][0]
                    _ch = map_dict[norm_code_line][key][1]
                    # print(f"{key} {_line} {_ch}")
                    if setblueprint.get(_line) is None:
                        setblueprint[_line] = {}
                    setblueprint[_line][_ch] = uid
                except Exception as e:
                    print("error in place uid ", e)
        return setblueprint

    def place_uid_in_source_code_exact(self, map_dict={}, setblueprint={}, norm_code_line=0, exact_matched_idx=[], uid=0):
        # only the matched characters are considered as found, not blindly all the characters 
        for i in range(0, len(exact_matched_idx)):
            if map_dict.get(norm_code_line) is not None and map_dict[norm_code_line].get(exact_matched_idx[i]) is not None:
                _line = map_dict[norm_code_line][exact_matched_idx[i]][0] # main code _line
                _ch = map_dict[norm_code_line][exact_matched_idx[i]][1] # main code _line, character number
                if setblueprint.get(_line) is None:
                    setblueprint[_line] = {}
                setblueprint[_line][_ch] = uid
                # print("gotcha ", _line, _ch, " with ", norm_code_line, exact_matched_idx[i])
            else:
                # print("Yes none")
                pass
        return setblueprint

    def process(self, norm_lines1=[], var_norm_lines1=[], norm_lines2=[], var_norm_lines2=[], alpha=0.7, level_threshold=0, map_dict1={}, map_dict2={},
                created_id_offset=-1, char_match_style="fuzzy"):
        print("processing n_sq_match: started")
        lcs_simp = self.process_n_sq_match(base_output=norm_lines1, found_output=norm_lines2, level_threshold=level_threshold, small_match_val=0.0001, print_interval=1000)
        print("processing n_sq_match: ended")
        lcs_var_norm = None
        if var_norm_lines1 is not None and var_norm_lines2 is not None:
            print("processing n_sq_match (var_norm): started")
            lcs_var_norm = self.process_n_sq_match(base_output=var_norm_lines1, found_output=var_norm_lines2, level_threshold=level_threshold,
                                                                 small_match_val=0.0001, print_interval=1000)
            print("processing n_sq_match (var_norm): ended")

        similarity, match_results, setblueprint1, setblueprint2, created_id = self.greedy_matching(lcs_simp=lcs_simp, lcs_var_norm=lcs_var_norm, alpha=alpha, base_output=norm_lines1,
                                                         found_output=norm_lines2, map_dict1=map_dict1, map_dict2=map_dict2, created_id_offset=created_id_offset, char_match_style=char_match_style)
        print("similarity ", similarity)
        print("match results ", match_results)
        return similarity, match_results, setblueprint1, setblueprint2, created_id

    def raw_char_count(self, _string):
        temp = _string.strip()
        return len(temp)

    def greedy_matching(self, lcs_simp={}, lcs_var_norm={}, alpha=0.7, base_output=[], found_output=[], map_dict1={}, map_dict2={},
                        created_id_offset=-1, char_match_style="fuzzy"):
        setblueprint1, setblueprint2 = {}, {}
        # updating with given alpha 
        self.alpha = alpha
        pairs = []
        for i in lcs_simp:
            for j in lcs_simp[i]:
                # print(len(lcs_simp[i][j]))
                if lcs_var_norm is not None and lcs_var_norm.get(i) is not None and lcs_var_norm[i].get(j) is not None:
                    # line i, line j, max matching x 2, max matching var norm x 2, matched characters in indexes
                    pairs.append([i, j, lcs_simp[i][j][0], lcs_simp[i][j][1], lcs_var_norm[i][j][0], lcs_var_norm[i][j][1], lcs_simp[i][j][2], lcs_var_norm[i][j][2], lcs_simp[i][j][3]])
                else:
                    pairs.append([i, j, lcs_simp[i][j][0], lcs_simp[i][j][1], 0, 0, lcs_simp[i][j][2], 0, None])

        # sort 
        global alpha_param
        alpha_param = alpha
        pairs = sorted(pairs, key=functools.cmp_to_key(func_sort_pair))
        # match + score calculation 
        f1,f2={},{}
        match_results = []
        tot_match = 0.0
        hor = 1.0
        created_id = created_id_offset
        for i in range(0, len(pairs)):
            x = pairs[i][0]
            y = pairs[i][1]
            if f1.get(x) is None and f2.get(y) is None:
                f1[x],f2[y] = True, True
                tot_match += self.alpha * pairs[i][2] + (1.0-self.alpha) * pairs[i][4]
                hor = hor + (self.alpha * pairs[i][6] + (1.0-self.alpha) * pairs[i][7])
                assert(tot_match <= hor)
                # lcs report 
                created_id += 1 # a common id to be created for the character to be matched
                # print(x, y, " base ", base_output[x], " found ", found_output[y], "id ", created_id)
                match_results.append([x, y]) # all the stack here, to be saved
                if char_match_style == "fuzzy": # for the code portion/comment portion
                    setblueprint1 = self.place_uid_in_source_code(map_dict=map_dict1, setblueprint=setblueprint1, norm_code_line=x, uid=created_id)
                    setblueprint2 = self.place_uid_in_source_code(map_dict=map_dict2, setblueprint=setblueprint2, norm_code_line=y, uid=created_id)
                elif char_match_style == "exact": # for the comment portion
                    mem = {}
                    if pairs[i][-1] is not None:
                        mt = pairs[i][-1] # dp already calculated, the positions
                    else: # from raw matching
                        mt = self.find_matched_char(a=base_output[x], b=found_output[y], i=0, j=0, mem=mem)
                    #print("mt = ", mt)
                    #print("base ", base_output[x], len(base_output[x]))
                    #print("found ", found_output[y], len(found_output[y]))
                    if len(mt) > 0:
                        base_mt, found_mt = [], [] # going to separate the terms for two lines
                        c1, c2 = "", ""
                        for k in range(0, len(mt)):
                            if len(mt[k]) == 2:
                                base_mt.append(mt[k][0])
                                found_mt.append(mt[k][1])
                                # print("CAME ", x, len(base_output), base_output[x], k,  mt[k])
                                c1 += base_output[x][mt[k][0]]
                                c2 += found_output[y][mt[k][1]]
                                # print("completed")
                        #print("x y ", base_output[x], found_output[y])
                        #print("c1 c2 ", c1, c2, len(c1), len(c2), len(mt), mt)
                        setblueprint1 = self.place_uid_in_source_code_exact(map_dict=map_dict1, setblueprint=setblueprint1, norm_code_line=x, exact_matched_idx=base_mt, uid=created_id)
                        # print("completed")
                        setblueprint2 = self.place_uid_in_source_code_exact(map_dict=map_dict2, setblueprint=setblueprint2, norm_code_line=y, exact_matched_idx=found_mt, uid=created_id)
        similarity = (tot_match*100.0/hor)
        similarity = round(similarity, 2)
        return similarity, match_results, setblueprint1, setblueprint2, created_id

    def find_matched_char(self, a="", b="", i=0, j=0, mem={}):
        # which characters (actually positions) got matched between a and b
        #print("i = ", i, j, a, b, mem)
        if i == len(a) or j == len(b):
            #print("returning ")
            return []
        if mem.get(i) is not None and mem[i].get(j) is not None:
            #print("dhuke gese")
            return mem[i][j]
        if mem.get(i) is None:
            mem[i] = {}
        if mem[i].get(j) is None:
            mem[i][j] = [] # just for local saving
        if a[i] == b[j]:
            temp = []
            temp.append([i,j])
            #print("ashi ", mem)
            st = self.find_matched_char(a=a, b=b, i=i+1, j=j+1, mem=mem)
            for k in range(0, len(st)):
                if len(st[k]) == 2:
                    temp.append([st[k][0], st[k][1]])
            mem[i][j] = temp
        else:
            st1 = self.find_matched_char(a=a, b=b, i=i+1, j=j, mem=mem)
            st2 = self.find_matched_char(a=a, b=b, i=i, j=j+1, mem=mem)
            if len(st1) > len(st2):
                ms = st1
            else:
                ms = st2
            for k in range(0, len(ms)):
                if len(ms[k]) == 2:
                    mem[i][j].append([ms[k][0], ms[k][1]])
        return mem[i][j]

    def find_matched_character_without_dp(self, dp={}, a="", b=""):
        stored_result = []
        i = len(a)-1
        j = len(b)-1
        while i >= 0 and j >= 0:
            if a[i] == b[j]:
                stored_result.append([i, j])
                i = i-1
                j = j -1
            if dp[i][j-1] > dp[i-1][j]:
                j = j-1
            else:
                i = i-1



    def path_generation(self, lcs_results_array, i, j, _list):
        value = 0
        if i < 0 or j < 0:
            return
        #if lcs_results_array[i][j][0] == len(base_output[i]):
        value = lcs_results_array[i][j][0]
        if self.dp.get(i-1) is not None and self.dp[i-1].get(j-1) is not None \
                and (value+self.dp[i-1][j-1] == self.dp[i][j]):
            _list.append([i, j])
            self.path_generation(lcs_results_array, i-1, j-1, _list)
        elif self.dp.get(i) is not None and self.dp[i].get(j-1) is not None and \
                self.dp[i][j-1] == self.dp[i][j]:
            _list.append([i, j-1])
            self.path_generation(lcs_results_array, i, j - 1, _list)
        elif self.dp.get(i-1) is not None and self.dp[i-1].get(j) is not None and \
                self.dp[i-1][j] == self.dp[i][j]:
            _list.append([i-1, j])
            self.path_generation(lcs_results_array, i-1, j, _list)
        return

    def sorting_based_solution(self):
        self.match_results = []
        res = 0
        f1,f2={},{}
        for i in range(0, len(self.pairs)):
            x = self.pairs[i][0]
            y = self.pairs[i][1]
            if f1.get(x) is None and f2.get(y) is None:
                f1[x],f2[y] = True, True
                self.match_results.append((x, y))
                res += self.pairs[i][2]
        return res

    def print_matched_pairs(self, base, found):
        for i in range(0, len(self.match_results)):
            print(base[self.match_results[i][0]], " , ", found[self.match_results[i][1]])



if __name__ == '__main__':
    fz = FuzzyMatch()


