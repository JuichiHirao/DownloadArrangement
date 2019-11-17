import re
import sys
import requests
import json
import mysql.connector
from datetime import datetime
import yaml


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
            obj = yaml.load(file)
            self.user = obj['user']
            self.password = obj['password']
            self.hostname = obj['hostname']
            self.dbname = obj['dbname']

        return mysql.connector.connect(user=self.user, password=self.password,
                                       host=self.hostname, database=self.dbname)

    def is_exist(self, theDate: datetime=None):

        if theDate is None:
            return False

        sql = 'SELECT title ' \
              '  FROM tv.akb48 WHERE the_date = %s '

        self.cursor.execute(sql, (theDate, ))

        rs = self.cursor.fetchall()

        exist = False

        if rs is not None:
            for row in rs:
                exist = True
                break

        return exist

    def export(self, data: Akb48Data = None):
        sql = 'INSERT INTO tv.akb48 (group_name ' \
              ', title, member, the_date, status) ' \
              ' VALUES(%s' \
              ', %s, %s, %s, %s) '

        self.cursor.execute(sql, (data.groupName
                                  , data.title, data.member, data.theDate, data.status))

        self.conn.commit()


class Akb48Schedule:

    """
    """
    def __init__(self):

        self.db = Akb48Db()
        self.start_year = 2019
        self.start_month = 10
        """
        self.api_endpoint = 'https://www.akb48.co.jp/public/api/schedule/calendar/'
        # json_data = request.data
        schedule_date = {"month": "09",
                         "year": "2019",
                         "category": "0"}
        r = requests.post("https://www.akb48.co.jp/public/api/schedule/calendar/", schedule_date)

        data = r.json()
        # print(data['data']['thismonth'])
        for thismonth in data['data']['thismonth']:
            # print(json.dumps(thismonth, indent=4))
            for one_schedule in data['data']['thismonth'][thismonth]:
                print(json.dumps(one_schedule, indent=4, ensure_ascii=False))
                # print(one_schedule['title'])
                if '公演' in one_schedule['title']:
                    group = 'AKB48'
                    date = one_schedule['date']
                    title = one_schedule['title']
                    # print(json.dumps(one_schedule, indent=4, ensure_ascii=False))
                    m_member = re.search('【出演メンバ.*', one_schedule['body'])
                    if m_member:
                        member = one_schedule['member']
                        print(m_member.group())
        """

    def parse_json(self, json_data):

        data_list = []
        for thismonth in json_data['data']['thismonth']:
            # print(json.dumps(thismonth, indent=4))
            for one_schedule in json_data['data']['thismonth'][thismonth]:
                # print(json.dumps(one_schedule, indent=4, ensure_ascii=False))
                # print(one_schedule['title'])
                if '公演' in one_schedule['title']:
                    data = Akb48Data()
                    data.groupName = 'AKB48'
                    # data.theDate = one_schedule['date']
                    data.theDate = datetime.strptime(one_schedule['date'], '%Y-%m-%d %H:%M:%S')
                    # print(data.theDate.strftime('%Y%m%d %H%M%d'))
                    data.title = one_schedule['title']
                    data.status = 'not exist'
                    # print(json.dumps(one_schedule, indent=4, ensure_ascii=False))
                    m_member = re.search('【出演メンバ.*', one_schedule['body'])
                    if m_member:
                        data.member = m_member.group()
                        print('{} {} {}'.format(data.theDate, data.title, data.member))

                    if not self.db.is_exist(data.theDate):
                        self.db.export(data)

                    data_list.append(data)

        return data_list

    def __get_data(self, year, month):

        self.api_endpoint = 'https://www.akb48.co.jp/public/api/schedule/calendar/'
        # json_data = request.data
        schedule_date = {"month": "{:0>2}".format(month),
                         "year": str(year),
                         "category": "0"}
        r = requests.post("https://www.akb48.co.jp/public/api/schedule/calendar/", schedule_date)

        data = r.json()
        # print(data['data']['thismonth'])
        # for thismonth in data['data']['thismonth']:
        #     print(json.dumps(thismonth, indent=4))
        # for one_schedule in data['data']['thismonth'][thismonth]:

        return data

    def execute(self):

        now_date = datetime.now()
        for year in range(self.start_year, now_date.year+1):
            start_month = self.start_month if year == self.start_year else 1
            end_month = now_date.month if year == now_date.year else 13
            for month in range(start_month, end_month):
                print('{}-{:0>2}'.format(year, month))
                json = self.__get_data(year, month)
                data_list = self.parse_json(json)

        return


if __name__ == '__main__':
    akb48 = Akb48Schedule()
    akb48.execute()
