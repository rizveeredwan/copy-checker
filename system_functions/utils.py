
from email.policy import default
from genericpath import isdir
import subprocess
import csv 
import os
import json

import platform

import zipfile
import shutil 

# Get the operating system name
def getos():
    os_name = platform.system()
    return os_name



def common_lib_installer(lib_name):
    try:
        status = subprocess.run(['pip', 'install', lib_name])
        assert(status.returncode == 0) 
    except Exception as e:
        print(e) 
    

try:
    import psutil 
except Exception as e:
    common_lib_installer('psutil')

try:
    # Create a new SHA-256 hash object
    import hashlib
except Exception as e:
    common_lib_installer('hashlib')


def is_process_running(pid):
    try:
        process = psutil.Process(pid)
        # Accessing any information about the process will raise an exception
        # if the process does not exist (i.e., it is not running).
        # print("Process status", process.status())
        return process.status()
    except psutil.NoSuchProcess:
        return False


def conduct_simple_hashing(input_string):
    # Create a new SHA-256 hash object
    hash_object = hashlib.sha256()

    # Update the hash object with the input string
    hash_object.update(input_string.encode('utf-8'))

    # Get the hexadecimal representation of the hash
    hashed_string = hash_object.hexdigest()

    return hashed_string


def dump_selected_language_json(problem_metadata={}):
    """
    input:
        - problem_metadata : {}, a json, the keys are integer (problem_id)
    output:
        - will dump a json, representing the current selected languages (selected_lang.json)
    """
    selected_lang = {}
    problem_ids = list(problem_metadata.keys())
    for i in range(0, len(problem_ids)):
        selected_lang[problem_ids[i]] = problem_metadata[problem_ids[i]]['default_lang'] 
    # json.dumps - string like dump 
    # json.dump - file like dump 
    with open('selected_lang.json', 'w') as file:
        json.dump(selected_lang, file)
    return selected_lang 

def read_selected_language_json(file_name=os.path.join('.', 'selected_lang.json')):
    with open(file_name, 'r') as file:
        selected_lang = json.load(file)
    return selected_lang 

def update_selected_language(problem_id=1, problem_metadata={}, selected_lang_stud="java_oop"):
    """
    input:
        - problem_id : integer, for which problem I am working
        - problem_metadata: metadata for working 
        - selected_lang_stud: "java_oop", "java", "c", "c++", "python"
    output:
        - dumping the selected languages in the form of a json 
        - updating default_lang and time(sec) attribute of problem_metadata 
    """
    if problem_metadata.get(problem_id) is not None and problem_metadata[problem_id][selected_lang_stud+' time(sec)'] is not None:
        # problem id is available and this language is also allowed for this problem 
        problem_metadata[problem_id]['default_lang'] = selected_lang_stud # updated the language 
        problem_metadata[problem_id]['time(sec)'] = problem_metadata[problem_id][problem_metadata[problem_id]['default_lang']+' time(sec)'] # updated time 
        dump_selected_language_json(problem_metadata=problem_metadata) # dumping the snapshot of new selected languages 


def update_default_lang_from_selected_json(assignment_path=os.path.join('.', 'submitted_assignments', '1', 'GoogleDrive', 'Roll_9'), problem_metadata={}):
    """
    input: (Called during evaluation from assignment_evaluator.py)
        - assignment_path: base folder for eachs student 
        - problem_metadata: {}, a json to be updated 
    output:
        - updated problem_metadata 
    """
    if os.path.exists(os.path.join(assignment_path, 'selected_lang.json')):
        selected_lang = read_selected_language_json(file_name=os.path.join(assignment_path, 'selected_lang.json'))
        # keys would be string here (as expected)
        for key in selected_lang:
            problem_id = key 
            if type(problem_id) is str:
                try:
                    problem_id = int(problem_id)
                except Exception as e:
                    print("Issue in update_default_lang_from_selected_json func ", e)
            if problem_metadata.get(problem_id) is not None and problem_metadata[problem_id]['default_lang'] != selected_lang[problem_id]['default_lang']:
                problem_metadata[problem_id]['default_lang'] = selected_lang[problem_id]['default_lang']
                problem_metadata[problem_id]['time(sec)'] = problem_metadata[problem_id][problem_metadata[problem_id]['default_lang']+' time(sec)'] # updated time 
                print("Language updated for problem ", problem_id)
    else:
        print("No selected_lang.json found in the directory")
    return problem_metadata 

