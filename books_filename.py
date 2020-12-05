import glob
import re
import os
import shutil
import sys
import zipfile36 as zipfile
from send2trash import send2trash


class FileNotError(Exception):
    def __init__(self, message):
        self.message = message


class MatchNotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class FileRename:

    def __init__(self):

        self.path = 'C:\SHARE\ScanSnap'
        self.export_path = '{}\TEMP'.format(self.path)

        self.plus_value = 2

        self.base_name = 'グインサーガ040_*.jpg'

        self.is_check = True
        # self.is_check = False

    def execute_glob(self):

        if not os.path.exists(self.export_path):
            os.mkdir(self.export_path)

        file_list = glob.glob(os.path.join(self.path, self.base_name))
        if self.plus_value < 0:
            sort_file_list = sorted(file_list)
        else:
            sort_file_list = sorted(file_list, reverse=True)

        for filename in sort_file_list:
            # print(os.path.basename(filename))

            re_seq_number = re.search('_(?P<seq_number>[0-9]{3})', filename)
            seq_number = ''
            if re_seq_number is not None:
                seq_number = re_seq_number.group('seq_number')
            else:
                print('noting {}'.format(filename))
                continue

            result_num = int(seq_number) + self.plus_value

            change_name = re.sub('_{}'.format(seq_number), '_{}'.format(str(result_num).zfill(3)), filename)
            os.rename(filename, change_name)
            print('{} <- {}'.format(change_name, filename))


if __name__ == '__main__':
    tool = FileRename()
    tool.execute_glob()
    # tool.execute()
