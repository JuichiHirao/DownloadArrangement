import glob
import re
import os
import shutil
import sys
import zipfile36 as zipfile


class ZipArchive:

    def __init__(self):

        self.path = 'C:\SHARE\ScanSnap\AAA'
        self.prefix_name = 'カイジ24億07_'

        self.to_path = 'C:\SHARE\ScanSnap'
        self.to_prefix_name = 'カバチ3-25_'

        self.is_check = True
        # self.is_check = False


    def execute(self):

        range_start = 0
        range_end = 100

        try:
            for idx in range(range_start, range_end):
                filename = '{}{}.jpg'.format(self.prefix_name, str(idx).zfill(3))
                pathname = os.path.join(self.path, filename)
                # if os.path.isfile(pathname):
                #     print('exist {}'.format(pathname))
                # else:
                #     print('not exist {}'.format(pathname))
                filename = '{}{}.jpg'.format(self.to_prefix_name, str(idx+131).zfill(3))
                to_pathname = os.path.join(self.to_path, filename)
                print('{} <- {}'.format(to_pathname, pathname))
                shutil.copy(pathname, to_pathname)
                continue
        except:
            print(sys.exc_info())
            print('Error')


if __name__ == '__main__':
    tool = ZipArchive()
    # tool.execute_glob()
    tool.execute()
