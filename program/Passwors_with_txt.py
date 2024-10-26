from program.DB_Logs import Users


def Passwords(bot):
    try:
        mas_pass = dict(i.split(':') for i in open('passwords.txt'))
        pass_users = ''.join(mas_pass['password_users'].split('\n'))
        pass_root = ''.join(mas_pass['password_root'].split('\n'))
    except FileNotFoundError as e:
        print('Нет файла паролей')
        pass_users = 'Tg_Bot_Oil_Tel'
        pass_root = 'Root_pass'

        with open('passwords.txt', 'w+') as f:
            text = f'password_users:Tg_Bot_Oil_Tel\npassword_root:Root_pass'
            f.write(text)

        us = Users()
        mas = us.read_DB()
        us.Close_DB()
        for i in mas:
            bot.send_message(mas[i], 'Нет файла паролей я создайл файл и пароли стандартные')


    except Exception as e:
        print(e, 'Ошибка в паролем')
        pass_users = 'Tg_Bot_Oil_Tel'
        pass_root = 'Root_pass'

        text = 'Какая-то ошибка с паролем поэтому пароль стандартный'
        us = Users()
        mas = us.read_DB()
        us.Close_DB()
        for i in mas:
            bot.send_message(mas[i], text)

    return pass_users, pass_root


def New_password(new_pass, pass_root):
    with open('passwords.txt', 'r+') as f:
        f.truncate(0)
        text = f'password_users:{new_pass}\npassword_root:{pass_root}'
        f.write(text)

