import re
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup
import urllib.request
from akb48_data import Akb48Data
from akb48_db import Akb48Db


class Nmb48Schedule:

    def __init__(self):

        self.db = Akb48Db()
        # self.db = None

    def __parse_entry_contents(self, entry_content, the_date_str):

        content_list = entry_content.find_all('div')
        if 'gekijou' not in content_list[0]['class']:
            return None
        # print(content_list[0]['class'])
        # print(entry_content)

        is_gekijou = False
        is_gekijou_first = False
        time_str = ''
        title = ''
        member = ''
        for idx, content in enumerate(content_list):
            # 2017-05-03 までの取得方法
            content_class_list = content['class']
            # print('class [{}]'.format(content['class']))
            if 'kaerebalink-box' in content['class']:
                break

            if is_gekijou:
                if 'syousai' not in content_class_list:
                    # class 'team' or 'trainee'以外に、titleで、公演の場合もあるので、is_gekijou_firstを設定
                    if is_gekijou_first:
                        title = content.text
                        is_gekijou_first = False
                        continue
                    break
                else:
                    m_time = re.search('(?P<time_str>[0-2][0-9]:[0-6][0-9])', content.text)
                    if m_time:
                        time_str = m_time.group('time_str')
                    else:
                        member = content.text
                    # print('         [{}] {} [{}]'.format(idx, content_class_list, content.text))

            if 'gekijou' in content_class_list:
                is_gekijou = True
                is_gekijou_first = True

        if len(title) <= 0:
            # print(entry_content)
            for idx, content in enumerate(content_list):
                if 'kaerebalink-box' in content['class']:
                    break
                content_class_list = content['class']
                print('         [{}] {} [{}]'.format(idx, content_class_list, content.text))
            return None

        data = Akb48Data()
        data.groupName = 'NMB48'
        data.title = title.replace(data.groupName, '').strip()
        if len(time_str) > 0:
            if re.search('2[4-9]:', time_str):
                the_date = datetime.strptime('{}'.format(the_date_str), '%Y/%m/%d')
                the_date += timedelta(days=1)
                hour = 24 - int(time_str.split(':')[0])
                minute = int(time_str.split(':')[1])
                the_date.replace(hour=hour, minute=minute)
            else:
                data.theDate = datetime.strptime('{} {}:00'.format(the_date_str, time_str), '%Y/%m/%d %H:%M:%S')
        else:
            data.theDate = datetime.strptime('{}'.format(the_date_str), '%Y/%m/%d')
        data.member = member
        data.status = 'not exist'

        # print('【{}】 {}  member {}'.format(data.title, data.theDate, data.member))

        return data

    def __get_one_page(self, url):

        with urllib.request.urlopen(url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            section_list = html_soup.find_all('div', class_='section1')
            for section in section_list:
                entry_date = section.find('div', class_='entry-date')
                """ <div class="entry-date">
                      <span class="day">19</span><span class="month month12"></span><span class="year">2019</span>
                    </div> """
                # print(str(entry_date))
                span_list = entry_date.find_all('span')
                the_date_str = '{}/{}/{}'.format(span_list[2].text, span_list[1]['class'][1].replace('month',''), span_list[0].text)

                entry_content = section.find('div', class_='entry-content')
                data = self.__parse_entry_contents(entry_content, the_date_str)

                if data is not None:
                    if not self.db.is_exist(data.theDate, data.groupName):
                        print('【{}】 {}  member {}'.format(data.title, data.theDate, data.member))
                        self.db.export(data)
                    else:
                        print('exist 【{}】 {}  member {}'.format(data.title, data.theDate, data.member))
        return

    def execute(self):

        idx = 328
        while idx < 329:
            if idx == 0:
                url = 'http://nmbschedule.blog.fc2.com/'
            else:
                url = 'http://nmbschedule.blog.fc2.com/page-{}.html'.format(idx)
            print('page {} {}'.format(idx, url))

            self.__get_one_page(url)
            idx = idx + 1


if __name__ == '__main__':
    hkt48 = Nmb48Schedule()
    hkt48.execute()
