class LCS:
    def __init__(self):
        self.dp = {}
        self.path = {}

    def clear_memory(self):
        self.dp.clear()
        self.path.clear()

    def recursion(self, i, j, M, N):
        if i >= len(M) or j >= len(N):
            return 0
        if self.dp.get(i) is not None and self.dp.get(i).get(j) is not None:
            return self.dp[i][j]
        res1 = 0
        if M[i] == N[j]:
            res1 = max(res1, 1 + self.recursion(i + 1, j + 1, M, N))
            if self.path.get(i) is None:
                self.path[i] = {}
            if self.path.get(i).get(j) is None:
                self.path[i][j] = 0 # [i+1, j+1]
        else:
            res2 = self.recursion(i + 1, j, M, N)
            res3 = self.recursion(i, j + 1, M, N)
            if res2 >= res3:
                res1 = res2
                if self.path.get(i) is None:
                    self.path[i] = {}
                if self.path.get(i).get(j) is None:
                    self.path[i][j] = 1 # [i+1, j]
            else:
                res1 = res3
                if self.path.get(i) is None:
                    self.path[i] = {}
                if self.path.get(i).get(j) is None:
                    self.path[i][j] = 2 # [i, j+1]
        if self.dp.get(i) is None:
            self.dp[i] = {}
        if self.dp[i].get(j) is None:
            self.dp[i][j] = 0
        self.dp[i][j] = res1
        return self.dp[i][j]

    def get_path(self, i, j, M, N):
        if i >= len(M) or j >= len(N):
            return ""
        if self.path[i][j] == 0:
            _string = M[i]+self.get_path(i+1, j+1, M, N)
        elif self.path[i][j] == 1:
            _string = self.get_path(i + 1, j, M, N)
        elif self.path[i][j] == 2:
            _string = self.get_path(i, j+1, M, N)
        return _string

    def begin_matching(self, M, N):
        self.clear_memory()
        res = self.recursion(0, 0, M, N)
        # print(res)
        return res

    def return_path(self, M, N):
        _string = self.get_path(0, 0, M, N)
        print(_string)

    def return_copy_of_dp(self):
        arr = {}
        for key1 in self.dp:
            arr[key1] = {}
            for key2 in self.dp[key1]:
                arr[key1][key2] = self.dp[key1][key2]
        return arr


if __name__ == '__main__':
    lcs = LCS()
    print(lcs.begin_matching(M="prime", N="3 is prime"))

"""
lcs = LCS()
lcs.begin_matching(M="CECCBCCECAACABEAABBCCBCECCBCEECECAE", N="ABEACCBBACCEAEEBCABECAAAAAE")
lcs.return_path(M="CECCBCCECAACABEAABBCCBCECCBCEECECAE", N="ABEACCBBACCEAEEBCABECAAAAAE")
"""