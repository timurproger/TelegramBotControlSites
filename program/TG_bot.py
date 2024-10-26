import telebot
from telebot import *
from threading import Thread
import requests

from program.DB_Logs import DB_Logs, DB_sites, Users
from program.Passwors_with_txt import Passwords, New_password
from program.RequestsGet import RequestsGet


class TgBotChacker():

    def __init__(self, ):
        # экземпляр потока
        self.th1 = None
        # Список сайтов для начала
        self.lists_sites = self.Start_list_sites()
        #apihelper.proxy = {'https':'https://bitrix2:102354@91.215.112.210:2020'}
        #apihelper.proxy = {'https': 'https://190.171.161.62:8080'}

        # Забираем из базы данных id users
        us = Users()
        mas = us.read_DB()
        us.Close_DB()

        key = open('BotKey.txt').read()
        self.list_users = mas
        # Создаем массив
        self.Veryfi_users = self.Start_list_users()

        self.User_id_root = []

        # Создание бота
        self.bot = telebot.TeleBot(key)
        # Ошибки которые пропускаються
        self.fail_exeption = (requests.exceptions.ConnectionError)
        # сылка которая удаляеться
        self.link_del = None
        # сылка которая проверяеться
        self.link_time_check = None
        # password
        self.Password, self.Password_root = Passwords(bot=self.bot)


        # Первичный запуск парсира
        self.Start_pars()

        @self.bot.message_handler(commands=['help_root'])
        def help(message):
            id_user = message.from_user.id
            if (id_user in self.User_id_root):
                text = f'/change_password - изменение пароля\n/users - посмотреть какие пользователи есть\n/root - авторизация под root\n/delete - удаление пользователей'
                self.bot.send_message(id_user, f'Список команд\n{text}')

        @self.bot.message_handler(commands=['users'])
        def Users_list(message):
            id_user = message.from_user.id
            if (id_user in self.User_id_root):
                text = ''.join([f'{i}\n' for i in self.list_users])
                self.bot.send_message(id_user, f'Список пользователей\n{text}')


        @self.bot.message_handler(commands=['change_password'])
        def change_password(message):
            id_user = message.from_user.id
            if (id_user in self.User_id_root):
                question = f'Вы точно хотите изменить пароль'
                keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
                key_c = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')  # кнопка «Да»
                keyboard.add(key_c)  # добавляем кнопку в клавиатуру
                key_yes = types.InlineKeyboardButton(text='Изменить', callback_data='change')  # кнопка «Да»
                keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
                self.bot.send_message(id_user, text=question, reply_markup=keyboard)


        def add_password(message):
            self.Password = message.text
            New_password(message.text, self.Password_root)
            self.bot.send_message(message.from_user.id, f'Пароль изменен на {self.Password}')


        @self.bot.message_handler(commands=['root'])
        def Root(message):
            self.bot.send_message(message.chat.id, 'Пароль')
            self.bot.register_next_step_handler(message, Root_veryfi)

        def Root_veryfi(message):
            id_user = message.from_user.id
            if(self.Password_root == message.text):
                self.bot.delete_message(id_user, message.id)
                self.bot.send_message(id_user, 'Добро пожаловать root')
                self.User_id_root.append(id_user)
            else:
                self.bot.send_message(message.chat.id, 'Пароль не верный')

        @self.bot.message_handler(commands=['delete'])
        def Root_delete(message):
            id_user = message.from_user.id
            if(id_user in self.User_id_root):
                self.bot.send_message(message.chat.id, 'Для удаления пользователя напишите его username')
                self.bot.register_next_step_handler(message, delete_users)


        def delete_users(message):
            if(message.text in self.list_users):
                us = Users()
                us.delete_from_DB(message.text)
                us.Close_DB()
                self.list_users.pop(message.text)
                self.bot.send_message(message.chat.id, 'Пользователь удален')
            else:
                self.bot.send_message(message.from_user.id, f'Такого пользователя нет')


        # Обраьотка команды veryfi
        @self.bot.message_handler(commands=['veryfi'])
        def Start_bot(message):
            id_user = message.from_user.id

            if(message.from_user.username in self.list_users):
                self.bot.send_message(id_user, 'Добро пожаловать')
                self.Veryfi_users[id_user] = True
            else:
                self.bot.send_message(id_user, 'Введите пароль')
                self.bot.register_next_step_handler(message, VeryFi)


        def VeryFi(message):
            id_user = message.from_user.id
            print(message.id)
            if(message.text == self.Password):
                self.bot.delete_message(id_user, message.id)
                self.bot.send_message(id_user, 'Добро пожаловать')
                self.list_users[message.from_user.username] = id_user
                self.Veryfi_users[id_user] = True
                us = Users()
                us.insert_into_DB(message.from_user.username, id_user)
                us.Close_DB()
            else:
                self.bot.send_message(id_user, 'Пароль не верный')


        # Обраьотка команды edit
        @self.bot.message_handler(commands=['edit'])
        def edit(message):
            id_user = message.from_user.id
            if(self.Veryfi_users[message.from_user.id] or id_user in self.User_id_root):
                question = 'выбирете дальнейшее действие для сайта'
                keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
                key_yes = types.InlineKeyboardButton(text='добавить', callback_data='add')  # кнопка «Да»
                keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
                key_no = types.InlineKeyboardButton(text='удалить', callback_data='delete')
                keyboard.add(key_no)

                self.bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


        @self.bot.message_handler(commands=['get_db'])
        def send_DB(message):
            id_user = message.from_user.id
            if (self.Veryfi_users[message.from_user.id] or id_user in self.User_id_root):
                db_log = DB_Logs()
                path = db_log.send_DB()
                db_log.Close_DB()
                self.bot.send_document(message.chat.id, open(path, 'rb'))


        @self.bot.message_handler(commands=['get_db_last_time'])
        def send_time_DB(message):
            id_user = message.from_user.id
            if (self.Veryfi_users[message.from_user.id] or id_user in self.User_id_root):
                keyboard = types.InlineKeyboardMarkup()
                question = 'Выберете сайт'
                for i in self.lists_sites:
                    # наша клавиатура
                    key = types.InlineKeyboardButton(text=i, callback_data=i)
                    keyboard.add(key)

                self.bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


        # Обраьотка команды check_list
        @self.bot.message_handler(commands=['check_list'])
        def check_list(message):
            id_user = message.from_user.id
            if (self.Veryfi_users[message.from_user.id] or id_user in self.User_id_root):
                if (len(self.lists_sites) != 0):
                    mesg = ''
                    for i in self.lists_sites:
                        mesg += f'`{i}` - *{self.lists_sites[i][0].upper()}*' + '\n'

                    self.bot.send_message(message.from_user.id, mesg, parse_mode="MARKDOWN")
                else:
                    self.bot.send_message(message.from_user.id, 'У вас нет отслеживаемых сайтов')

        # Обработка нажатаий на опр кнопку
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            id_user = call.message.chat.id
            if (self.Veryfi_users[call.message.chat.id] or id_user in self.User_id_root):
                if call.data == 'cancel':
                    self.bot.send_message(call.message.chat.id,'Запрос отменен')
                if call.data == 'change':
                    q = 'Введите новый пароль для пользователей'
                    self.bot.send_message(call.message.chat.id, q)
                    self.bot.register_next_step_handler(call.message, add_password)
                if call.data == "add":
                    # call.data это callback_data, которую мы указали при объявлении кнопки
                    # код сохранения данных, или их обработки
                    self.bot.send_message(call.message.chat.id,
                                          "Напишите ссылку вашего сайта в формате link - name website")
                    self.bot.register_next_step_handler(call.message, add_site)
                    print('add')
                elif call.data == "delete":
                    self.bot.send_message(call.message.chat.id, "Напишите ссылку которую можно удалить")
                    self.bot.register_next_step_handler(call.message, delete_site)
                    print('delete')
                elif call.data == "yes":
                    if(self.link_del != None):
                        self.bot.send_message(call.message.chat.id, f"Сайт {self.link_del} удален")
                        self.lists_sites.pop(self.link_del)

                        self.link_del = None
                elif call.data == "no":
                    if(self.link_del != None):
                        self.bot.send_message(call.message.chat.id, f"Сайт {self.link_del} не удален")
                        self.link_del = None

                elif call.data == "min_15":
                    if (self.link_time_check != None):
                        logs = DB_Logs()
                        text = logs.read_DB_time(15, self.link_time_check)
                        self.bot.send_message(call.message.chat.id, text)
                        self.link_time_check = None
                    else:
                        self.bot.send_message(call.message.chat.id, 'Выберете сначала сайт')

                elif call.data == "min_30":
                    if (self.link_time_check != None):
                        logs = DB_Logs()
                        text = logs.read_DB_time(30, self.link_time_check)
                        self.bot.send_message(call.message.chat.id, text)
                        self.link_time_check = None
                    else:
                        self.bot.send_message(call.message.chat.id, 'Выберете сначала сайт')

                elif call.data == "hour_1":
                    if (self.link_time_check != None):
                        logs = DB_Logs()
                        text = logs.read_DB_time(60, self.link_time_check)
                        logs.Close_DB()
                        self.bot.send_message(call.message.chat.id, text)
                        self.link_time_check = None
                    else:
                        self.bot.send_message(call.message.chat.id, 'Выберете сначала сайт')

                elif call.data == "hour_2":
                    if (self.link_time_check != None):
                        logs = DB_Logs()
                        print(self.link_time_check)
                        text = logs.read_DB_time(120, self.link_time_check)
                        self.bot.send_message(call.message.chat.id, text)
                        self.link_time_check = None
                    else:
                        self.bot.send_message(call.message.chat.id, 'Выберете сначала сайт')


                elif 'http' in call.data:
                    print(call.data)
                    self.link_time_check = call.data
                    question = f'Выбирете за какое время нужно выслать базу даных по сайту {self.link_time_check}'
                    keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
                    key_15 = types.InlineKeyboardButton(text='15 мин', callback_data='min_15')  # кнопка «Да»
                    keyboard.add(key_15)  # добавляем кнопку в клавиатуру
                    key_30 = types.InlineKeyboardButton(text='30 мин', callback_data='min_30')
                    keyboard.add(key_30)
                    key_60 = types.InlineKeyboardButton(text='1 ч', callback_data='hour_1')  # кнопка «Да»
                    keyboard.add(key_60)  # добавляем кнопку в клавиатуру
                    key_120 = types.InlineKeyboardButton(text='2 ч', callback_data='hour_2')
                    keyboard.add(key_120)
                    self.bot.send_message(call.message.chat.id, text=question, reply_markup=keyboard)


        def add_site(message):
            text = message.text.lower()
            if ('http' in text):

                link, name = text.split('-')
                link = ''.join(link.split())
                name = ' '.join(name.split())
                if(link not in self.lists_sites):
                    self.lists_sites[link] = [name, 0]
                    self.bot.send_message(message.chat.id, f'Вы добавили {message.text}')
                    sites_db = DB_sites()
                    sites_db.insert_into_DB(name, link)
                else:
                    self.bot.send_message(message.chat.id, f'Такой сайт {link} уже есть в списке')
            else:
                self.bot.send_message(message.chat.id,
                                      f'{message.text} неверная ссылка может забыли указать http//....')
                self.bot.send_message(message.chat.id, "Напишите ссылку вашего сайта в формате link - name website")


        def delete_site(message):
            link = message.text
            if (link in self.lists_sites.keys()):
                self.link_del = link
                question = f'Вы точно хотите удалить {message.text}'
                keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
                key_yes = types.InlineKeyboardButton(text='да', callback_data='yes')  # кнопка «Да»
                keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
                key_no = types.InlineKeyboardButton(text='нет', callback_data='no')
                keyboard.add(key_no)

                self.bot.send_message(message.chat.id, question, reply_markup=keyboard)

                db_sites = DB_sites()
                db_sites.delete_from_DB(link)
                db_sites.Close_DB()

                logs = DB_Logs()
                logs.delete_from_DB(link)
                logs.Close_DB()
            # elif(link_del!=None):
            # bot.send_message(message.chat.id,'Не понятно какой сайт удалять, попробуйте заново')
            else:
                self.bot.send_message(message.chat.id, 'Такого сайта нет')


    def Start_pars(self):
        req = RequestsGet(self.lists_sites, self.bot)
        self.th1 = Thread(target=lambda: req.check_sites())
        self.th1.start()

    def Start_list_users(self):
        Veryfi_users={}

        for i in self.list_users:
            Veryfi_users[self.list_users[i]] = False
        return Veryfi_users

    def Start_list_sites(self):
        sites = DB_sites()
        mas_sites = sites.read_DB()
        sites.Close_DB()
        lists_sites = {}
        for i in mas_sites:
            lists_sites[i[1]] = [i[0], 0]

        return lists_sites


    def Start_bot(self, count):
        print('сервер запущен')
        self.bot.infinity_polling(interval=0)
        if (count >= 1):
            self.bot.send_message(self.message.chat.id, 'Сервер был сломан но сново запущен')

    def Bot_fail(self):
        self.bot.infinity_polling(interval=0)
        self.bot.send_message(self.message.chat.id,
                              'Бот пошел отдыхать через несколько минут прийдет (произошла какая-то проблема на стороне сервера, в скором времяни сервер будет перезапущен)')
        self.bot.stop_bot()

