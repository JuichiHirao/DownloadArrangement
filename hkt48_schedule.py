import re
from datetime import datetime
import os
from bs4 import BeautifulSoup
import urllib.request
from akb48_data import Akb48Data
from akb48_db import Akb48Db


class Hkt48Schedule:

    def __init__(self):

        self.start_year = 2019
        self.start_month = 3
        self.base_url = 'http://www.hkt48.jp'
        # self.base_url = 'http://www.hkt48.jp/schedule/'
        self.detail_other_list = []
        self.detail_none = []

        self.db = Akb48Db()
        # self.db = None

    def get_one_month_no_detail(self, year, month):

        one_month_url = os.path.join('{}/{}'.format(self.base_url, 'schedule/'), '{}/{:0>2}'.format(year, month))
        # print('{}-{:0>2}'.format(year, month))
        print(one_month_url)

        with urllib.request.urlopen(one_month_url) as response:
            html = response.read()
            html_soup = BeautifulSoup(html, "html.parser")
            # print(html_soup)
            tr_list = html_soup.find_all('tr')
            idx = 0
            for tr in tr_list:

                th_data = tr.find('th')
                span_data = th_data.find('span')
                if span_data:
                    day_str = "{:0>2}".format(int(span_data.text))
                else:
                    print('day None')
                p_list = tr.find_all('p')
                for p_data in p_list:
                    if p_data:
                        img_tag = p_data.find('img')
                        img_src = img_tag.attrs['src']
                        category_kind = os.path.basename(img_src)
                        if 'category_icon_01' in category_kind:
                            a_tag = p_data.find('a')
                            if '休館日' in a_tag or '休館日' in a_tag.text:
                                continue

                            the_date, title = self.__parse_title(a_tag.text, year, month, day_str)

                            if 'href' in a_tag.attrs:
                                stage_url = '{}{}'.format(self.base_url, a_tag.attrs['href'])
                                # print(stage_url)
                                # stage_url = a_tag.attrs['href']
                                member = self.__get_member(stage_url)

                            print('{} 【{}】 【{}】'.format(the_date, title, member))

                            data = Akb48Data()
                            data.groupName = 'HKT48'
                            data.title = title
                            data.theDate = the_date
                            data.member = member
                            data.status = 'not exist'

                        else:
                            # print('{}/{}/{} [{}]'.format(year, month, category_kind))
                            data = None
                    else:
                        print('p tag None')

                    if data is not None:
                        # sql = 'INSERT INTO tv.akb48 (group_name '
                        #       ', title, member, the_date, status) '
                        if not self.db.is_exist(data.theDate, data.groupName):
                            self.db.export(data)
                    # break
                continue

    def __get_member(self, url):
        # one_schedule_url = '{}{}'.format(self.base_url, url.replace('./', ''))

        print('    {}'.format(url))
        with urllib.request.urlopen(url) as response:
            detail_html = response.read()
            detail_html_soup = BeautifulSoup(detail_html, "html.parser")
            detail = detail_html_soup.find('div', class_='asset-body')

            if detail is None:
                self.detail_none.append(str(url))
                return None

            member, time_str = self.__parse_detail(str(detail))  # detail.textだと、BRタグが抜けてしまう

        return member

    def __parse_title(self, title_text, year, month, day):

        m_time = re.search('(?P<time_str>[0-2][0-9]:[0-6][0-9]) ', title_text)

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

            the_date = datetime.strptime('{}/{}/{} {}:00'.format(year, month, day
                                                                 , m_time.group('time_str')), '%Y/%m/%d %H:%M:%S')
            # print('{} {}'.format(the_date, a_tag.text))
        else:
            print('  m_time nothing {}'.format(title_text))
            title = ''
            the_date = None

        return the_date, title

    def __parse_detail(self, detail_text):
        detail_text_list = detail_text.split('\n')

        member = ''
        time_str = ''
        is_next_member = False
        for idx, detail_text in enumerate(detail_text_list):
            if '出演メンバー' in detail_text:
                is_next_member = True
                continue

            if is_next_member:
                # print('  is_next_member {}'.format(detail_text))
                member = detail_text.replace('</div>', '').strip()
                break
            # else:
            #     if len(detail_text.strip()) > 0:
            #         msg = '  detail [{}] {}'.format(idx, detail_text)
            #         self.detail_other_list.append(msg)

        if not is_next_member or len(member.strip()) <= 0:
            for idx, detail_text in enumerate(detail_text_list):
                msg = '  detail [{}] {}'.format(idx, detail_text)
                print(msg)

        # member = member.replace('<br/>', '')
        member = re.sub('<br/>$', '', member)

        return member, time_str

    def execute(self):
        now_date = datetime.now()
        for year in range(self.start_year, now_date.year + 1):
            start_month = self.start_month if year == self.start_year else 1
            end_month = now_date.month if year == now_date.year else 13
            for month in range(start_month, end_month):
                print('{}-{:0>2}'.format(year, month))
                self.get_one_month_no_detail(year, month)

            break

        for detail_other in self.detail_other_list:
            print(detail_other)
        for detail_none in self.detail_none:
            print(detail_none)

        return


if __name__ == '__main__':
    hkt48 = Hkt48Schedule()
    hkt48.execute()