def read_program_metadata(problem_ids):
    """
    input
        custom_equality : true/false (string, lower case letter)
    """
    # Here problem_ids are string
    problem_metadata = {}
    for key in problem_ids:
        problem_metadata[key] = { 
            'time(sec)': 10, # default timer
            'default_lang': 'java_oop', # default language
            'matching_type': 'fuzzy', # matching type 
            'custom_equality': None, 
            'java_oop time(sec)' : 10, # default timer for one language
            'java time(sec)' : None, # default timer 
            'c time(sec)' : None, # not allowed
            'c++ time(sec)' : None, # not allowed 
            'python time(sec)' : None, # not allowed,
            'precision': 6, # default precision 
        }
    try:
        langs = ['java_oop', 'java', 'c', 'c++', 'python']
        with open('controller_metadata.csv', 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader: 
                try: # default language 
                    problem_metadata[int(row['problem_id'].strip())]['default_lang'] = row['default_lang']
                except Exception as e:
                    print(e) 
                try: # default matching type 
                    problem_metadata[int(row['problem_id'].strip())]['matching_type'] = row['matching_type']
                except Exception as e:
                    print(e) 
                try: # default custom_equality function 
                    problem_metadata[int(row['problem_id'].strip())]['custom_equality'] = row['custom_equality']
                    if problem_metadata[int(row['problem_id'].strip())]['custom_equality'].lower() == 'true': # either true or false
                        problem_metadata[int(row['problem_id'].strip())]['custom_equality'] = "true"
                    else:
                        problem_metadata[int(row['problem_id'].strip())]['custom_equality'] = "false"
                except Exception as e:
                    problem_metadata[int(row['problem_id'].strip())]['custom_equality'] = "false"
                    print(e) 
                try: # precision set
                    problem_metadata[int(row['problem_id'].strip())]['precision'] = int(row['precision'])
                except Exception as e:
                    problem_metadata[int(row['problem_id'].strip())]['precision'] = 6
                # Language specific inputs 
                for l in range(0, len(langs)):
                    try:
                        problem_metadata[int(row['problem_id'].strip())][langs[l]+' time(sec)'] = float(row[langs[l]+' time(sec)']) # upgraded to float time
                    except Exception as e:
                        problem_metadata[int(row['problem_id'].strip())][langs[l]+' time(sec)'] = None # not allowed language
                # prepare the timeout based on default_lang 
                update_selected_language(problem_id=int(row['problem_id'].strip()), problem_metadata=problem_metadata, 
                                          selected_lang_stud=problem_metadata[int(row['problem_id'].strip())]['default_lang'])                  
    except Exception as e:
        print(e)
    return problem_metadata

def find_test_case_ids(problem_id):
    #print("current directory ", os.getcwd())
    #print("what ", os.listdir())
    files = os.listdir(os.path.join('.', str(problem_id), 'resource', 'testcases'))
    # print(files)
    case_files = []
    for i in range(0, len(files)):
        if ('in' in files[i] and '.txt' in files[i]):
            t = files[i].split('.txt')[0]
            t = t.split('in')[1] 
            if t == '-1':
                continue # a custom input file 
            case_files.append(int(t))
    case_files.sort()
    return case_files

def verify_int(s):
    try:
        s = int(s)
        return s 
    except Exception as e:
        # print(e)
        pass
    return None 

def find_problem_names():
    problems = []
    folders = os.listdir('.')
    for f in range(0, len(folders)):
        if os.path.isdir(os.path.join('.', folders[f])) is True and verify_int(folders[f]) is not None: # problem directory 
            problems.append(int(folders[f])) 
    return problems

def clean_directory_removal(folder):
    files = os.listdir(folder)
    for i in range(0, len(files)):
        if os.path.isdir(os.path.join(folder, files[i])):
            clean_directory_removal(folder=os.path.join(folder, files[i]))
        else:
            os.remove(os.path.join(folder, files[i]))
    os.remove(folder)
    return 


def unzip_file(zip_path, extract_to, move_directory=False):
    # # Example usage:
    #zip_file_path = 'path/to/your/archive.zip'
    #extract_to_directory = 'path/to/extracted/files'
    # unzip_file(zip_file_path, extract_to_directory)
    try:
        shutil.rmtree(extract_to)
    except Exception as e:
        print(e)
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    else:
        print(f"{zip_path} does not exists")
    if move_directory is True:
        entities = os.listdir(extract_to)
        if len(entities) == 1 and os.path.isdir(os.path.join(extract_to, entities[0])):
            files = os.listdir(os.path.join(extract_to, entities[0]))
            path_of_files = []
            for i in range(0, len(files)):
                os.rename(src=os.path.join(extract_to, entities[0], files[i]), dst=os.path.join(extract_to, files[i]))
                path_of_files.append(os.path.join(extract_to, files[i]))
            try:
                shutil.rmtree(os.path.join(extract_to, entities[0])) # it should be a single folder, that should be removed  
            except Exception as e:
                print(e)
            return path_of_files 
    return []


def read_csv_file_for_result_acc(path, testcase=1):
    if os.path.exists(path) is False:
        print(f"no valid output.csv found for {path}")
        return 0.0 
    accurate = 0
    total = testcase
    with open(path, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            value = row['score']
            # print("value ", value, type(value))
            accurate += float(value)
    return round((accurate*100.0)/total,2)

def result_accumulation():
    print("Without Running the judge first, the score will not be calculated properly")
    f = open(os.path.join('.', 'evaluation_score.csv'), 'w', newline='\n')
    csv_writer = csv.writer(f)
    try:
        folders = find_problem_names()
        for i in range(0, len(folders)):
            folders[i] = str(folders[i])
        temp1 = []
        temp2 = []
        for f in range(0, len(folders)):
            # print("f ", folders[f])
            # test case count finding 
            testcase = len(os.listdir(os.path.join('.', folders[f], 'resource', 'testcases')))
            data_file = os.path.join('.', folders[f], 'resource', 'statistics', 'output.csv') 
            if os.path.exists(data_file) is True:
                score = read_csv_file_for_result_acc(path= os.path.join('.', folders[f], 'resource', 'statistics', 'output.csv'), testcase=testcase)
                temp1.append(folders[f])
                temp2.append(score)
            else:
                print("Result file is not prepared. Please run the judge first") 
        csv_writer.writerow(temp1)
        csv_writer.writerow(temp2) 
        print("Result stored in evaluation_score.csv. Can be found in root directory")
    except Exception as e:
        print(e)


def extract_int_portion(string_name):
    """
    input:
        - string_name, a given string
    output:
        - an integer conversion, segement (Roll_09 -> 9)
    """
    val = 0 
    for i in range(0, len(string_name)):
        try:
            t = int(string_name[i])
            val = val * 10 + t 
        except Exception as e:
            pass 
    return val

def add_local_script_to_run_asst(problem_folder="", problem_id=1, problem_metadata={}):
    """
    input:
    output:
        - A local script file in the folder 
    """
    # path linking should always be from the root directory 
    # adding a script to run a specific problem locally, in the form of a script 
    f = open(os.path.join(problem_folder,'run_solution.sh'), 'w')
    f.write('#!/bin/bash\n\n')
    f.write("# Compilation script for the program\n")
    default_lang = "java_oop"
    if problem_metadata.get(problem_id) is not None and problem_metadata.get(problem_id).get("default_lang") is not None:
        default_lang = problem_metadata.get(problem_id).get("default_lang")
    if default_lang in ["java", 'java_oop']:
         if os.path.exists(os.path.join(problem_folder)):
            text1 = "javac"
            files2 = None 
            if os.path.exists(os.path.join(problem_folder, "solution")):
                files1 = os.listdir(os.path.join(problem_folder, "solution"))
            if os.path.exists(os.path.join(problem_folder, "generic_module")): # For simplicity of the system, developed as such
                files2 = os.listdir(os.path.join(problem_folder, "generic_module"))
            if len(files1) > 0:
                for i in range(0, len(files1)):
                    if files1[i].endswith('.java'):
                        text1 += " " + os.path.join('.', 'solution', files1[i])
            if files2 is not None and len(files2) > 0:
                for i in range(0, len(files2)):
                    if files2[i].endswith('.java'):
                        text1 += " " + os.path.join('.', 'solution', files2[i])

            single_line_comp_command = 'if ' + 'javac ' + os.path.join('solution', '*.java') + " " + os.path.join('generic_module', "*.java") + "; then\n"
            single_line_comp_command += 'fi\n\n'
            text2 = "java solution.Problem" 
            f.write(text1+"\n\n\n"+single_line_comp_command + text2)
    if default_lang in ["c", "c++"]: # As c and c++ both can be compiled with g++, choosing that, minimum requirement from g++, expected to have the latest version there
        text1 = 'g++'
        if 'ubuntu' in getos().lower():
            ff = "Problem.out"
        elif 'windows' in getos().lower():
            ff = "Problem.exe"
        text1 = text1 + " -o " + os.path.join("solution", ff)
        if os.path.exists(os.path.join(problem_folder, "solution")):
                files1 = os.listdir(os.path.join(problem_folder, "solution"))
        if len(files1) > 0:
                for i in range(0, len(files1)):
                    if files1[i].endswith('.c') or files1[i].endswith('.cpp'):
                        text1 += " " + os.path.join('.', 'solution', files1[i])
        text2 = os.path.join('.', 'solution', ff)
        f.write(text1+"\n"+text2)
    if default_lang in ['python']:
        mid_ware = ""
        if 'windows' in getos():
            mid_ware = "Scripts"
        elif 'ubuntu' in getos():
            mid_ware = "bin"
        text1 = os.path.join('jenv', mid_ware, 'python') + " " + os.path.join('solution', 'Problem.py')   
        text2 = os.path.join('python') + " " + os.path.join('solution', 'Problem.py')
        text3 = os.path.join('python3') + " " + os.path.join('solution', 'Problem.py')
        c1 = "if " + text1 + " ; then\n" 
        c1 += 'elif ' + text2 + " ; then\n" 
        c1 += 'elif ' + text3 + " ; then\n" 
        c1 += 'fi'
        f.write(c1+'\n')

def submission_format_checker(assignment_path ="Roll_1/", problem_id_list=[1, 2, 3, 4], problem_metadata={}):
    """
    input:
        - assignment_path: root one 
        - problem_id_list: all should be integers 
        - problem_metadata: json file, keys should be integer 
    output:
        - will check if I have a solution folder or not for each problem    
    """
    # check solution folder 
    exts = ['.java', '.c', '.cpp', '.py'] # allowing for any kind of python file
    verdict = True 
    for i in range(0, len(problem_id_list)):
        if os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution')):
            if problem_metadata.get(problem_id_list[i]) is not None and problem_metadata.get(problem_id_list[i]).get('default_lang') is not None:
                if 'java' in problem_metadata.get(problem_id_list[i]).get('default_lang') or 'java_oop' in problem_metadata.get(problem_id_list[i]).get('default_lang'):
                    verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution', 'Problem.java'))
                if 'c' in problem_metadata.get(problem_id_list[i]).get('default_lang'):
                    verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution', 'Problem.c'))
                if 'c++' in problem_metadata.get(problem_id_list[i]).get('default_lang'):
                    verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution', 'Problem.cpp'))
                if 'python' in problem_metadata.get(problem_id_list[i]).get('default_lang'):
                    verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution', 'Problem.py'))
            else:
                for j in range(0, len(exts)):
                    if os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'solution', 'Problem'+exts[j])):
                        verdict = verdict & True 
        else:
            verdict = verdict & False 
        verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'resource'))
        options = ['student', 'teacher', 'testcases']
        for opt in options:
            verdict = verdict & os.path.exists(os.path.join(assignment_path, str(problem_id_list[i]), 'resource', opt))
    return verdict 



def read_basic_file(file_path=""):
    """
    input:
        - file_path: a complete path 
    output:
        - code_lines, a list of lines, space removed 
    """
    lines = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            l = lines[i].strip().split()
            l = " ".join(l)
            l = l.strip() 
            if len(l) > 0:
                lines.append(l) 
    return lines  

def read_raw_file_data(file_path=""):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            lines = f.readlines()
            f_string = ""
            for i in range(0, len(lines)):
                f_string = f_string + lines[i] # a new line \n will automatically be added if found 
            return f_string
    return ""

def get_actual_python_version():
    if 'windows' in getos().lower():
        lib_folder_name = "Scripts"
    else:
        lib_folder_name = "bin" 
    venv_python_path = os.path.join('.', 'jenv', lib_folder_name, 'python')
    options = [venv_python_path, 'python', 'python3', 'python2']
    for i in range(0, len(options)):
        try:
            status = subprocess.run([options[i], '--version'], check=True, text=True, capture_output=True) 
            if status.returncode == 0:
                return options[i] 
        except Exception as e:
            # print("Issue in python finding module ", e)
            pass 
    return None 