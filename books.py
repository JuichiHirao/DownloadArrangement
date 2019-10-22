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


class ZipArchive:

    def __init__(self):

        self.path = 'D:\DATA\Downloads'
        self.export_path = 'D:\DATA\Downloads\COMICS'
        self.target_names = []
        # self.dir_name = '(堦斒僐儈僢僋) [備偆偒傑偝傒] 揝榬僶乕僨傿乕 戞{0:02d}姫'
        # self.zip_name = '(1985-2008) [ゆうきまさみ] 鉄腕バーディー 第{0:02d}巻'
        # self.dir_name = '(堦斒僐儈僢僋) [偙傗傑婎晇] 側偍偞傝僟儞僕儑儞 戞{0:02d}姫'
        # self.zip_name = '[こやま基夫] なおざりダンジョン 第{0:02d}巻'
        # self.dir_name = '[いわしげ孝] 花マル伝 第{0:02d}巻'
        # self.zip_name = '[いわしげ孝] 花マル伝 第{0:02d}巻'
        # self.dir_name = '[原泰久] キングダム -KINGDOM- 第{0:02d}巻'
        # self.zip_name = '[原泰久] キングダム -KINGDOM- 第{0:02d}巻'
        # self.dir_name = '[前川たけし] 鉄拳チンミ Legends 第{0:02d}巻'
        # self.zip_name = '[前川たけし] 鉄拳チンミ Legends 第{0:02d}巻'
        # self.dir_name = '[川原正敏] 龍帥の翼 史記・留侯世家異伝 第{0:02d}巻'
        # self.zip_name = '[川原正敏] 龍帥の翼 史記・留侯世家異伝 第{0:02d}巻'
        # self.path = 'D:\DATA\Downloads\[偙傗傑婎晇] 側傝備偒僟儞僕儑儞'
        # self.dir_name = 'なりゆきダンジョン{0:01d}巻'
        # self.zip_name = '(1997-1998) [こやま基夫] なりゆきダンジョン 第{0:01d}巻'
        # self.range_start = 1
        # self.range_end = 4
        # self.path = 'D:\DATA\Downloads\(堦斒僐儈僢僋) [埨揷峅擵] 僔儑儉僯(暥屔斉) 慡3姫'
        # self.dir_name = 'ショムニ (文庫) 第{0:02d}巻'
        # self.zip_name = '(1996-1998) [安田弘之] ショムニ 文庫版 第{0:02d}巻'
        # self.range_start = 1
        # self.range_end = 4
        # self.target_name = glob.escape('[深沢美潮] フォーチュン・クエスト ') + '*'
        # self.re_str = re.escape('[深沢美潮] フォーチュン・クエスト ') + '第(?P<num>[0-9]{2})巻 (?P<subheading>.*)'
        # self.zip_name = '(1989-1993) [深沢美潮] フォーチュン・クエスト 第num巻 subheading'
        # '[深沢美潮] 新フォーチュン・クエスト 第01巻 白い竜の飛来した街'
        # self.target_name = glob.escape('[深沢美潮] 新フォーチュン・クエスト ') + '*'
        # self.re_str = re.escape('[深沢美潮] 新フォーチュン・クエスト ') + '第(?P<num>[0-9]{2})巻 (?P<subheading>.*)'
        # self.zip_name = '(1994-2012) [深沢美潮] 新フォーチュン・クエスト 第num巻 subheading'
        # '[神坂一] スレイヤーズ 01 スレイヤーズ！'
        self.target_name = glob.escape('[神坂一] スレイヤーズ ') + '*'
        self.re_str = re.escape('[神坂一] スレイヤーズ ') + '(?P<num>[0-9]{2}) (?P<subheading>.*)'
        self.zip_name = '(1990-2000) [神坂一] スレイヤーズ 第num巻 subheading'
        # '[水野良] グランクレスト戦記 第03巻'
        self.target_name = glob.escape('[水野良] グランクレスト戦記 ') + '*'
        self.re_str = re.escape('[水野良] グランクレスト戦記 ') + '第(?P<num>[0-9]{2})巻'
        self.zip_name = '[水野良] グランクレスト戦記 第num巻'

        # self.is_check = True
        self.is_check = False

    def __archive(self, archive_path, zip_filename):

        file_list = os.listdir(archive_path)

        zip_pathname = os.path.join(self.export_path, zip_filename + '.zip')
        with zipfile.ZipFile(zip_pathname, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
            for file in file_list:
                filename = os.path.basename(file)

                if file == zip_filename + '.zip':
                    continue

                # new_zip.write('data/temp/test1.txt', arcname='test1.txt')
                file_pathname = os.path.join(archive_path, filename)
                new_zip.write(file_pathname, arcname=filename)

    def get_group_str(self, match: re.match = None, group_name: str = ''):
        group_str = ''
        try:
            group_str = match.group(group_name)
        except IndexError:
            pass

        return group_str

    def execute_glob(self):
        match_list = glob.glob(os.path.join(self.path, self.target_name))

        for filename in match_list:
            print(os.path.basename(filename))
            m = re.match(self.re_str, os.path.basename(filename))
            if m:
                # zip_filename = self.zip_name.replace('num', m.group('num')) \
                #     .replace('subheading', m.group('subheading')).replace('[別スキャン]', '').strip()
                zip_filename = self.zip_name
                num = self.get_group_str(m, 'num')
                if len(num) > 0:
                    zip_filename = zip_filename.replace('num', m.group('num')).strip()

                subheading = self.get_group_str(m, 'subheading')
                if len(subheading) > 0:
                    zip_filename = zip_filename.replace('subheading', subheading).strip()

                pathname = os.path.join(self.path, zip_filename)
                self.__archive(pathname, zip_filename)

    def execute(self):
        try:
            for idx in range(self.range_start, self.range_end):
                # dir_name = '(堦斒僐儈僢僋) [備偆偒傑偝傒] 揝榬僶乕僨傿乕 戞01姫'
                dir_name = self.dir_name.format(idx)
                zip_name = self.zip_name.format(idx)
                pathname = os.path.join(self.path, dir_name)
                # with open('extract_files.txt', encoding='utf-8') as file:
                #     for line in file.readlines():
                #         self.target_names.append(line.rstrip('\n'))
                if os.path.isdir(pathname):
                    print('exist ' + dir_name)
                    self.__archive(pathname, zip_name)
                else:
                    print('not exist ' + dir_name)
        except:
            print(sys.exc_info())
            print('Error')


if __name__ == '__main__':
    tool = ZipArchive()
    tool.execute_glob()
