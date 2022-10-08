import os
print(os.getcwd())
print(os.path.exists('file_matcher'))
from file_matcher.lcs import LCS


class FuzzyMatch:
    def __init__(self):
        self.lcs_module = LCS()
        self.dp = {}
        self.lcs_results_array = []
        self.pairs = []
        self.match_results = []

    def print_lines(self, lines):
        for i in range(0, len(lines)):
            print(lines[i])

    def print_arr(self, lcs_print_array):
        for i in range(0, len(lcs_print_array)):
            # print("i = ",i)
            for j in range(0, len(lcs_print_array[i])):
                print(lcs_print_array[i][j][0])

    def process(self, base_output, found_output):
        # compute LCS (n^2)
        self.lcs_results_array.clear()
        self.pairs.clear()
        for i in range(0, len(base_output)):
            self.lcs_results_array.append([])
            for j in range(0, len(found_output)):
                self.lcs_results_array[-1].append(0)
        for i in range(0, len(base_output)):
            best_save, best_idx = -1, -1
            for j in range(0, len(found_output)):
                res = self.lcs_module.begin_matching(M=base_output[i], N=found_output[j])
                arr = self.lcs_module.return_copy_of_dp()
                self.lcs_results_array[i][j] = [res, arr]
                self.pairs.append([i, j, res])
                if best_save < res:
                    best_save = res
                    best_idx = j
            #print(base_output[i], found_output[best_idx], best_save, best_idx, len(base_output[i]))
                # input("give value ")
        # print(lcs_results_array)
        self.memory_clear()
        """
        res = self.best_matching(lcs_results_array=self.lcs_results_array, i=len(base_output)-1, j=len(found_output)-1,
                                 base_output=base_output)
        """
        res = self.sorting_based_solution()
        # print("verdict ",verdict)
        return res

    def memory_clear(self):
        self.dp.clear()

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

    def best_matching(self, lcs_results_array, i, j, base_output):
        if i < 0 or j < 0:
            return 0
        if self.dp.get(i) is not None and self.dp[i].get(j) is not None:
            return self.dp[i][j]
        res1 = lcs_results_array[i][j][0] + self.best_matching(lcs_results_array, i - 1, j - 1, base_output)
        res2 = self.best_matching(lcs_results_array, i, j - 1, base_output)
        res3 = self.best_matching(lcs_results_array, i - 1, j, base_output)
        if self.dp.get(i) is None:
            self.dp[i] = {}
        if self.dp[i].get(j) is None:
            self.dp[i][j] = 0
        self.dp[i][j] = max(max(res1, res2), res3)
        return self.dp[i][j]

    def sorting_based_solution(self):
        self.pairs.sort(key=lambda x: x[2], reverse=True)
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


