import bot_utils
from datetime import datetime
from mysql.connector import connect, Error
import os
import cf

# получение данных с папки Dispatcher в кеш
def get_update_dispatcher_data(serv):
    date = datetime.now()
    Base_dispatcher = dict()
    path = bot_utils.path_from_server(serv, 'Dispatcher/', 'AG3/Dispatcher/')
    retry = True
    count = 0
    while retry:
        with bot_utils.connect_snavi_ftp(serv) as ftp:
            ftp.encoding = 'cp1251'
            try:
                ftp.cwd(path)
                for i in ftp.nlst():
                    try:
                        ftp.cwd(i)
                    except:
                        print(str(date) + ' Error read path name %s ' % (i))
                        continue
                    try:
                        file = ftp.nlst()
                        Base_dispatcher[i] = file
                    except:
                        print(str(date) + ' Ошибка добавления в словарь %s' % (i))
                    ftp.cwd('..')
                retry = False
            except:
                print(str(date) + 'Connection from ' + serv + ' timeout. Retrying...')
                retry = True
                count += 1
                if (count > 10):
                    print(str(date) + 'ERROR. Server not responding')
                    count = 0
                    break
    print(str(date) + 'Данные из папки %s получены' % (path))
    return Base_dispatcher

# проверяем наличие прибора в папке Dispatcher
def check_dispetcher(serv, number):
    if serv == 'm1':
        map_dispatcher = cf.Dispatcher_dict_m1
    elif serv == 'm3':
        map_dispatcher = cf.Dispatcher_dict_m3
    res_mess = ''
    if len(map_dispatcher) > 0:
        for key in map_dispatcher.keys():
            for val in map_dispatcher.get(key):
                if number == val:
                    res_mess += '-Номер найден в [Dispatcher]. Клиент: %s ✅\n' % (key)
                    return res_mess
                elif len(val) > 7 and val[1:] == number:
                    res_mess += '-Номер найден в [Dispatcher]. Клиент: %s Он в блокировке‼️\n' % (key)
                    return res_mess
    return '-Прибора нет в папке [Dispatcher]‼️\n'

    # получаем список файлов в каталоге с даннными прибора
def writeListToFile(line):
    try:
        file = open("listFiles", 'a', encoding="utf-8")
        if line.find("drw-") == -1 and line.find("bin") > 0:
            file.write(line + '\n')
        file.close()
    except:
        print("Ошибка записи списка содержимого папки Data")

# проверка папки Data на сервере
def check_data1(number, serv)->str:
    res:str = ''  
    date = datetime.now()
    ftp = bot_utils.connect_snavi_ftp(serv)
    path = bot_utils.path_from_server(serv, '', 'AG5/')
    if ftp == 0:
        return ""
    try:
        path = (path + "Data/" + number)
        print(ftp.cwd(path))
        print(ftp.retrlines('LIST', writeListToFile))
        print(date.strftime("%d-%m-%Y %H:%M") + ' ' + serv + 'список папок получен')
    except:
        bot_utils.write_to_log('Error open path ' + path +' on ', serv)
        print(date.strftime("%d-%m-%Y %H:%M") + ' ' + serv + ' ошибка считывания с FTP' )
        ftp.quit()
        return ""
    ftp.quit()
    print('Папака с прибором ' + number + ' в папке Data найдена')
    try:
        if serv == 'm3':
            return bot_utils.find_actual_file()
        file = open("listFiles", 'r', encoding="utf-8")
        res = file.readline()
        file.close()
        os.remove("listFiles")
    except:
        print("Error. listFiles")
    return res

#запуск сбора данных с сервера
def check_data_on_server(serv:str, number) ->str:
    res_mess = '🖥Данные с сервера - ' + serv + ':\n'
    if bot_utils.check_file(number, serv, cf.file_dev) == 1:
        res_mess += '-Прибор есть в ключе✅\n'
    else:
        res_mess += '-Прибора нет в ключе‼️\n'
    if bot_utils.check_file(number, serv, cf.file_unservice) == 1:
        res_mess += '-Прибор найден в [Unservice]‼️\n'
    res_mess += check_dispetcher(serv, number)
    if bot_utils.check_file(number, serv, cf.file_mispass) == 1:
        res_mess += '-Прибор найден в [MismatchPasswordList]‼️\n'
    file_in_data = check_data1(number, serv)
    if serv == 'm1': 
        file_in_data = file_in_data[29:]
    if len(file_in_data) > 0:
        res_mess += '-Самый актуальный файл в папке [Data]: \n' + str(file_in_data.split()) + '\n'
    return res_mess


def connect_to_db(db_name:str):
    try:
        connection = connect(host=cf.SQL_SERVER, 
                    port='3316', 
                    user=cf.SQL_LOGIN, 
                    password=cf.SQL_PASS,
                    database=db_name,)
        return connection
    except Error as e:
        print(e)


def find_data_by_number(number:str, connection):
    resault = ""
    find_query = "SELECT * FROM terminals WHERE number=\"" + number + "\"" 
    try:
        with connection.cursor() as cursor:
            cursor.execute(find_query)
            resault = cursor.fetchall()
    except Error as e:
        print(e)
    return resault