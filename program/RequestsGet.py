import datetime

import requests
import time
import random
from program.DB_Logs import DB_Logs, Users


class RequestsGet():
    def __init__(self, lists_sites, bot):
        #Переопределяем список сайтов
        self.lists_sites = lists_sites

        #Переопределяем бота
        self.bot = bot

        # Уникальный юзер агент
        self.user_agent = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 MullvadBrowser/115.10.0',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15']

        # Ошибки которые пропускаються
        self.fail_exeption = (requests.exceptions.ConnectionError)

    
    # Функция с проверкой робатоспасобности сайтов
    def check_sites(self):

            while True:

                for i in self.lists_sites:
                    log = DB_Logs()
                    status_code = 200
                    try:
                        response = requests.get(i, headers={'User-agent': self.user_agent[random.randint(0, 3)]}, verify=False)
                        status = response.status_code
                        response.close()

                        status_code = status

                        print(f'{i} - {status}')
                        if(status!=200 and self.lists_sites[i][1]==0):
                            self.lists_sites[i][1] = 1
                            self.Send_for_users_nout_failed(f'C {i} сайтом какие-то проблемы код ошибки {status}')
                        elif(status==200 and self.lists_sites[i][1]==1):
                            self.lists_sites[i][1] = 0
                            self.Send_for_users_nout_restored(f'{i} сайт востановлен')


                    except requests.exceptions.HTTPError as e:
                        status_code = 500
                        self.Send_for_users_nout_failed(f'На {i} сайт нельзя попасть так из-за ошибки HTTPError но он скорейвсего работает')
                        
                        if(self.lists_sites[i][1]==0):
                            self.lists_sites[i][1] = 1
                    
                    except self.fail_exeption as e:
                        print(e)
                    
                    except Exception as e:
                        self.Send_for_users_nout_failed(f'На {i} сайте неизвестная ошибка')
                        status_code = 400
                        if(self.lists_sites[i][1]==0):
                            self.lists_sites[i][1] = 1


                    log.insert_into_DB([self.lists_sites[i][0], i, datetime.datetime.now(), status_code])
                    log.Close_DB()


                time.sleep(random.randint(135, 200))

    def Send_for_users_nout_restored(self, text):
        us = Users()
        mas = us.read_DB()
        us.Close_DB()
        for i in mas:
            self.bot.send_message(mas[i], text)

    def Send_for_users_nout_failed(self, text):
        us = Users()
        mas = us.read_DB()
        us.Close_DB()
        for i in mas:
            self.bot.send_message(mas[i], text)

