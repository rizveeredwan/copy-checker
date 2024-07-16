import csv
import os


class FileRead:
    def __init__(self):
        pass

    def read_file(self, file_name, matching_type="fuzzy"):
        lines = []
        try:
            with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                for l in f:
                    if matching_type == "fuzzy": # fuzzy reading 
                        temp = l.strip()
                        temp = temp.lower()
                        lines.append(temp)
                    elif matching_type == "exact": # exact reading 
                        temp = l
                        temp = temp
                        lines.append(temp)
                if matching_type == "exact":
                    i = len(lines)
                    while i >= 0:
                        if lines[i] == '\n': # removing redundant blank lines from the bottom 
                            del lines[i]
                            continue 
                        else:
                            break 

        except Exception as e:
            print(e)
        return lines

    def print_lines(self, lines):
        print(len(lines))
        for i in range(0, len(lines)):
            print(lines[i])

    def file_write(self, file_name, _list):
        with open(file_name, 'w', encoding='utf-8', newline='') as f:
            csv_writer = csv.writer(f)
            for l in _list:
                csv_writer.writerow(l)


