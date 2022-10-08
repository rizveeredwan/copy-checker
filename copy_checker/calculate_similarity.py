import csv
import json
import os
import copy

from copy_checker.code_normalization import CodeNormalization
from copy_checker.fuzzy_match import FuzzyMatch


class CalculateSimilarity:
    def __init__(self):
        self.data = {}  # id: 1 : []
        self.data_var_normalized = {} # all the variables are replaced
        self.code_n = CodeNormalization()
        self.f_m = FuzzyMatch()
        self.suspicious = {}

    def number_of_text(self, lines):
        ct = 0
        for i in range(0, len(lines)):
            ct = ct + len(lines[i])
        return ct

    def execute_matching(self, threshold=0.8, alpha=0.7, A=None, B=None, print_flag=False):
        try:
            if os.path.exists(A) and os.path.exists(B):
                _listA_var_non_normalized = self.code_n.normalize(code_file=A, var_normalization_flag=False)
                _listA_var_normalized = self.code_n.normalize(code_file=A, var_normalization_flag=True)
                ctA_var_non_normalized = max(1.0, self.number_of_text(lines=_listA_var_non_normalized)) * 1.0
                ctA_var_normalized = max(1.0, self.number_of_text(lines=_listA_var_normalized)) * 1.0

                _listB_var_non_normalized = self.code_n.normalize(code_file=B, var_normalization_flag=False)
                _listB_var_normalized = self.code_n.normalize(code_file=B, var_normalization_flag=True)
                ctB_var_non_normalized = max(1.0, self.number_of_text(lines=_listB_var_non_normalized)) * 1.0
                ctB_var_normalized = max(1.0, self.number_of_text(lines=_listB_var_normalized)) * 1.0
            else:
                raise Exception("file not found error")
            res1 = self.f_m.process(base_output=_listA_var_non_normalized, found_output=_listB_var_non_normalized)
            pairs1 = copy.deepcopy(self.f_m.match_results)
            res2 = self.f_m.process(base_output=_listA_var_normalized, found_output=_listB_var_normalized)
            pairs2 = copy.deepcopy(self.f_m.match_results)

            score1 = alpha * (res1 / ctA_var_non_normalized) + (1 - alpha) * (res2 / ctA_var_normalized)  # 0.5 * normal + 0.5 * variable normalization dp match
            score2 = alpha * (res2 / ctB_var_non_normalized) + (1 - alpha) * (res2 / ctB_var_normalized)

            if score1 >= threshold and score2 >= threshold:  # res/ct1 >= 0.97 and res/ct2 >= 0.97
                print("Suspicious code detected ", 'S_A = ', score1, 'S_B = ', score2)
                if print_flag is True:
                    self.print_pairs(f=os.path.join('.', 'variable_non_normalized_matching.txt'), A=_listA_var_non_normalized,
                                     B=_listB_var_non_normalized, match_results=pairs1)
                    self.print_pairs(f=os.path.join('.', 'variable_normalized_matching.txt'),
                                     A=_listA_var_normalized,
                                     B=_listB_var_normalized, match_results=pairs2)
            else:
                print("No suspicion")
        except Exception as e:
            print(e)

    def print_pairs(self, f, A, B, match_results):
        with open(f, 'w', encoding='utf-8', errors='ignore') as w:
            for i in range(0, len(match_results)):
                w.write(str(match_results[i][0])+A[match_results[i][0]] + " , "
                        + str(match_results[i][1])+B[match_results[i][1]]+'\n')
            return


if __name__ == '__main__':
    obj = CalculateSimilarity
    # A Test Code Fragment
    obj.execute_matching(threshold=0.8, alpha=0.7, A=None, B=None, print_flag=False)
