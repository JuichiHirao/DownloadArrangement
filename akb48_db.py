import re
import sys
import requests
import json
import mysql.connector
from datetime import datetime
import yaml
from akb48_data import Akb48Data


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

    def is_exist(self, the_date: datetime = None, group_name: str = ''):

        if the_date is None:
            return False

        sql = 'SELECT title ' \
              '  FROM tv.akb48 WHERE akb48.group_name = %s and the_date = %s '

        self.cursor.execute(sql, (group_name, the_date))

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
