import os
import re


class CodeNormalization:
    def __init__(self):
        self.keywords = {
            'c++': [],
        }
        self.read_keywords(file_name=os.path.join('.', 'copy_checker', 'keywords.txt'), language='c++')
        # print(self.keywords['c++'])

    def read_keywords(self, file_name, language):
        temp = ['\n', '\t']
        with open(file_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i in range(0, len(lines)):
                for t in temp:
                    lines[i] = lines[i].strip().split(t)
                    # print(lines[i], len(lines[i]))
                    if len(lines[i]) > 1:
                        break
                    lines[i] = lines[i][0]
                for j in range(0, len(lines[i])):
                    lines[i][j] = lines[i][j].strip()
                    if len(lines[i][j]) > 0:
                        self.keywords[language].append(lines[i][j])

    def _list_to_string(self, _list):
        _string = ""
        for j in range(0, len(_list)):
            if _string == "":
                _string = _list[j]
            else:
                _string = _string + " " + _list[j]
        return _string

    def keyword_removal(self, _list, code_type):
        updated_list = []
        for i in range(0, len(_list)):
            temp = _list[i].strip().split(' ')
            temp2 = []
            for j in range(0, len(temp)):
                if temp[j] not in self.keywords[code_type] and len(temp[j]) != 0:
                    temp2.append(temp[j])
            _string = self._list_to_string(temp2)
            if _string != "":
                updated_list.append(_string)
        return updated_list

    def unique_chars(self, _list):
        unk = []
        for i in range(0, len(_list)):
            if _list[i] not in unk and len(_list[i]) > 0:
                unk.append(_list[i])
        return unk

    def reduce_list_from_gaps(self, _list):  # reducing empty lines
        _list2 = []
        for i in range(0, len(_list)):
            unk = self.unique_chars(_list[i])
            if len(unk) == 0:
                continue
            _list2.append(_list[i])

    def removing_space(self, _string):
        _string2 = ""
        for i in range(0, len(_string)):
            if _string[i] != ' ' and _string[i] != '\t':
                _string2 = _string2 + _string[i]
        return _string2

    def split_line_by_delimiter(self, _list, sym):
        _list2 = []
        for i in range(0, len(_list)):
            temp = _list[i].split(sym)
            for j in range(0, len(temp)):
                temp[j] = self.removing_space(_string=temp[j])
                unk = self.unique_chars(temp[j])
                if len(unk) == 0:
                    continue
                _list2.append(temp[j])
        return _list2

    def remove_empty_lines(self, lines):
        _list2 = []
        for i in range(0, len(lines)):
            lines[i] = lines[i].strip()
            if len(self.unique_chars(lines[i])) > 0:
                _list2.append(lines[i])
        return _list2

    def finding_only_bracket(self, lines, i, flag):
        # not complete
        for j in range(0, len(lines[i])):
            if lines[i][j] == flag:
                return True
        else:
            return False

    def identifying_condition_portion(self, lines, i):
        # [for, while, if ]
        sp = ['for', 'while', 'if', 'elseif']
        condition_ended = None
        lines[i] = lines[i].strip()
        for s in sp:
            patt = s + "\s*\("
            idx1 = re.search(patt, lines[i])
            if idx1 is not None:  # for( or #for (, identified,
                # print(s, idx1, lines[i])
                st = idx1.span()[0]
                en = idx1.span()[1] - 1
                stack = []
                for j in range(i, len(lines)):
                    # print(lines[j], stack)
                    for k in range(en, len(lines[j])):
                        if lines[j][k] == '(':
                            stack.append('(')
                        elif lines[j][k] == ')' and len(stack) > 0:
                            stack.pop()
                        if len(stack) == 0:
                            condition_ended = j
                            return condition_ended, k
                    else:
                        en = 0  # next start
                break
        return None, None

    def adding_second_bracket_blocks(self, lines):
        for i in range(0, len(lines)):
            lines[i] = lines[i].strip()
        i = 0
        stat = []
        while i < len(lines):
            sp_block_verdict, pos = self.identifying_condition_portion(lines, i)
            if sp_block_verdict is None:
                if lines[i] == 'else':
                    sp_block_verdict = i
                    pos = 3
            # print(lines[i], sp_block_verdict)
            if sp_block_verdict is None:
                # no key word detected
                if len(stat) > 0:
                    if stat[-1][1] == 0:  # normal
                        if lines[i][0] == '}':
                            stat.pop()  # balance paranthesis
                            i = i + 1
                        else:
                            i = i + 1  # need to balance it first
                    else:  # abnormal
                        while len(stat) > 0 and stat[-1][1] == 1:
                            i = i + 1
                            lines.insert(i, '}')
                            stat.pop()
                            if i + 1 < len(lines) and len(lines[i + 1]) >= 4 and lines[i+1][0:4] == 'else':
                                i = i + 1
                                break
                else:
                    i = i + 1
            else:  # block detected
                # print("sp_block_verdict ",sp_block_verdict, lines[i])
                i = sp_block_verdict
                if len(lines[i]) - 1 > pos:  # other characters in the same line, separating a line
                    nl = lines[i][pos + 1:]
                    lines.insert(i + 1, nl)  # [for, cout]
                    lines.insert(i + 1, '{')  # [for, {, cout
                    stat.append(['{', 1])
                    lines[i] = lines[i][0:pos + 1]
                    i = i + 2
                    continue
                if i + 1 < len(lines) and self.finding_only_bracket(lines, i + 1, '{') is True:  # bracket is found
                    i = i + 1
                    stat.append(['{', 0])  # normal
                    i = i + 1
                else:
                    lines.insert(i + 1, '{')
                    i = i + 1
                    stat.append(['{', 1])  # abnormal
                    i = i + 1
        return lines

    def one_liner_removal_simpler(self, x):
        x = x.replace('\t', ' ')
        x = x.strip()
        x = x.split(' ')
        sp_keys = ['for', 'while', 'if', 'else']
        for i in range(0, len(x)):
            if x[i] in sp_keys or x[i][0:-1] in sp_keys:  # for vs for(
                if (i - 1) > 0:
                    if x[i - 1] == 'else' and x[i] == 'if':
                        continue
                    x[i] = '\n' + x[i]
        x = " ".join(x)
        return x

    def else_replace(self, x):
        x = x.replace('\t', ' ')  # tab -> space
        words = x.strip().split(' ')
        for i in range(0, len(words)):
            if words[i] == 'else':
                if i+1 < len(words) and len(words[i+1])>=2 and words[i + 1][0:2] == 'if':
                    continue
                words[i] = 'else' + " \n"
        x = " ".join([i for i in words])
        x = x.strip()
        return x

    def extra_new_line_addition(self, x):
        x = x.replace('{', "\n" + '{' + "\n")
        x = x.replace('}', "\n" + '}' + "\n")
        x = x.replace(';', ';' + "\n")
        x = x.replace(',', ';' + "\n")
        # x = x.replace('else', 'else' + "\n")
        # x = re.sub(r'\belse\b', 'else' + "\n",x)
        x = self.else_replace(x)
        operators = ['&&', '||']
        for op in operators:
            x = x.replace(op, " \n " + op)
        # extra newline after some keywords
        x = self.one_liner_removal_simpler(x)
        return x



    def variable_normalization(self, line, language, variable_save={}):
        operator = ['<', '>', ',', ';', ':', '(', ')', '{', '}', '[', ']', '=', '+', '-', '*', '/',
                    '%', '**', '^', '|', '&', '&&', '||', '.', '->', '#', ';', '\n', '\t', '"', "'"]
        if language in ['c++', 'c']:
            for op in range(0, len(operator)):
                line = line.replace(operator[op], " " + operator[op] + " ")
        line = line.strip().split(' ')
        # print("line = ", line)
        i = 0
        last_keyword_identified = False
        special_types = ['int', 'float', 'double', 'string', 'char', 'void', 'define', 'bool', 'class', 'struct',
                         'pair', 'priority_queue', 'queue', 'stack ', 'long long int', 'long long', 'unsigned']
        while i < len(line):
            if line[i] in special_types:
                last_keyword_identified = True
            else:
                if last_keyword_identified is True:
                    # print(last_keyword_identified, line[i], len(line[i]))
                    if re.search('^[a-zA-Z_$][a-zA-Z_$0-9]*$', line[i]) is not None and line[i] not in special_types and \
                            line[i] not in self.keywords[language]:
                        variable_save[line[i]] = True
                        line[i] = 'VAR'
                    if line[i] == ';':
                        # last_keyword_identified = False
                        pass
                else:
                    if variable_save.get(line[i]) is not None:  # already as a variable detected
                        line[i] = 'VAR'
                    elif re.search('^[a-zA-Z_$][a-zA-Z_$0-9]*$', line[i]) is not None and \
                            line[i] not in special_types and line[i] not in self.keywords[language]:
                        if '"' not in line:
                            if line[i] == 'using':
                                print("oh no ", self.keywords[language])
                            variable_save[line[i]] = True # int var \n b -> int var \n var
                            line[i] = 'VAR'
            i = i + 1
        text = " ".join(i for i in line)
        text = text.strip()
        return text

    def comment_removal(self, lines):
        i = 0
        comment_found = False
        new_lines = []
        while i < len(lines):
            if '/*' in lines[i]:
                comment_found = True
                i = i + 1
                continue
            elif '*/' in lines[i] and comment_found is True:
                comment_found = False
                i = i + 1
                continue
            if comment_found is False:
                new_lines.append(lines[i])
            i = i + 1
        lines = new_lines
        i = 0
        new_lines2 = []
        while i < len(lines):
            idx = lines[i].find("//")
            if idx != -1:
                # print("idx ", idx)
                _str = ""
                unique_found = False
                for j in range(0, len(lines[i])):
                    if j == idx:
                        break
                    _str = _str + lines[i][j]
                    if lines[i][j] not in ['\n', '\t', ';', ' ']:
                        unique_found = True
                if unique_found is True:
                    new_lines2.append(_str)
            else:
                new_lines2.append(lines[i])
            i = i + 1
        lines = new_lines2
        return lines

    def reducing_lines(self, lines):
        lines2 = []
        operator = ['>', ',', ';', ':', ')', ']', '=', '+', '-', '*', '/',
                    '%', '**', '^', '|', '&', '&&', '||', '.', '->', '#', ';', '\n', '\t', '"', "'"]
        for i in range(0, len(lines)):
            lines[i] = lines[i].strip()
            if len(lines[i])>0 and lines[i][0] in operator:
                if len(lines2) > 0:
                    lines2[-1] = lines2[-1]+" "+lines[i]
                else:
                    lines2.append(lines[i])
            elif len(lines[i])>0:
                lines2.append(lines[i])
        return lines2

    def identify_blocks(self, lines):
        # not complete
        blocks = []
        block_id = -1
        line_allow = None  # None, inf, 1
        line_count = 0  # boundary checking
        for i in range(0, len(lines)):
            if line_allow is None:
                block_id += 1
                line_count = 1
            if line_allow == 'inf':
                line_count += 1
            if line_allow == 1:
                pass
            blocks.append(block_id)
            if (i + 1) < len(lines) and lines[i + 1] == '{':
                line_allow = 'inf'  # infinity line allowed
                line_count = 1

    def header_file_related_issues(self, line):
        if len(line)>0:
            patterns = ["#[\s]*include[\s]*<", '#[\s]*define[\s]+', 'typedef', 'template[\s]*<']
            for patt in patterns:
                x = re.search(patt, line)
                if x:
                    # (line, patt)
                    return True # problem
        return False # No problem

    def redundant_line_broken_merge(self, lines):
        lines2 = []
        for i in range(0, len(lines)):
            lines[i] = lines[i].strip()
            if len(lines2) > 0 and lines2[-1][-1] != ';' and \
                    self.header_file_related_issues(line=lines2[-1]) is False: # a \n + b;
                lines2[-1] = lines2[-1] + " " + lines[i]
            elif len(lines[i]) > 0:
                lines2.append(lines[i])
        return lines2

    def normalize(self, code_file, language='c++', var_normalization_flag=False):
        with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            lines = self.comment_removal(lines=lines)
            # redundant line break removal
            lines = self.redundant_line_broken_merge(lines=lines)
            variable_save = {}
            lines = self.remove_empty_lines(lines)  # removing empty lines
            for i in range(0, len(lines)):
                # print("before1 = ", lines[i])
                lines[i] = self.extra_new_line_addition(lines[i])
                if var_normalization_flag is True:
                    # print("before = ", lines[i])
                    lines[i] = self.variable_normalization(line=lines[i], language=language,
                                                           variable_save=variable_save)
                    # print("after = ", lines[i])
            # print('pre = \n', lines)
        _list_of_delim = ['\n', '\t', ';', ',']
        for i in range(0, len(_list_of_delim)):
            # line strip
            lines = self.split_line_by_delimiter(_list=lines, sym=_list_of_delim[i])
            # print('\n',lines)
        self.adding_second_bracket_blocks(lines)
        # reducing lines count, e.g. b,+a changing to b+a
        lines = self.reducing_lines(lines)
        # print('final = \n', lines)
        return lines


if __name__ == '__main__':
    obj = CodeNormalization()
    out = obj.normalize(code_file=os.path.join('.', 'copy_checker', 'examples', 'simple_code.cpp'),
                  var_normalization_flag=True)
    print(out)
    # print(obj.split_line_by_delimiter(_))
