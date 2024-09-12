from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

import shutil
import os
import zipfile


def unzip_and_place_files(src_zip="", inter_folder="", dst_folder="", valid_extensions=['c', 'cpp', 'java', 'py']):
    with zipfile.ZipFile(src_zip, 'r') as zip_ref:
        # Extract all contents to the destination directory
        zip_ref.extractall(inter_folder)
    stack = [inter_folder]
    i = 0
    while i < len(stack):
        curr = stack[i]
        if os.path.isdir(curr) is True:
            files = os.listdir(curr)  # folder will visit underneath
            for j in range(0, len(files)):
                stack.append(os.path.join(curr, files[j]))
        else:  # just a file, direct copy
            p = os.path.basename(curr)
            ext = p.split('.')[1]
            print(p, ext)
            if valid_extensions is not None:
                if ext in valid_extensions:
                    print("come here ", curr, dst_folder)
                    shutil.move(src=curr, dst=dst_folder)
            else:
                shutil.move(src=curr, dst=dst_folder)
        i += 1


class DatabaseConnectivity:
    def __init__(self, database_url="mongodb://localhost:27017", database_name=""):
        self.database_url = database_url
        self.database_name = database_name
        self.mongodb_connect = None
        self.db = None

        self.connect_to_mongoDB()
        if self.mongodb_connect is not None:
            self.connect_to_db()
        print(self.mongodb_connect, self.db)
        assert (self.mongodb_connect is not None and self.db is not None)

    def connect_to_mongoDB(self):
        # Connect to MongoDB
        try:
            self.mongodb_connect = MongoClient(
                self.database_url)  # Assuming MongoDB is running locally on the default port
        except Exception as e:
            print(e)
            self.mongodb_connect = None

    def connect_to_db(self):
        try:
            # Access the database
            self.db = self.mongodb_connect[self.database_name]
        except Exception as e:
            print(e)
            self.db = None

    def return_collection(self, collection_name):
        try:
            return self.db[collection_name]
        except Exception as e:
            print(e)
            return



    def create_entry_for_new_zip_submission(self, db_name="", collection="", zip_file_path="", alpha=0.5, level_threshold=3, process_status=0,
                                            email_sent=False, submission_time=str(datetime.now()), completion_time=None, json_data={},
                                            client_email='rizvee@cse.du.ac.bd'):
        # directory creation
        if os.path.exists(os.path.join('.', 'local_storage')) is False:
            os.mkdir(os.path.join('.', 'local_storage'))
        entry = {
            'alpha' : alpha,
            'level_threshold' : level_threshold,
            'process_status' : process_status, # 0:WHITE, 1:GREY, 2:BLACK
            'email_sent' : email_sent,
            'submission_time' : submission_time,
            'completion_time' : completion_time,
            'json_data' : json_data, # query should this be string or not,
            'client_email' : client_email
        }
        try:
            result = self.mongodb_connect[db_name][collection].insert_one(entry)
            print(result.inserted_id)
            # id based folder, folder for zip, folder for unzipped
            os.mkdir(os.path.join('.', 'local_storage', str(result.inserted_id)))
            os.mkdir(os.path.join('.', 'local_storage', str(result.inserted_id), 'zip_file'))
            os.mkdir(os.path.join('.', 'local_storage', str(result.inserted_id), 'zip_file', 'temp'))
            os.mkdir(os.path.join('.', 'local_storage', str(result.inserted_id), 'all_files'))
            # sorting out the files
            if zip_file_path is not None:
                shutil.copy(src=zip_file_path, dst=os.path.join('.', 'local_storage', str(result.inserted_id), 'zip_file'))
            # unzip in temp
            src_zip = os.path.join('.', 'local_storage', str(result.inserted_id), 'zip_file', os.path.basename(zip_file_path))
            inter_folder = os.path.join('.', 'local_storage', str(result.inserted_id), 'zip_file', 'temp')
            dst_folder = os.path.join('.', 'local_storage', str(result.inserted_id), 'all_files')
            unzip_and_place_files(src_zip=src_zip, inter_folder=inter_folder, dst_folder=dst_folder, valid_extensions=['c', 'cpp', 'java', 'py'])
            return str(result.inserted_id)
        except Exception as e:
            print(e)
            return None

    def update_entry(self, primary_key=None, db_name="", collection="", alpha=0.5,  level_threshold=3, process_status=2,
                                            email_sent=False, submission_time=str(datetime.now()), completion_time=None, json_data={},
                     client_email="rizvee@cse.du.ac.bd"):
        data = {}
        if alpha is not None:
            data['alpha'] = alpha
        if level_threshold is not None:
            data['level_threshold'] = level_threshold
        if process_status is not None:
            data['process_status'] = process_status
        if email_sent is not None:
            data['email_sent'] = email_sent
        if submission_time is not None:
            data['submission_time'] = submission_time
        if completion_time is not None:
            data['completion_time'] = completion_time
        if json_data is not None:
            data['json_data'] = json_data
        if client_email is not None:
            data['client_email'] = client_email
        try:
            filter = {'_id' : ObjectId(primary_key)}
            # Use the $set operator to update the fields
            update = {'$set': data}
            self.mongodb_connect[db_name][collection].update_one(filter, update)
            return True
        except Exception as e:
            print(e)
            return None

# DB entry create

# DB existing entry update


if __name__ == '__main__':
    dc = DatabaseConnectivity(database_name='copy_code_db')
    res = dc.create_entry_for_new_zip_submission(self, collection="copy_code_colc", file_path=None, alpha=0.5, level_threshold=3, process_status=0,
                                            email_sent=False, submission_time=str(datetime.now()), completion_time=None, json_data={})
    print(res)