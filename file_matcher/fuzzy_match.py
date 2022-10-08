from file_matcher.file_read import FileRead
from file_matcher.lcs import LCS


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
            print("i = ",i)
            for j in range(0, len(lcs_print_array[i])):
                print(lcs_print_array[i][j][0])

    def space_removal(self, line):
        line = line.replace('\t', " ")
        l = line.strip().split(' ')
        line = " ".join([i for i in l if i != " "])
        line = line.strip()
        return line

    def process(self, f1, f2):
        # f1, f2 are file paths
        # reading files
        base_output = self.fr_module.read_file(file_name=f1)
        found_output = self.fr_module.read_file(file_name=f2)

        # space balance
        save = []
        for i in range(0, len(found_output)):
            s = self.space_removal(found_output[i])
            if len(s) > 0:
                save.append(s)
        found_output = save

        #print("base_ouput ", base_output)
        #print("found_output ",found_output)

        # compute LCS (n^2)
        lcs_results_array = []
        for i in range(0, len(base_output)):
            lcs_results_array.append([])
            for j in range(0, len(found_output)):
                lcs_results_array[-1].append(0)
        for i in range(0, len(base_output)):
            for j in range(0, len(found_output)):
                res = self.lcs_module.begin_matching(M=base_output[i], N=found_output[j])
                arr = self.lcs_module.return_copy_of_dp()
                lcs_results_array[i][j] = [res, arr]
                # print(base_output[i], found_output[j], res)
                # input("give value ")
        # print(lcs_results_array)
        self.memory_clear()
        res = self.best_matching(lcs_results_array=lcs_results_array, i=len(base_output)-1, j=len(found_output)-1,
                                 base_output=base_output)
        # print("res = ",res)
        #self.print_arr(lcs_results_array)

        if res == len(base_output) and base_output == found_output:
            verdict = 'complete_match'
        elif res == len(base_output):
            verdict = 'partial_match'
            """
            _list = []
            self.path_generation(lcs_results_array=lcs_results_array, i=len(base_output)-1, j=len(found_output)-1,
                                 base_output=base_output, _list=_list)
            print(_list)
            """
        else:
            verdict = 'error'
        # print("verdict ",verdict)
        return verdict

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

    def best_matching(self, lcs_results_array, i, j, base_output):
        if i < 0 or j < 0:
            return 0
        if self.dp.get(i) is not None and self.dp[i].get(j) is not None:
            return self.dp[i][j]
        value = 0
        if lcs_results_array[i][j][0] == len(base_output[i]):
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
