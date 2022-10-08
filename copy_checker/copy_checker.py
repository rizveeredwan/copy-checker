import csv
import json
import os
import copy

from copy_checker.code_normalization import CodeNormalization
from copy_checker.fuzzy_match import FuzzyMatch


class CopyChecker:
    def __init__(self):
        self.data = {}  # id: 1 : []
        self.data_var_normalized = {} # all the variables are replaced
        self.code_n = CodeNormalization()
        self.f_m = FuzzyMatch()
        self.suspicious = {}

    def data_collect(self):
        p = os.path.join('temp_folder', 'base_dir')
        folders1 = os.listdir(p)
        for i in range(0, len(folders1)):
            _id = folders1[i]
            # suspicious stat
            self.suspicious[_id] = {}
            self.data[_id] = {}
            self.data_var_normalized[_id] = {}
            p2 = os.path.join(p, folders1[i], 'CODES')
            folders2 = os.listdir(p2)
            for j in range(0, len(folders2)):  # 1, 2, 3, 4
                p3 = os.path.join(p2, folders2[j])
                files = os.listdir(p3)
                for k in range(0, len(files)):
                    if '.c' in files[k] or '.cpp' in files[k] or '.java' in files[k]:
                        p4 = os.path.join(p3, files[k])  # cpp files
                        _list = self.code_n.normalize(code_file=p4, var_normalization_flag=False)
                        self.data[_id][folders2[j]] = _list
                        _list = self.code_n.normalize(code_file=p4, var_normalization_flag=True)
                        self.data_var_normalized[_id][folders2[j]] = _list
                        self.suspicious[_id][folders2[j]] = []
                        # print(_list)
                        # print(p4, folders2[j])
                        # print(self.data[_id][folders2[j]])
                        break

    def number_of_text(self, lines):
        ct = 0
        for i in range(0, len(lines)):
            ct = ct + len(lines[i])
        return ct

    def matching(self, threshold=0.8, alpha=0.7, asst_no=1):
        _ids = list(self.data.keys())
        print(_ids)
        count = {}
        for id in _ids:
            count[id] = [0.0, []]
        for i in range(0, len(_ids)):
            id1 = _ids[i]
            for j in range(i+1, len(_ids)):
                id2 = _ids[j]
                assert(id1, id2)
                # print(id1, id2)
                for problem in self.data[id1]:
                    if self.data[id2].get(problem) is not None:
                        print("common = ",i, j, id1, id2, problem)
                        # without variable normalization
                        res = self.f_m.process(base_output=self.data[id1][problem],
                                               found_output=self.data[id2][problem])
                        print("res ",res)
                        # with variable normalization
                        res2 = self.f_m.process(base_output=self.data_var_normalized[id1][problem],
                                               found_output=self.data_var_normalized[id2][problem])
                        ct1 = max(1.0, self.number_of_text(lines=self.data[id1][problem]))*1.0
                        ct1_var_normalized = max(1.0, self.number_of_text(lines=self.data_var_normalized[id1][problem])) * 1.0
                        ct2 = max(1.0, self.number_of_text(lines=self.data[id2][problem]))*1.0
                        ct2_var_normalized = max(1.0, self.number_of_text(lines=self.data_var_normalized[id2][problem])) * 1.0
                        print(ct1, ct2, res/ct1, res/ct2)
                        score1 = alpha * (res/ct1) + (1-alpha) * (res2/ct1_var_normalized) # 0.5 * normal + 0.5 * variable normalization dp match
                        score2 = alpha * (res / ct2) + (1-alpha) * (res2 / ct2_var_normalized)
                        if score1 >= threshold and score2 >= threshold: # res/ct1 >= 0.97 and res/ct2 >= 0.97
                            count[id1][0] = count[id1][0] + 1
                            count[id1][1].append([problem, id2])
                            count[id2][0] = count[id2][0] + 1
                            count[id2][1].append([problem, id1])
                            # suspicious codes
                            self.suspicious[id1][problem].append((id2, score1, score2))
                            self.suspicious[id2][problem].append((id1, score2, score1))
        self.write_into_file(count=count, asst_no=asst_no)

    def write_into_file(self, count, asst_no=1):
        name = 'copy_stat '+str(asst_no)+'.csv'
        with open(os.path.join('data', name), 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            for id in count:
                _list = [id, count[id][0], count[id][1]]
                csv_writer.writerow(_list)
                # Serializing json
        name = "suspicious_state "+str(asst_no)+".json"
        with open(os.path.join('data', name), "w") as outfile:
            try:
                json.dump(self.suspicious, outfile)
            except Exception as e:
                print(e)

    def normalize_and_match(self, threshold=0.8, alpha=0.7, asst_no=1):
        self.data_collect()
        self.matching(asst_no=asst_no)

    def execute_single_matching(self, threshold=0.8, alpha=0.7, A=None, B=None, print_flag=False):
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
    obj = CopyChecker()
    obj.normalize_and_match()
