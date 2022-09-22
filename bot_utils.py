from datetime import datetime
from ftplib import FTP
import os
import re
import cf
import locale
from mysql.connector import connect, Error

# настройки подключеня к серверам по FTP
config_m_1 = [cf.M1_IP, cf.M1_PORT, cf.M1_LOGIN, cf.M1_PASS]
config_m_3 = [cf.M3_IP, cf.M3_PORT, cf.M3_LOGIN, cf.M3_PASS]

def find_actual_file() -> str:
    max_date = ['0'] * 3
    result = ''
    date = datetime.now().strftime("%m-%d-%Y")

    with open("listFiles", 'r', encoding='utf-8') as file:
        list_files = file.readlines()
        for line in list_files:
            if line.find(date) >= 0 and line.find('bin') >= 0 :
                result = line
                break
            str_date = line.split(' ', 1)
            if re.fullmatch("\d\d-\d\d-\d{4}", str_date[0]):
                tmp = str_date[0].split('-')
                if int(tmp[2]) > int(max_date[2]) or int(tmp[0]) > int(max_date[0]) or int(tmp[1]) > int(max_date[1]):
                    max_date = tmp
                    result = line
    print(result)
    os.remove("listFiles")
    return result

# запись логов в файл
def write_to_log(str, server):
    date = datetime.now()
    try:
        cf.f_log = open(cf.file_log, 'a')
        cf.f_log.write((date.strftime("%d-%m-%Y %H:%M") + ' ' + str + server + '\n'))
        cf.f_log.close()
    except:
        print("Error write to log file")

# функция для подключения к FTP
def connect_snavi_ftp(serv):
    ftp = FTP()
    if serv == 'm1':    # проверяем валидное ли имя сервера
        s = config_m_1
    elif serv == 'm3':
        s = config_m_3
    else:
        write_to_log('Error server name ', serv)
        ftp.quit()
        return 0
    try:
        print(ftp.connect(s[0], int(s[1]))) # подключаемся к ftp
        print(ftp.login(s[2], s[3]))
    except:
        write_to_log('Error connect to ftp ',s[0])
        ftp.quit()
        return 0
    return ftp

# достаем из строки только первые попавшие 7 цифр номера прибора
def find_num_in_string(line, number):
    i = 0
    temp = ''
    while i < len(line) and len(temp) < 7:
        if line[i] >= '0' and line[i] <= '9':
            temp += line[i]
        i += 1
    if temp == number or temp == number[1:] or temp == number[2:]:
        return 1
    return 0

# функция подключается к FTP и проверяет наличия прибора в файле который указан в аргументах
def check_file(number, serv, file):
    date = datetime.now() 
    ftp = connect_snavi_ftp(serv)
    if ftp == 0:
        return 0
    if serv == 'm1':
        path = file
    elif serv == 'm3':
        path = ('AG5/' + file)
    try:
        with open(cf.file_tmp, 'wb') as f_tmp:
            ftp.retrbinary('RETR ' + path, f_tmp.write, 1024)
    except:
        write_to_log('Error file ' + path + ' write from ftp ', serv)
        ftp.quit()
        return 0
    with open(cf.file_tmp, 'r') as f:
        while True:     # проверяем файл temp после скачивания с сервера на наличие номера прибора в нем
            line = f.readline()
            if not line:
                break
            elif find_num_in_string(line, number) == 1:
                ftp.quit()
                print(date.strftime("%d-%m-%Y %H:%M") + ' %s %s успешно проверен' % (serv, file))
                return 1
    print(date.strftime("%d-%m-%Y %H:%M") + ' ' + serv + ' ' + file + ' проверен но безрезультатно')
    ftp.quit()
    return 0

    # создаем файл atg в чужих
def add_to_atg(update, context):
    count = 0
    chat = update.effective_chat
    text = update.message.text.split()
    now = datetime.now()
    locale.setlocale(locale.LC_ALL, '')
    file_atg = ['AutoGRAPH database 1.3\n', str(count), ' records\n']
    path  = cf.path_predator + now.strftime("%m. %B\\")
    if not os.path.isdir(path):
        os.mkdir(path)
    if len(text) == 4:
        if text[2].isdigit() and len(text[2]) == 7 and text[3].isdigit() and len(text[3]) == 7:
            count = int(text[3]) - int(text[2]) + 1
            count1 = count
            file_atg[1] = str(count)
            list_files = os.listdir(path)
            for file in list_files:
                if file == (text[1] + '.atg'):
                    try:
                        with open((path + text[1] + '.atg'), 'r+', encoding='utf-8') as f:
                            file_atg = f.readlines()
                            count_text = file_atg[1].split(' ')
                            file_atg[1] = str(int(count_text[0]) + count) + ' ' + count_text[1]
                            break
                    except:
                        print('Error add to atg ' + text[1])
            for number in file_atg:
                if number[:7] == text[2]:
                    context.bot.send_message(chat_id=chat.id, text=chat.first_name +  ', прибор ' + text[2] + ' в файле уже есть‼️')
                    return
            while count > 0:
                while len(text[2]) < 7:
                    text[2] = '0' + text[2]
                file_atg.append((text[2] + ':\tPASSWORD=testtest;\n'))
                text[2] = str(int(text[2]) + 1)
                count -= 1
            with open(path+text[1] + '.atg', 'w+', encoding='utf-8') as file:
                for line in file_atg:
                    file.write(line)
            context.bot.send_message(chat_id=chat.id, text=chat.first_name + ', в файл ' + text[1] + '.atg добавлено ' + str(count1) + ' приборов ✅')
        else:
            context.bot.send_message(chat_id=chat.id, text=chat.first_name + ', аргументы указаны не верно, повторите попытку‼️')
    else:
        context.bot.send_message(chat_id=chat.id, text=chat.first_name + ', аргуентов должно быть три:\n/atg [имя файла] [номер прибра первый] [номер последний]\n Если нужно добавить в один и тот же файл еще приборы, просто повторите операцию.')

#отправляем уведомление админу и добавляем юзера в базу
def add_user(chat, context, id: str):
    context.bot.send_message(chat_id=id, text="⚠️У нас новый пользователь: " + chat.first_name)
    with open('data', 'a', encoding='utf-8') as f:
        f.write(str(chat.id) + ' ' + str(chat.first_name) + ' ' + str(chat.last_name) + '\n')


#поиск днных в atg и добавление в базу данных
def connect_to_db():
    try:
        with connect(host=cf.SQL_SERVER, user=cf.SQL_LOGIN, password=cf.SQL_PASS) as connection:
            print(connection)
    except Error as e:
        print(e)
