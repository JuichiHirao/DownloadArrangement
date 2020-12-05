import re
from datetime import datetime
import os
from bs4 import BeautifulSoup
import urllib.request
from akb48_data import Akb48Data
from akb48_db import Akb48Db


class Ske48Schedule:

    def __init__(self):

        self.start_year = 2020
        self.start_month = 11
        self.base_url = 'http://www.ske48.co.jp/schedule/'
        self.detail_other_list = []
        self.detail_none = []

        self.db = Akb48Db()

    def get_one_month_no_detail(self, year, month):

        # http://www.ske48.co.jp/schedule/calendar.php?y=2018&m=10
        one_month_url = os.path.join(self.base_url, 'calendar.php?y={}&m={}'.format(year, month))
        # print(one_month_url)
        with urllib.request.urlopen(one_month_url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            # print(html_soup)
            td_list = html_soup.find_all('tr')
            idx = 0
            for td in td_list:

                th_data = td.find('th')
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
                    the_date, title = self.__parse_title(stage_name_text, year, month, day_str)
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

    def __get_member(self, url):
        one_schedule_url = '{}{}'.format(self.base_url, url.replace('./', ''))

        with urllib.request.urlopen(one_schedule_url) as response:
            detail_html = response.read()
            detail_html_soup = BeautifulSoup(detail_html, "html.parser")
            detail = detail_html_soup.find('div', class_='detail')

            if detail is None:
                self.detail_none.append(str(url))
                return None

            member, time_str = self.__parse_detail(str(detail))  # detail.textだと、BRタグが抜けてしまう

        return member

    def __parse_title(self, title_text, year, month, day):

        m_time = re.search('[' + re.escape('（(') + '](?P<time_str>[0-2][0-9]:[0-6][0-9])開演[' + re.escape('）)') + ']', title_text)
        if m_time:
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
                self.get_one_month_no_detail(year, month)

            # for rangeでは、当月は実行されないので、当月のみ指定の場合は↓で実行
            if self.start_month == start_month and self.start_year == year:
                print('{}-{:0>2}'.format(year, start_month))
                self.get_one_month_no_detail(year, start_month)

        for detail_other in self.detail_other_list:
            print(detail_other)
        for detail_none in self.detail_none:
            print(detail_none)

        return


if __name__ == '__main__':
    ske48 = Ske48Schedule()
    ske48.execute()
