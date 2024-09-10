import os 
import shutil 
import subprocess
import csv
import argparse

from system_functions.copy_checker.copy_checker import *

BASE_DIRECTORY = os.path.join('dummy_data') # where the code submissions are kept
TRACKER_FILE = os.path.join('file_status_tracker.csv') # where status will be written (how many files have been processed such information)

def remove_base(path=os.path.join('.', 'interactive_temp')):
    try:
        shutil.rmtree(path) 
    except Exception as e:
        print(e)

def create_base(path=os.path.join('.', 'interactive_temp')):
    os.mkdir(path)


def read_tracker():
    global TRACKER_FILE
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            csv_file = csv.reader(f)
            status = []
            for row in csv_file:
                status.append(row)
            return status 
    return [['filename', 'status']]


def update_tracker(status=[], file_name="ABC", verdict="YES"):
    f = False 
    for i in range(0, len(status)):
        if status[i][0] == file_name:
            status[i][2] = verdict 
            f = True 
            break 
    if f is False:
        status.append([file_name, verdict]) # this entry was never found 
    with open(TRACKER_FILE, 'r') as w:
        csv_file = csv.writer(w)
        for i in range(0, len(status)):
            csv_file.writerow(status[i])
        return csv_file 
    return status 

def return_current_status(filename="", status=[]):
    for i in range(0, len(status)):
        if status[i][0] == filename:
            if status[i][1] == "YES":
                return "YES" 
            return None 
    return None 

def process(BASE_DIRECTORY=os.path.join('dummy_data'), TRACKER_FILE=os.path.join('file_status_tracker.csv'), input_data="", output_data=""):
    # to find the quality of the code output 
    status = read_tracker()
    files = os.listdir(BASE_DIRECTORY)
    for i in range(0, len(files)):
        v = input(f"Continue with {files[i]}: ")
        cur_st = return_current_status(filename=files[i], status=status)
        if cur_st == "YES":
            print(f"Already Processed {files[i]}")
            continue 
        update_tracker(file_name=files[i], status=status, verdict="YES") 
        # now code run and work with 
        print("v ", v) 
        if v == "n":
            continue
        remove_base()
        create_base()
        # copy src 
        shutil.copy(src=os.path.join(BASE_DIRECTORY, files[i]), dst=os.path.join('.', 'interactive_temp', files[i])) 
        # compile 
        f = False 
        try:
            command = ['javac', os.path.join('.', 'interactive_temp', files[i])]
            subprocess.run(command)
            f = True 
            print("compilation done ", files[i])
        except Exception as e:
            print("Escaping COMPILATION: ", e, files[i])
        if f is True:
            curr = os.getcwd()
            os.chdir(os.path.join('.', 'interactive_temp'))
            try:
                command = ['java', files[i].split('.')[0]]
                subprocess.run(command)
            except Exception as e:
                print(e)
            except KeyboardInterrupt as e:
                print(e)
            os.chdir(curr)
        else:
            print("Escaping run: ", files[i])


def find_copy_stat(BASE_DIRECTORY = os.path.join('.', 'dummy_data'), alpha=0.7, level_threshold=1, num_threads=1, stat_file_name="output.csv"):
    # to find the copy statistics 
    files = os.listdir(BASE_DIRECTORY)
    for i in range(0, len(files)):
        files[i] = os.path.join(BASE_DIRECTORY, files[i])
        print(files[i])
    result = start_copy_checking(path_of_files=files, alpha=alpha, level_threshold=level_threshold, num_threads=num_threads)
    data = []
    header = [""]
    for i in range(0, len(files)):
        header.append(files[i])
    data.append(header)
    for i in range(0, len(files)):
        data.append([files[i]])
        for j in range(0, len(files)):
            if i == j:
                data[-1].append('-')
            else:
                data[-1].append(result[i][j][0]) # only taking similarity 
    with open(stat_file_name, 'w', errors='ignore') as w:
        csv_writer = csv.writer(w)
        csv_writer.writerows(data)
            

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Parameters")

    parser.add_argument('--op_type', '-ot', type=int, default=0, help='Operation Type')
    parser.add_argument('--base_directory', '-b', type=str, default=os.path.join('.', 'dummy_data'), help='Base Code Directory')
    parser.add_argument('--alpha', '-a', type=float, default=0.7, help='Weight Value for Matching') # weight of variable normalized and non-normalized version's matching
    parser.add_argument('--level_threshold', '-l', type=int, default=0, help='Level Threshold for Granularity') # Lower value: slower and more depthful searching, higer value vice versa
    parser.add_argument('--num_threads', '-nt', type=int, default=1, help='Number of Threads')
    parser.add_argument('--output_file', '-of', type=str, default=os.path.join('.', 'output.csv'), help='Output CSV File Name') # where the results will be kept (nxn) scores
    parser.add_argument('--file_status_tracker', '-f', type=str, default=os.path.join('.', 'file_status_tracker.csv'), help='File Status Tracker')


    # Parse the arguments
    args = parser.parse_args()
    print(args)
    op_type = 0 
    if args.op_type is not None:
        op_type = args.op_type 
    alpha = 0.7
    if args.alpha is not None:
        alpha = args.alpha 
    level_threshold = 0
    if args.level_threshold is not None:
        level_threshold = args.level_threshold
    BASE_DIRECTORY = os.path.join('dummy_data')
    if args.base_directory is not None:
        BASE_DIRECTORY = args.base_directory 
    output_file_name = 'output.csv'
    if args.output_file is not None:
        output_file_name = args.output_file
    file_status_tracker = 'file_status_tracker.csv'
    if args.file_status_tracker is not None:
        file_status_tracker = args.file_status_tracker
     

    #process()
    print(op_type)
    if op_type == 0: 
        find_copy_stat(alpha=alpha, level_threshold=level_threshold, BASE_DIRECTORY=BASE_DIRECTORY, num_threads=2, stat_file_name=output_file_name)
    if op_type == 1:
        process(BASE_DIRECTORY=BASE_DIRECTORY, TRACKER_FILE=file_status_tracker , input_data="", output_data="")

# python3 interactive_checker.py -ot 0 -b dummy_data_8 -a 0.7 -l 3 -nt 2 -of output_8.csv -f file_status_tracker_8.csv
# python3 interactive_checker.py -ot 0 -b dummy_data_9 -a 0.7 -l 3 -nt 2 -of output_9.csv -f file_status_tracker_9.csv
# python3 interactive_checker.py -ot 0 -b dummy_data -a 0.7 -l 3 -nt 2 -of output.csv -f file_status_tracker.csv