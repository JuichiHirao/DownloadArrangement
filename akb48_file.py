import glob
import os
import re
import mysql.connector
import yaml
from datetime import datetime


class Akb48Data:

    def __init__(self):
        self.id = -1
        self.groupName = ''
        self.title = ''
        self.member = ''
        self.theDate = None
        self.memo = ''
        self.memo2 = ''
        self.remark = ''
        self.filename = ''
        self.rating1 = 0
        self.rating2 = 0
        self.status = ''
        self.createdAt = None
        self.updatedAt = None


class Akb48Db:

    def __init__(self):

        self.conn = self.__get_conn()
        self.cursor = self.conn.cursor()

    def __get_conn(self):

        with open('credentials.yml') as file:
            obj = yaml.load(file, Loader=yaml.FullLoader)
            self.user = obj['user']
            self.password = obj['password']
            self.hostname = obj['hostname']
            self.dbname = obj['dbname']

        return mysql.connector.connect(user=self.user, password=self.password,
                                       host=self.hostname, database=self.dbname)

    def update_file_info(self, data: Akb48Data = None):
        sql = 'UPDATE tv.akb48 ' \
              '  SET filename = %s ' \
              '    , status = %s ' \
              ' WHERE id = %s'

        self.cursor.execute(sql, (data.filename, data.status, data.id))

        self.conn.commit()

    def get_by_date(self, theDate: datetime=None):

        if theDate is None:
            return False

        sql = 'SELECT id ' \
              '  , group_name, title, subtitle, member ' \
              '  , the_date, memo, memo2, remark ' \
              '  , filename, rating1, rating2, status ' \
              '  , created_at, updated_at ' \
              '  FROM tv.akb48 WHERE date(the_date) = %s '

        self.cursor.execute(sql, (theDate, ))

        rs = self.cursor.fetchall()

        exist = False

        data_list = []
        if rs is not None:
            for row in rs:
                data = Akb48Data()
                data.id = row[0]
                data.groupName = row[1]
                data.title = row[2]
                data.subTitle = row[3]
                data.member = row[4]
                data.theDate = row[5]
                data.memo = row[6]
                data.memo2 = row[7]
                data.remark = row[8]
                data.filename = row[9]
                data.rating1 = row[10]
                data.rating2 = row[11]
                data.status = row[12]
                data.createdAt = row[13]
                data.updatedAt = row[14]

                data_list.append(data)

        return data_list


class Akb48File:

    def __init__(self):

        self.db = Akb48Db()

        self.dir_list = ['D:\\DATA\\Downloads\\AKB48', 'F:\\AKB48公演']

    def execute(self):

        for dir in self.dir_list:
            file_list = glob.glob(os.path.join(dir, '*'))
            print('{}'.format(len(file_list)))

            for file in file_list:
                file_basename = os.path.basename(file)
                m_file = re.search('[12][0-9][0-1][0-9][0-3][0-9]', file_basename)
                if m_file:
                    try:
                        the_date = datetime.strptime(m_file.group(), '%y%m%d')
                        # print(the_date)
                    except ValueError as err:
                        print(err)
                        print(m_file.group())
                        continue

                    data_list = self.db.get_by_date(the_date)

                    match_cnt = 0
                    match_data = None
                    for data in data_list:
                        if data.groupName.upper() in file_basename.upper():
                            # m_time = re.search('\\s[01][0-9][0-5][0-9]\\s', file)
                            the_date_time = data.theDate.strftime('%H%M')
                            if the_date_time in file:
                                match_cnt = match_cnt + 1
                                match_data = data
                        else:
                            continue
                    # print(data_list)

                    if match_cnt == 1:
                        if match_data.filename is None or len(match_data.filename) <= 0:
                            match_data.status = 'exist'
                            match_data.filename = file_basename
                            self.db.update_file_info(match_data)
                            print('updated {} {}'.format(match_data.theDate, file_basename))
                        else:
                            print('already updated {} {}'.format(match_data.theDate, file_basename))
                    else:
                        print('no match or many match {}'.format(file_basename))

            # break


if __name__ == '__main__':
    akb48 = Akb48File()
    akb48.execute()
