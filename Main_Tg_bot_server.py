import os

import urllib3.exceptions
from telebot import *
from threading import Thread
import requests

from program.DB_Logs import DB_sites
from program.TG_bot import TgBotChacker

eq = None


th = Thread(target=lambda: quit())

def quit():
    while True:
            if(input() == 'eq'):
                print('Программа закрыта')
                os.kill(os.getpid(),9)


def starts_websites():
    db = DB_sites()
    mas = {'https://google.com/': ['Google', 0]}

    for i in mas:
        db.insert_into_DB(mas[i][0], i)

    db.Close_DB()




if __name__ == '__main__':
    starts_websites()
    th.start()

    while True:
        t1 = 150
        count = 0
        dt = 100
        try:
            try:
                TgBotChacker().Start_bot(count)

            except urllib3.exceptions.MaxRetryError as e:
                count += 1
                print(e, 'Сервер отключили скоро перезапусться')
                time.sleep(random.randint(t1, t1 + dt))
            except Exception as e:
                count += 1
                print(e, 'Сервер отключили скоро перезапусться')
                TgBotChacker().Bot_fail()
                time.sleep(random.randint(t1, t1+dt))
            except requests.exceptions.ConnectionError as e:
                print(e, 'Сервер отключили скоро перезапусться инет пропал')
                time.sleep(random.randint(t1, t1 + dt))

        except:
            print('Идет много багов')






