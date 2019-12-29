import re
import requests
from akb48_db import Akb48Db
from akb48_data import Akb48Data
from datetime import datetime


class Akb48Schedule:

    def __init__(self):

        self.db = Akb48Db()
        self.start_year = 2019
        self.start_month = 12

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

                    if not self.db.is_exist(data.theDate, data.groupName):
                        print('{} {} {}'.format(data.theDate, data.title, data.member))
                        self.db.export(data)
                    else:
                        print('exist {} {} {}'.format(data.theDate, data.title, data.member))

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

            # for rangeでは、当月は実行されないので、当月のみ指定の場合は↓で実行
            if self.start_month == start_month and self.start_year == year:
                print('{}-{:0>2}'.format(year, start_month))
                json = self.__get_data(year, start_month)
                data_list = self.parse_json(json)

        return


if __name__ == '__main__':
    akb48 = Akb48Schedule()
    akb48.execute()
