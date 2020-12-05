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

        self.white_page_file = 'D:\DATA\Downloads\COMICS\((WhitePage.jpg'
        self.path = 'D:\DATA\Downloads'
        self.export_path = 'D:\DATA\Downloads\COMICS'
        self.target_names = []

        """
        self.range_start = 1
        # プラス1した値を設定
        self.range_end = 73
        # self.total_num_start = 29
        self.dir_name = 'NARUTO—ナルト— カラー版 {0:02d} [aKraa]'
        self.zip_name = '(1999-2014) [岸本斉史] NARUTO —ナルト— カラー版 第{0:02d}巻'
        """

        # range_start, range_end, total_num_start
        self.num_setting = [1, 30, 0]
        self.dir_name = '[立原あゆみ] 弱虫 (ちんぴら) 第{0:02d}巻'
        self.zip_name = '(1997-2006) [立原あゆみ] 弱虫 (ちんぴら) 第{0:02d}巻'
        self.is_white_page = False
        # self.num_setting = [82, 98, 0]
        # self.dir_name = '[青山剛昌] 名探偵コナン 第{0:02d}巻'
        # self.zip_name = '[青山剛昌] 名探偵コナン 第{0:02d}巻'
        # self.is_white_page = False
        # self.num_setting = [1, 72, 0]
        # self.dir_name = 'NARUTO—ナルト— カラー版 {0:02d} [aKraa]'
        # self.zip_name = '(1999-2014) [岸本斉史] NARUTO —ナルト— カラー版 第{0:02d}巻'
        # self.is_white_page = True
        # self.num_setting = [1, 34, 0]
        # self.dir_name = 'HUNTER×HUNTER カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[冨樫義博] HUNTER×HUNTER カラー版 第{0:02d}巻'
        # self.is_white_page = True
        # self.num_setting = [1, 34, 0]
        # self.dir_name = '[藤原カムイ] ドラゴンクエスト列伝 ロトの紋章 ~紋章を継ぐ者達へ~ 第{0:02d}巻'
        # self.zip_name = '(2004-2020) [藤原カムイ] ドラゴンクエスト列伝 ロトの紋章 ~紋章を継ぐ者達へ~ 第{0:02d}巻'
        # self.is_white_page = False
        # self.num_setting = [1, 5, 1]
        # self.dir_name = 'ジョジョの奇妙な冒険 第1部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 1部 ファントムブラッド{1:02d}'
        # self.num_setting = [1, 7, 6]
        # self.dir_name = 'ジョジョの奇妙な冒険 第2部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 2部 戦闘潮流{1:02d}'
        # self.num_setting = [1, 16, 13]
        # self.dir_name = 'ジョジョの奇妙な冒険 第3部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 3部 スターダストクルセイダース{1:02d}'
        # self.num_setting = [1, 18, 29]
        # self.dir_name = 'ジョジョの奇妙な冒険 第4部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 4部 ダイヤモンドは砕けない{1:02d}'
        # self.num_setting = [1, 17, 47]
        # self.dir_name = 'ジョジョの奇妙な冒険 第5部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 5部 黄金の風{1:02d}'
        # self.num_setting = [1, 17, 64]
        # self.dir_name = 'ジョジョの奇妙な冒険 第6部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 6部 ストーンオーシャン{1:02d}'
        # self.num_setting = [1, 24, 81]
        # self.dir_name = 'ジョジョの奇妙な冒険 第7部 カラー版 {0:02d} [aKraa]'
        # self.zip_name = '[荒木飛呂彦] ジョジョの奇妙な冒険 カラー版 第{0:03d}巻 7部 スティール・ボール・ラン{1:02d}'

        self.is_check = True
        # self.is_check = False

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

        range_start = self.num_setting[0]
        range_end = self.num_setting[1] + 1
        total_num_start = self.num_setting[2]

        try:
            total_num = total_num_start
            # for idx in range(self.range_start, self.range_end):
            for idx in range(range_start, range_end):
                # dir_name = '(堦斒僐儈僢僋) [備偆偒傑偝傒] 揝榬僶乕僨傿乕 戞01姫'
                dir_name = self.dir_name.format(idx)
                if total_num_start == 0:
                    zip_name = self.zip_name.format(idx)
                else:
                    zip_name = self.zip_name.format(total_num, idx)

                pathname = os.path.join(self.path, dir_name)

                if self.is_white_page:
                    file_list = os.listdir(pathname)
                    sorted(file_list)
                    white_page = file_list[0].replace('p000', 'p000a')
                    white_filename = os.path.join(pathname, white_page)
                    if not os.path.isfile(white_filename):
                        print('白紙ページをコピーしました{}'.format(white_page))
                        shutil.copy(self.white_page_file, white_filename)
                    else:
                        print('白紙ページのファイル名に既にファイルが存在します')

                # with open('extract_files.txt', encoding='utf-8') as file:
                #     for line in file.readlines():
                #         self.target_names.append(line.rstrip('\n'))
                if os.path.isdir(pathname):
                    print('exist ' + dir_name)
                    self.__archive(pathname, zip_name)
                else:
                    print('not exist ' + dir_name)
                total_num = total_num + 1
        except:
            print(sys.exc_info())
            print('Error')


if __name__ == '__main__':
    tool = ZipArchive()
    # tool.execute_glob()
    tool.execute()
