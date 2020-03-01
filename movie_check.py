import glob
import re
import os
import shutil
import rarfile
from send2trash import send2trash


class FileNotError(Exception):
    def __init__(self, message):
        self.message = message


class MatchNotFoundError(Exception):
    def __init__(self, message):
        self.message = message


class MovieCheck:

    def __init__(self):
        # m_post_date = re.search('.*Posted by noname on (?P<match_str>[a-zA-Z0-9\s]*) |.*', post_date.text)
        # self.re_file_prefix = '[A-Z]{3}[0-9]{2} ([0-3][0-9][0-1][0-9][0-3][0-9]|[0-9]{4})'
        self.re_file_prefix_list = ['(?P<group_name>[A-Z]{3}[0-9]{2}) '
                                    '(?P<date_str>([0-3][0-9][0-1][0-9][0-3][0-9]|[0-9]{4}))',
                                    '(?P<date_str>([0-3][0-9][0-1][0-9][0-3][0-9]|[0-9]{4})) '
                                    '(?P<group_name>[A-Z]{3}[0-9]{2})']
        self.re_time = '1[0-9][03]0'

        self.path = 'D:\DATA\Downloads\AKB48'
        rarfile.UNRAR_TOOL = r'C:\\myapp\\unrar'
        self.target_names = []
        try:
            with open('extract_file.txt', encoding='utf-8') as file:
                for line in file.readlines():
                    self.target_names.append(line.rstrip('\n'))
        except:
            print('Error')

        self.is_check = True
        # self.is_check = False

    def __get_dest_name(self, extract_name: str = ''):
        # ファイル存在チェック
        if not os.path.isfile(os.path.join(self.path, extract_name)):
            raise FileNotError(extract_name + 'のファイルが存在しません')

        pre_list = []
        m_pre = None
        for re_file_prefix in self.re_file_prefix_list:
            m_pre = re.search(re_file_prefix, extract_name)
            if m_pre:
                pre_list.append(m_pre.group('group_name'))
                pre_list.append(m_pre.group('date_str'))
                break

        is_not_find = True
        err_detail = ''
        if len(pre_list) > 0:
            find_filter = filter(lambda name: re.search(pre_list[0], name)
                                 and re.search(pre_list[1], name)
                                 , self.target_names)
            find_list = list(find_filter)
            if len(find_list) == 1:
                is_not_find = False
            elif len(find_list) > 1:
                m_time = re.search(self.re_time, extract_name.replace(pre_list[0], '').replace(pre_list[1], ''))
                if m_time:
                    find_filter = filter(lambda name: re.search(pre_list[0], name) and re.search(pre_list[1], name)
                                         and re.search(m_time.group(), name)
                                         , self.target_names)
                    find_list = list(find_filter)
                    if len(find_list) == 1:
                        is_not_find = False
                    else:
                        err_detail = 'many time[{}] error'.format(m_time.group())
            else:
                err_detail = 'no match file_prefix'
        else:
            err_detail = 'no match file_prefix'

        if is_not_find:
            if m_pre:
                raise MatchNotFoundError(extract_name + 'に一致するファイル名がextract_files.txtに存在しませんでした ['
                                         + m_pre.group() + '] ' + err_detail)
            else:
                raise MatchNotFoundError("{} の中にグループ名が無し".format(extract_name))

        # print('change 【' + extract_name.replace(m_pre.group(), find_list[0]) + '】 <-- ' + mp4_filename)
        return extract_name.replace(m_pre.group(), find_list[0])

    def execute(self):
        file_list = glob.glob(os.path.join(self.path, '*part1.rar'))
        file_list.extend(glob.glob(os.path.join(self.path, '*part01.rar')))
        for file in file_list:
            mp4_filename = ''
            try:
                rar_archive = rarfile.RarFile(file)
                for f in rar_archive.infolist():
                    if re.search('url$', f.filename):
                        continue
                    mp4_filename = f.filename
            except rarfile.NeedFirstVolume:
                print('Error ボリュームが足りてない ' + file)

            if len(mp4_filename) <= 0:
                print('Error 解凍ファイルが不明 [' + os.path.basename(file) + ']')
                continue

            try:
                dest_filename = self.__get_dest_name(mp4_filename)
            except FileNotError as err:
                print('FileNot ' + err.message)
                continue
            except MatchNotFoundError as err:
                print('MatchNotFound ' + err.message)
                continue

            print('change 【' + dest_filename + '】 <-- ' + mp4_filename)
            file.replace('part1', 'part*')
            delete_list = glob.glob(file.replace('part1', 'part*').replace('part01', 'part*'))
            print('  rm ' + str(delete_list))

            if not self.is_check:
                src_filepath = os.path.join(self.path, mp4_filename)
                dest_filepath = os.path.join(self.path, dest_filename)
                shutil.move(src_filepath, dest_filepath)
                for filepath in delete_list:
                    send2trash(filepath)


if __name__ == '__main__':
    tool = MovieCheck()
    tool.execute()
