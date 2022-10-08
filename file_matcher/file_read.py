import csv
import os


class FileRead:
    def __init__(self):
        pass

    def read_file(self, file_name):
        lines = []
        try:
            with open(file_name, 'r', encoding='utf-8', errors='ignore') as f:
                for l in f:
                    temp = l.strip()
                    temp = temp.lower()
                    lines.append(temp)
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


"""
fr = FileRead()
lines = fr.read_file(file_name=os.path.join('.', 'out.txt'))
fr.print_lines(lines=lines)
"""
