# For offline processing of the unresolved submissions
from datetime import datetime
import csv

from system_functions.database_connectivity import *
from system_functions.copy_checker.copy_checker import *
from system_functions.copy_checker.visual_html import *

# file structure
"""
- local_storage
    - id
        - zip file
        - all_files: single single each file
"""


def keep_basename(_list=[]):
    for i in range(0, len(_list)):
        _list[i] = os.path.basename(_list[i])
    return _list


def prepare_csv_entry(path_of_files=[], array_data=[], csv_file_path="similarity_matrix.csv"):
    with open(csv_file_path, 'w', errors='ignore', newline="") as f:
        csv_writer = csv.writer(f)
        data = ['']
        for i in range(0, len(path_of_files)):
            data.append(path_of_files[i])
        csv_writer.writerow(data)
        print(data)
        print(array_data)
        for key1 in range(0, len(array_data)):
            data = [path_of_files[key1]]
            # print("YES ", key1,  array_data[key1], len(array_data[key1]))
            for key2 in range(0, len(array_data)):
                try:
                    print(len(array_data[key1][key2]))
                    if key1 == key2:
                        data.append('-')
                    else:
                        data.append(array_data[key1][key2][0])
                except Exception as e:
                    print(e)
            print(data)
            csv_writer.writerow(data)
        return


def generate_all_html_files(base_folder_path="", path_of_files=[], array_data=[], alpha=0.5, level_threshold=3):
    for i in range(0, len(array_data)):
        for j in range(i + 1, len(array_data)):
            f1 = path_of_files[i]
            f2 = path_of_files[j]
            print(f1, f2)
            html_string = generate_visual_html_for_client(file1_name=f1, file2_name=f2, alpha=alpha,
                                                          level_threshold=level_threshold, sim_score=array_data[i][j][0],
                                                          tag_file1_code_arr=array_data[i][j][1], tag_file2_code_arr=array_data[i][j][2])
            print(html_string)
            f_path = os.path.join(base_folder_path, path_of_files[i].split('.')[0]+'_vs_'+path_of_files[j].split('.')[0]+'.html')
            print(f_path)
            write_into_html_file(html_string=html_string, file_name=f_path)


class OfflineProcessing:
    def __init__(self, database_url="mongodb://localhost:27017", database_name="copy_code_db"):
        self.dc = DatabaseConnectivity(database_url=database_url, database_name=database_name)

    def continuous_processing(self, database_name="copy_code_db", collection='copy_code_db', num_threads=4):
        filter = {'process_status': 0}  # not started
        result = self.dc.mongodb_connect[database_name][collection].find(filter)
        for ent in result:
            # update that it is being processed
            # print(ent)
            self.dc.update_entry(primary_key=ent['_id'], db_name=database_name, collection=collection,
                                 alpha=ent['alpha'], level_threshold=ent['level_threshold'], process_status=1,
                                 email_sent=ent['email_sent'], submission_time=ent['submission_time'],
                                 completion_time=None, json_data=ent['json_data'])
            # start updating here with thread and update in the DB after completion
            try:
                path_of_files = os.listdir(os.path.join('local_storage', str(ent['_id']), 'all_files'))
                for i in range(0, len(path_of_files)):
                    path_of_files[i] = os.path.join(os.path.join('local_storage', str(ent['_id']), 'all_files'),
                                                    path_of_files[i])
                json_data = start_copy_checking(path_of_files=path_of_files, alpha=ent['alpha'],
                                                level_threshold=ent['level_threshold'], num_threads=num_threads)
                print("DONE")
                # after completion, again update
                self.dc.update_entry(primary_key=ent['_id'], db_name=database_name, collection=collection,
                                     alpha=ent['alpha'], level_threshold=ent['level_threshold'], process_status=2,
                                     email_sent=ent['email_sent'], submission_time=ent['submission_time'],
                                     completion_time=str(datetime.now()), json_data=json_data)
            except Exception as e:
                print(e)
            # start emailing
            try:
                path_of_files = keep_basename(_list=path_of_files)
                try:
                    os.mkdir(os.path.join('.', 'local_storage', str(ent['_id']), ent['client_email']))
                except Exception as e:
                    print(e)

                # prepare CSV Entry
                csv_file_path = os.path.join('.', 'local_storage', str(ent['_id']), ent['client_email'],
                                             'similarity_matrix.csv')
                prepare_csv_entry(path_of_files=path_of_files, array_data=json_data, csv_file_path=csv_file_path)
                # prepare visual html files
                generate_all_html_files(base_folder_path=os.path.join('.', 'local_storage', str(ent['_id']), ent['client_email']),
                                        path_of_files=path_of_files, array_data=json_data, alpha=ent['alpha'],
                                        level_threshold=ent['level_threshold'])
                # prepare zip
                # send the email
                pass
            except Exception as e:
                print(e)


if __name__ == '__main__':
    oc = OfflineProcessing(database_url="mongodb://localhost:27017", database_name="copy_code_db")
    oc.continuous_processing(database_name="copy_code_db", collection='copy_code_colc')
