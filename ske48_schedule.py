import re
import sys
import requests
import json
import mysql.connector
from datetime import datetime
import yaml
import os
from bs4 import BeautifulSoup
import urllib.request
from akb48_data import Akb48Data
from akb48_db import Akb48Db


class Ske48Schedule:

    def __init__(self):

        self.start_year = 2017
        self.start_month = 10
        # self.conn = self.__get_conn()
        # self.cursor = self.conn.cursor()
        self.base_url = 'http://www.ske48.co.jp/schedule/'
        # self.main_url = 'http://www.ske48.co.jp/schedule/calendar.php?y=2018&m=10'
        # http://www.ske48.co.jp/schedule/?id=1569313609
        self.detail_other_list = []
        self.detail_none = []

        self.db = Akb48Db()

    def get_one_month_no_detail(self, year, month):

        # self.main_url = 'http://www.ske48.co.jp/schedule/calendar.php?y=2018&m=10'
        one_month_url = os.path.join(self.base_url, 'calendar.php?y={}&m={}'.format(year, month))
        # print(one_month_url)
        with urllib.request.urlopen(one_month_url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            # print(html_soup)
            # stage_list = html_soup.find_all('li', class_='stage')
            td_list = html_soup.find_all('tr')
            idx = 0
            for td in td_list:

                th_data = td.find('th')
                # m_day = re.search('<th>(?P<day>[0-9]{1,2})日\([月火水木金土日]\)</th>', str(th_data))
                m_day = re.search('(<th>|<th class.*>)(?P<day>[0-9]{1,2})日', str(th_data))
                day = ''
                if m_day:
                    day_str = "{:0>2}".format(int(m_day.group('day')))
                    # print(day_str)
                else:
                    print('the_date is None'.format(str(th_data)))
                stage_list = td.find_all('li', class_='stage')
                idx = 0
                for stage in stage_list:
                    a_link = stage.find('a')
                    stage_name_text = stage.text
                    if '劇場休館日' == stage.text:
                        continue

                    if 'href' in a_link.attrs:
                        stage_url = a_link.attrs['href']

                    # print(stage_name_text)
                    the_date, title = self.__parse_title_no_detail(stage_name_text, year, month, day_str)
                    if the_date is None:
                        one_schedule_url = '{}{}'.format(self.base_url, stage_url.replace('./', ''))
                        the_date = datetime.strptime('{}/{}/{}'.format(year, month, day_str), '%Y/%m/%d')
                        msg = 'detail failed {} {} url {}'.format(stage_name_text, the_date, one_schedule_url)
                        data = Akb48Data()
                        data.groupName = 'SKE48'
                        data.title = msg
                        data.theDate = the_date
                        data.status = 'not exist'

                        if not self.db.is_exist(data.theDate, data.groupName):
                            self.db.export(data)

                        continue

                    data = Akb48Data()
                    data.groupName = 'SKE48'
                    data.title = title
                    data.theDate = the_date
                    data.member = self.__get_member(stage_url)
                    data.status = 'not exist'
                    print('{} {}'.format(the_date, title))
                    if data.member is None:
                        data.member = ''
                    else:
                        print('    {}'.format(data.member))

                    if not self.db.is_exist(data.theDate, data.groupName):
                        self.db.export(data)


                '''
                if 'href' in a_link.attrs:
                    stage_url = a_link.attrs['href']
                print('{} {}'.format(stage, stage_url))

                one_schedule_url = '{}{}'.format(self.base_url, stage_url.replace('./', ''))
                print(one_schedule_url)

                with urllib.request.urlopen(one_schedule_url) as response:
                    detail_html = response.read()
                    detail_html_soup = BeautifulSoup(detail_html, "html.parser")
                    detail = detail_html_soup.find('div', class_='detail')

                    if detail is None:
                        self.detail_none.append(str(stage))
                        continue

                    the_date, title = self.__parse_title(detail.find('h3'))
                    # if len(detail_date) > 0:
                    #     theDate = datetime.strptime('{} {}:00'.format(detail_date, time_str), '%Y.%m.%d %H:%M:%S')

                    member, time_str = self.__parse_detail(str(detail)) # detail.textだと、BRタグが抜けてしまう
                    # if len(time_str) > 0:
                    #     theDate = datetime.strptime('{} {}:00'.format(detail_date, time_str), '%Y.%m.%d %H:%M:%S')
                    # else:
                    #     theDate = datetime.strptime('{}'.format(detail_date), '%Y.%m.%d')
                    # detail_text = str(detail)
                    print('  one_schedule [{}] {}'.format(the_date, title))
                    print('    {}'.format(member))

                # if idx > 2:
                #     break
                idx = idx + 1
                '''
            # stage_list = html_soup.find_all('dt', class_='stage')
            # for stage in stage_list:
            #     span_date = stage.find('span', class_='new')
            #     print('{} {}'.format(stage, span_date))

            # entrys = html_soup.find_all('div', class_='archive-content')

    def __get_member(self, url):
        one_schedule_url = '{}{}'.format(self.base_url, url.replace('./', ''))
        # print(one_schedule_url)

        with urllib.request.urlopen(one_schedule_url) as response:
            detail_html = response.read()
            detail_html_soup = BeautifulSoup(detail_html, "html.parser")
            detail = detail_html_soup.find('div', class_='detail')

            if detail is None:
                self.detail_none.append(str(url))
                return None

            member, time_str = self.__parse_detail(str(detail))  # detail.textだと、BRタグが抜けてしまう

        return member

    def get_one_month(self, year, month):

        # self.main_url = 'http://www.ske48.co.jp/schedule/calendar.php?y=2018&m=10'
        one_month_url = os.path.join(self.base_url, 'calendar.php?y={}&m={}'.format(year, month))
        print(one_month_url)
        print('http://www.ske48.co.jp/schedule/calendar.php?y=2019&m=10')
        with urllib.request.urlopen(one_month_url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            # print(html_soup)
            stage_list = html_soup.find_all('li', class_='stage')
            idx = 0
            for stage in stage_list:
                a_link = stage.find('a')
                if '劇場休館日' == stage.text:
                    continue

                if 'href' in a_link.attrs:
                    stage_url = a_link.attrs['href']
                print('{} {}'.format(stage, stage_url))

                one_schedule_url = '{}{}'.format(self.base_url, stage_url.replace('./', ''))
                print(one_schedule_url)
                with urllib.request.urlopen(one_schedule_url) as response:
                    detail_html = response.read()
                    detail_html_soup = BeautifulSoup(detail_html, "html.parser")
                    detail = detail_html_soup.find('div', class_='detail')

                    if detail is None:
                        self.detail_none.append(str(stage))
                        continue

                    the_date, title = self.__parse_title(detail.find('h3'))
                    # if len(detail_date) > 0:
                    #     theDate = datetime.strptime('{} {}:00'.format(detail_date, time_str), '%Y.%m.%d %H:%M:%S')

                    member, time_str = self.__parse_detail(str(detail)) # detail.textだと、BRタグが抜けてしまう
                    # if len(time_str) > 0:
                    #     theDate = datetime.strptime('{} {}:00'.format(detail_date, time_str), '%Y.%m.%d %H:%M:%S')
                    # else:
                    #     theDate = datetime.strptime('{}'.format(detail_date), '%Y.%m.%d')
                    # detail_text = str(detail)
                    print('  one_schedule [{}] {}'.format(the_date, title))
                    print('    {}'.format(member))

                # if idx > 2:
                #     break
                idx = idx + 1
            # stage_list = html_soup.find_all('dt', class_='stage')
            # for stage in stage_list:
            #     span_date = stage.find('span', class_='new')
            #     print('{} {}'.format(stage, span_date))

            # entrys = html_soup.find_all('div', class_='archive-content')

    def __parse_title_no_detail(self, title_text, year, month, day):

        m_time = re.search('[' + re.escape('（(') + '](?P<time_str>[0-2][0-9]:[0-6][0-9])開演[' + re.escape('）)') + ']', title_text)
        # print(title_text)
        # m_time = re.search('(?P<time_str>[0-2][0-9]:[0-6][0-9])開演', title_text)
        if m_time:
            # time_str = m_time.group('time_str').replace('24:', '00:')
            time_str = m_time.group('time_str')
            if re.search('2[456]:', time_str):
                time_str = time_str.replace('24:', '00:').replace('25:', '01:').replace('26:', '02:')
                day = '{:0>2}'.format(int(day) + 1)
                # print('{}-{:0>2}'.format(year, month))
                title = title_text
            else:
                replace_time_str = m_time.group()
                title = title_text.replace(replace_time_str, '')
            the_date = datetime.strptime('{}/{}/{} {}:00'.format(year, month, day, time_str), '%Y/%m/%d %H:%M:%S')
        else:
            title = ''
            the_date = None

        return the_date, title

    def __parse_title(self, h3_title):

        if h3_title is None:
            return '', ''

        title = h3_title.text

        m_detail_date = re.search('20[0123][0-9]\.[01][0-9]\.[0-3][0-9]', h3_title.text)
        if m_detail_date:
            date_str = m_detail_date.group()
            title = title.replace(date_str, '')

        m_time = re.search('(?P<time_str>[0-2][0-9]:[0-6][0-9])開演<br/><br/>', h3_title.text)
        if m_time:
            time_str = m_time.group('time_str')
            replace_time_str = m_time.group()
            title = title.replace(replace_time_str, '')

        the_date = datetime.strptime('{} {}:00'.format(date_str, time_str), '%Y.%m.%d %H:%M:%S')

        return the_date, title

    def __parse_detail(self, detail_text):
        detail_text_list = detail_text.split('\n')

        member = ''
        time_str = ''
        for idx, detail_text in enumerate(detail_text_list):
            if '出演メンバー' in detail_text:
                m_member = re.search('【出演メンバー】.*【', detail_text)
                # m_member = re.search('【出演メンバー】.*<br/><br/>', detail_text)
                if m_member:
                    member = re.sub('【$', '', m_member.group())

                m_time = re.search('(?P<time_str>[0-2][0-9]:[0-6][0-9])開演<br/><br/>', detail_text)
                if m_time:
                    time_str = m_time.group('time_str')
            else:
                detail_text = re.sub('<h3 .*', '', detail_text)
                detail_text = re.sub('<div class="detail clearfix">', '', detail_text)
                detail_text = re.sub('(<dl>|</dd>|</li>|<dd>|<li>|</dl>|</ul>|</div>)', '', detail_text)
                detail_text = re.sub('<ul class="profileList clearfix">', '', detail_text)
                detail_text = re.sub('<dt><a href="/profile.*', '', detail_text)
                detail_text = re.sub('<span><a href="/profile.*', '', detail_text)
                if len(detail_text.strip()) > 0:
                    msg = '  detail [{}] {}'.format(idx, detail_text)
                    self.detail_other_list.append(msg)

        return member, time_str

    def execute(self):
        now_date = datetime.now()
        for year in range(self.start_year, now_date.year + 1):
            start_month = self.start_month if year == self.start_year else 1
            end_month = now_date.month if year == now_date.year else 13
            for month in range(start_month, end_month):
                print('{}-{:0>2}'.format(year, month))
                # self.get_one_month(year, month)
                self.get_one_month_no_detail(year, month)

                # if month == 12:
                #     return

        for detail_other in self.detail_other_list:
            print(detail_other)
        for detail_none in self.detail_none:
            print(detail_none)

        return


if __name__ == '__main__':
    ske48 = Ske48Schedule()
    ske48.execute()
