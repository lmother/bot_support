# coding: utf8
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import bot_utils
from serv import *
import cf



user_set = [214265986, 294343795]


text1 = "Непонятно😕\nЧто бы увидеть список всех команд введите /help"
text2 = 'Проверяю номер'
text3 = '-Можете отправить мне номер прибора котрый нужно проверить.\n-В номере должно быть семь цифр'
text4 = '💬Все что смог найти по данному прибору:\n\n'




def on_start(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет.\n' + chat.first_name + ' , чем могу быть полезен 🥷')
    cf.Dispatcher_dict_m1 = get_update_dispatcher_data('m1')
    cf.Dispatcher_dict_m3 = get_update_dispatcher_data('m3')
    if check_user(chat.id) == 0: # если пользователя в истории нет, тогда добавим)
        bot_utils.add_user(chat, context, "214265986")
        

def on_help(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text="/start - просто поздороваться))\n/help - список всех комманд\n" + text3)
    if check_user(chat.id) == 0: # если пользователя в истории нет, тогда добавим)
        bot_utils.add_user(chat, context, "214265986") 

# проверяем data файл на наличие id пользователя в нем
def check_user(id):
    with open('data', 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            list = line.split(' ')
            if list is not None and list[0] == str(id):
                f.close()
                return 1
    return 0

def on_message(update, context):
    res_mess = ''
    chat = update.effective_chat
    text = update.message.text
    if check_user(chat.id) == 0: # если пользователя в истории нет, тогда добавим)
         bot_utils.add_user(chat, context, "214265986")
    try:
        if len(text) == 7 and text.isdigit():
            number = text
            context.bot.send_message(chat_id=chat.id, text=(text2 + ' ' + text + ' 🔄👨🏻‍💻'))
            # проверяем наличие данных на М3
            res_mess += check_data_on_server('m3', number)
            # проверяем наличие данных на М1
            res_mess += check_data_on_server('m1', number)
            context.bot.send_message(chat_id=chat.id, text=(text4 + res_mess))
        else:
            raise
    except:
        context.bot.send_message(chat_id=chat.id, text=text1)

def main():
    print("Бот запущен. Нажмите Ctrl+C для завершения")
    cf.Dispatcher_dict_m1 = get_update_dispatcher_data('m1')
    cf.Dispatcher_dict_m3 = get_update_dispatcher_data('m3')

    updater = Updater(cf.TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("atg", bot_utils.add_to_atg))
    dispatcher.add_handler(CommandHandler("start", on_start))
    dispatcher.add_handler(CommandHandler("help", on_help))
    dispatcher.add_handler(MessageHandler(Filters.text | Filters.document.category("text"), on_message))
    #dispatcher.add_handler(MessageHandler(Filters.user(user_set) | Filters.text | Filters.document.category("text"), on_message))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()