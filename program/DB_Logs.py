import sqlite3
from datetime import *

# creates DB, tables and headers

class DB_Logs():
    def __init__(self):
        self.name = 'Check_sites.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS time_work_sites (title, link, time, fail)")
        #self.bot = bot


    def insert_into_DB(self, data):

        self.cur.execute("INSERT INTO time_work_sites VALUES (?, ?, ?, ?)", data)
        self.con.commit()

    def delete_from_DB(self, link):
        self.cur.execute(f'DELETE FROM time_work_sites WHERE link = "{link}"')
        self.con.commit()

    def read_DB_time(self, duration, link):
        delt_time = datetime.now() - timedelta(minutes=duration)
        list_timeline_errors = list(self.cur.execute(f'SELECT time, fail FROM time_work_sites WHERE link = "{link}" AND datetime(time) >= datetime("{delt_time}")'))
        count = len(list_timeline_errors)
        text = '\n'.join([f'{datetime.strptime(i[0], "%Y-%m-%d %H:%M:%S.%f").strftime("%Y-%m-%d %H:%M")} - {i[1]}' for i in list_timeline_errors])

        text = f"Сайт https://www.udmurtneft.ru/ \n Дата и время  -  статус\n{text}\n\nКол-во записей - {count}"

        return text

    def send_DB(self):
        self.con.commit()
        return self.name

    def Close_DB(self):
        self.con.close()


class DB_sites():
    def __init__(self):
        self.name = 'Check_sites.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS sites (title, link)")


    def insert_into_DB(self, title, link):
        if(len(list(self.cur.execute(f'SELECT link FROM sites WHERE link = "{link}"'))) == 0):
            data = [title, link]
            self.cur.execute("INSERT INTO sites VALUES(?, ?)", data)
            print([ f'{i}\n' for i in self.read_DB()])
            self.con.commit()

    def delete_from_DB(self, link):
        self.cur.execute(f'DELETE FROM sites WHERE link = "{link}"')
        self.con.commit()

    def read_DB(self):
        list_timeline_errors = list(self.cur.execute(f'SELECT * FROM sites'))
        return list_timeline_errors

    def Close_DB(self):
        self.con.close()


class Users():
    def __init__(self):
        self.name = 'Check_sites.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (Name, user_id)")


    def insert_into_DB(self, name, user_id):
        if(len(list(self.cur.execute(f'SELECT user_id FROM users WHERE user_id = "{user_id}"'))) == 0):
            data = [name, user_id]
            self.cur.execute("INSERT INTO users VALUES(?, ?)", data)
            print([ f'{i}\n' for i in self.read_DB()])
            self.con.commit()

    def delete_from_DB(self, username):
        self.cur.execute(f'DELETE FROM users WHERE Name = "{username}"')
        self.con.commit()

    def read_DB(self):
        list_timeline_errors = list(self.cur.execute(f'SELECT * FROM users'))
        d ={}
        for i in list_timeline_errors:
            d[i[0]] = i[1]
        return d

    def Close_DB(self):
        self.con.close()


