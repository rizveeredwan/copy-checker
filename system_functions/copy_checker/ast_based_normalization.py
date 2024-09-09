import ast
import astor


# Step 3: Define a custom transformer class to modify the `id` attribute
class IDTransformer(ast.NodeTransformer):
    def visit_Name(self, node):
        # Change the id to 'VAR'
        node.id = 'VAR'
        return node

    def visit_FunctionDef(self, node):
        # Replace the function name with 'FUNCTION_NAME'
        node.name = 'FUNCTION_NAME'

        # Continue visiting child nodes (such as arguments and body)
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        # Replace the function name with 'FUNCTION_NAME'
        node.name = 'CLASS_NAME'

        # Continue visiting child nodes (such as arguments and body)
        self.generic_visit(node)
        return node


def init_change_var(tree=None):
    # Step 4: Apply the transformer to the AST
    transformer = IDTransformer()
    modified_tree = transformer.visit(tree)
    return modified_tree


class CodeFromAST:
    def __init__(self):
        pass

    def code_from_ast(self, lang="python", modified_tree=None):
        generated_code = None
        try:
            if lang == "python":
                try:
                    generated_code = ast.unparse(modified_tree)
                except AttributeError:
                    import astor  # Only needed for Python 3.8 and earlier
                    generated_code = astor.to_source(modified_tree)
        except Exception as e:
            pass
        return generated_code

    def code_from_ast_py(modified_tree=None):
        # For Python 3.9+
        generated_code = None
        try:
            generated_code = ast.unparse(modified_tree)
        except AttributeError:
            import astor  # Only needed for Python 3.8 and earlier
            generated_code = astor.to_source(modified_tree)
        return generated_code


class ConstructAST:
    def __init__(self):
        pass

    def construct_ast(self, lang="python", code=""):
        tree = None
        try:
            if lang == "python":
                tree = self.construct_py_ast(code=code)
                print("tree ", ast.dump(tree))
        except Exception as e:
            pass
        return tree

    def construct_py_ast(self, code=""):
        tree = ast.parse(code)
        return tree


class AstBasedNormalization:
    def __init__(self):
        self.construct_ast_obj = ConstructAST()
        self.code_from_ast_obj = CodeFromAST()

    def make_single_string(self, lines=[]):
        temp =""
        for i in range(0, len(lines)):
            temp = temp + lines[i] + '\n'
        return temp

    def read_from_file(self, file_name=""):
        with open(file_name, 'r') as f:
            lines = f.readlines()
            return lines

    def remove_single_line_comment_for_python(self, lines=[]):
        new_lines, single_line_comments = [], []
        for i in range(0, len(lines)):
            comment = ""
            inst = ""
            flag = False
            for j in range(0, len(lines[i])):
                if lines[i][j] =='#':
                    flag = True
                    st, en, shift = [+1, -1], [len(lines[i]), -1], [1, -1] # two options: forward vs backward
                    for k in range(0, 2):
                        for l in range(j+st[k], en[k], shift[k]):
                            if lines[i][l] == "'" or lines[i][l] == '"':
                                flag = False
                                break
                    if flag:
                        inst = lines[i][0:j]
                        comment = lines[i][j:]
                        break
            if flag is False:
                inst = lines[i]
            if len(inst) > 0:
                new_lines.append(inst)
            if len(comment) > 0:
                single_line_comments.append(comment)
        return new_lines, single_line_comments

    def make_list_of_strings(self, text=""):
        print(text)
        lines = text.strip().split('\n')
        new_lines = []
        for i in range(0, len(lines)):
            t = lines[i].strip().split()
            if len(t) > 0:
                new_lines.append(lines[i])
        return new_lines

    def norm_code(self, file_name="", var_norm=True, lang="python"):
        # Step 1: File reading
        code_lines = self.read_from_file(file_name=file_name)
        print(code_lines)
        # Step 1-1: single line comment separation
        code_lines, single_line_comments = self.remove_single_line_comment_for_python(lines=code_lines)
        # Step 1-2: make single string
        temp = self.make_single_string(lines=code_lines)
        print(temp)
        tree = None
        # Step 2: Construct AST from code
        if lang == "python":
            tree = self.construct_ast_obj.construct_ast(lang='python', code=temp)
        if var_norm is True:
            try:
                modified_tree = init_change_var(tree=tree)
            except Exception as e:
                print(e)
        else:
            modified_tree = tree
        # Step 5: Convert the modified AST back to Python code
        generated_code = None
        try:
            if lang =="python":
                generated_code = self.code_from_ast_obj.code_from_ast(lang='python', modified_tree=modified_tree)
        except Exception as e:
            pass
        print(generated_code)
        rephrased_code_lines = self.make_list_of_strings(text=generated_code)
        return generated_code, rephrased_code_lines, single_line_comments


"""
def func(a, b):
    x = 3 * a + 4 * b
    return x 
"""


def read_from_file(file_name="temp.py"):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        return lines


if __name__ == '__main__':
    ast_based_conversion = AstBasedConversion()
    lines = read_from_file()
    print(lines)
    gen_code, re_lines = ast_based_conversion.norm_code(code_lines=lines, var_norm=True, lang='python')
    print(gen_code)
    print(re_lines)