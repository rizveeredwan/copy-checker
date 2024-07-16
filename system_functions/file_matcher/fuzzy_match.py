import sys
import re

from system_functions.file_matcher.file_read import FileRead
from system_functions.file_matcher.lcs import LCS


class FuzzyMatch:
    def __init__(self):
        self.fr_module = FileRead()
        self.lcs_module = LCS()
        self.dp = {}

    def print_lines(self, lines):
        for i in range(0, len(lines)):
            print(lines[i])

    def print_arr(self, lcs_print_array):
        for i in range(0, len(lcs_print_array)):
            for j in range(0, len(lcs_print_array[i])):
                print(lcs_print_array[i][j][0])

    def space_removal(self, line):
        line = line.replace('\t', " ")
        l = line.strip().split(' ')
        line = " ".join([i for i in l if i != " "])
        line = line.strip()
        return line
    
    def character_count(self, _list):
        tot = 0
        for i in range(0, len(_list)):
            tot += len(_list[i])
        return tot
    
    def apply_precision(self, _list=[], precision=7):
        pattern = r'\b(?:\d+\.\d*|\.\d+|\d+)\b'
        for i in range(0, len(_list)):
            input_string = _list[i]
            # Find all matches and their positions
            matches = [(match.group(), match.start(), match.end()) for match in re.finditer(pattern, input_string)]
            # Replace each match with the replacement value
            for match, start, end in matches:
                replacement = "" 
                try:
                    replacement = float(match)
                    replacement = round(replacement, precision)
                    replacement = str(replacement) 
                except Exception as e:
                    print(e)
                input_string = input_string[:start] + replacement + input_string[end:]
                _list[i] = input_string 
        return _list 

    def process(self, f1, f2, matching_type="fuzzy", precision=6):
        assert(matching_type in ['exact', 'fuzzy'])
        # f1, f2 are file paths
        # reading files
        base_output = self.fr_module.read_file(file_name=f1, matching_type=matching_type)
        found_output = self.fr_module.read_file(file_name=f2, matching_type=matching_type)

        # space balance
        save = []
        for i in range(0, len(found_output)):
            if matching_type == "fuzzy":
                s = self.space_removal(found_output[i])
            else:
                s = found_output[i]
            if len(s) > 0:
                save.append(s)
        found_output = save

        #print("base_ouput ", base_output)
        #print("found_output ",found_output)
        if matching_type == "exact":
            base_output = self.apply_precision(_list=base_output, precision=precision)
            found_output =  self.apply_precision(_list=found_output, precision=precision)
            # print("base found ", base_output, found_output)
            score = self.exact_line_by_line_match(base_ouput=base_output, found_output=found_output) 
            return score
        elif matching_type == "fuzzy":
            # compute LCS (n^2)
            lcs_results_array = []
            for i in range(0, len(base_output)):
                lcs_results_array.append([])
                for j in range(0, len(found_output)):
                    lcs_results_array[-1].append(0)
            for i in range(0, len(base_output)):
                for j in range(0, len(found_output)):
                    try:
                        res = self.lcs_module.begin_matching(M=base_output[i], N=found_output[j])
                        arr = self.lcs_module.return_copy_of_dp()
                        lcs_results_array[i][j] = [res, arr] 
                    except Exception as e:
                        print(e)
                        lcs_results_array[i][j] = [0.0, None] 
                    
                # print(base_output[i], found_output[j], res)
                # input("give value ")
            self.memory_clear()
            res = 0
            try:
                res = self.best_matching(lcs_results_array=lcs_results_array, i=len(base_output)-1, j=len(found_output)-1, 
                                    base_output=base_output)
                """
                _list = []
                self.path_generation(lcs_results_array=lcs_results_array, i=len(base_output)-1, j=len(found_output)-1,
                                    base_output=base_output, _list=_list)
                print(_list)
                """
            except Exception as e:
                print(e)
            
            if res == len(base_output):
                # full expected output has been found 
                tot_base = self.character_count(_list=base_output)
                tot_found = self.character_count(_list=found_output)
                # complete character match 
                if tot_base == tot_found:
                    return 1.0 
                # complete character match + extra characters 
                if tot_base < tot_found:
                    return 1.0 - (tot_found-tot_base)/tot_found 
            else:
                # all the lines are not found 
                return res/(1.0 * len(base_output)) # partial scoring 

    def memory_clear(self):
        self.dp.clear()

    def path_generation(self, lcs_results_array, i, j, base_output, _list):
        value = 0
        if i < 0 or j < 0:
            return
        if lcs_results_array[i][j][0] == len(base_output[i]):
            value = 1
        if self.dp.get(i-1) is not None and self.dp[i-1].get(j-1) is not None \
                and (value+self.dp[i-1][j-1] == self.dp[i][j]):
            _list.append([i, j])
        elif self.dp.get(i) is not None and self.dp[i].get(j-1) is not None and \
                self.dp[i][j-1] == self.dp[i][j]:
            _list.append([i, j-1])
        elif self.dp.get(i-1) is not None and self.dp[i-1].get(j) is not None and \
                self.dp[i-1][j] == self.dp[i][j]:
            _list.append([i-1, j])
        return
    
    def exact_line_by_line_match(self, base_ouput, found_output):
        if len(base_ouput) != len(found_output):
            return 0 
        i = 0
        while i < len(base_ouput):
            if i < len(found_output) and base_ouput[i] == found_output[i]:
                i += 1 
            else:
                return 0.0 # 0 score  
        return 1.0   

    def best_matching(self, lcs_results_array, i, j, base_output):
        if i < 0 or j < 0:
            return 0
        if self.dp.get(i) is not None and self.dp[i].get(j) is not None:
            return self.dp[i][j]
        value = 0
        if lcs_results_array[i][j][0] == len(base_output[i]): # full text found in this line of base output
            value = 1
        res1 = value + self.best_matching(lcs_results_array, i - 1, j - 1, base_output)
        res2 = self.best_matching(lcs_results_array, i, j - 1, base_output)
        res3 = self.best_matching(lcs_results_array, i - 1, j, base_output)
        if self.dp.get(i) is None:
            self.dp[i] = {}
        if self.dp[i].get(j) is None:
            self.dp[i][j] = 0
        self.dp[i][j] = max(max(res1, res2), res3)
        return self.dp[i][j]

if __name__ == '__main__':
    in_file_path = ""
    out_file_path = ""
    matching_type = "fuzzy"
    try:
        in_file_path = sys.argv[0] 
    except Exception as e:
        print(e)
    
    try:
        out_file_path = sys.argv[1] 
    except Exception as e:
        print(e)

    try:
        matching_type  = sys.argv[2] 
    except Exception as e:
        print(e)
    try:
        precision  = sys.argv[3] 
        if type(precision) is str:
            precision = int(precision) 
        print("precision ", precision)
    except Exception as e:
        print("Issue in setting precision ", e)
        precision = 6 

    fm = FuzzyMatch()
    fm.process(f1=in_file_path, f2=out_file_path, matching_type=matching_type, precision=precision)


