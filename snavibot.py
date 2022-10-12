# coding: utf8
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from bot_utils import *
from serv_ag import *
import cf
import re
import adm_menu



user_set = [214265986, 294343795]


text1 = "Непонятно😕\nЧто бы увидеть список всех команд введите /help"
text2 = 'Проверяю номер'
text4 = '💬Все что смог найти по данному прибору:\n\n'

def on_ag(update, context):
    chat = update.effective_chat
    args = update.message.text.split()
    if check_user('users', chat.id) == 0:
        add_user(chat, context, "214265986")
    else:
        if len(args) <= 1:
            context.bot.send_message(chat_id=chat.id, text='Укажите номер прибора после команды⚠️')
            return
        context.bot.send_message(chat_id=chat.id, text='Собираю данные...⏳')
        resault = find_data_by_number(args[1], connect_to_db('snavi'))
        text = parse_message_from_db(resault)
        if len(resault) > 0:
            context.bot.send_message(chat_id=chat.id, text=text)
        else:
            context.bot.send_message(chat_id=chat.id, text='По Вашему запросу данных нет🤷🏻‍♂️')


def on_update(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Обновляю данные...⏳')
    cf.Dispatcher_dict_m1 = get_update_dispatcher_data('m1')
    cf.Dispatcher_dict_m3 = get_update_dispatcher_data('m3')
    if len(cf.Dispatcher_dict_m1) > 0 and len(cf.Dispatcher_dict_m3) > 0:
        context.bot.send_message(chat_id=chat.id, text='Данные обновлены✅')

def on_start(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='Привет.\n' + chat.first_name + ' , чем могу быть полезен 🥷')
    if check_user('users', chat.id) == 0:
        add_user(chat, context, "214265986")

def on_help(update, context):
    chat = update.effective_chat
    if check_user('users', chat.id) == 0:
        add_user(chat, context, "214265986")
    else:
        context.bot.send_message(chat_id=chat.id, text='\
/start - просто поздороваться))\n\
/help - список всех комманд\n\
/upd - обновление данных с папки Dispatcher\n\
/atg - добавить приборы в Чужие\n\
/ag - получить информацию о настройка прибора\n\
👉 - Можете отправить мне номер прибора котрый нужно проверить. В номере должно быть семь цифр')
     

def on_message(update, context):
    res_mess = ''
    chat = update.effective_chat
    text = update.message.text
    if check_user('users', chat.id) == 0:
         add_user(chat, context, "214265986")
    else:
        try:
            print(text)
            if re.fullmatch(r'\d{7}$', text):
                number = text
                print(number)
                context.bot.send_message(chat_id=chat.id, text=(text2 + ' ' + text + ' 🔄👨🏻‍💻'))
                res_mess += check_data_on_server('m3', number)
                res_mess += check_data_on_server('m1', number)
                context.bot.send_message(chat_id=chat.id, text=(text4 + res_mess))
            else:
                print('Error in on_message')
                context.bot.send_message(chat_id=chat.id, text='Укажите корректно номер прибора❗️')
        except:
            context.bot.send_message(chat_id=chat.id, text=text1)



def handlers(dispatcher):
    
    dispatcher.add_handler(CommandHandler("start", on_start))
    dispatcher.add_handler(CallbackQueryHandler(adm_menu.add_buttons))
    dispatcher.add_handler(CommandHandler("atg", bot_utils.add_to_atg))
    dispatcher.add_handler(CommandHandler("help", on_help))
    dispatcher.add_handler(CommandHandler("upd", on_update))
    dispatcher.add_handler(CommandHandler("ag", on_ag))
    dispatcher.add_handler(MessageHandler(Filters.user(user_set) | Filters.text | Filters.document.category("text"), on_message))


def main():
    print("Бот запущен. Нажмите Ctrl+C для завершения")
    cf.Dispatcher_dict_m1 = get_update_dispatcher_data('m1')
    cf.Dispatcher_dict_m3 = get_update_dispatcher_data('m3')
    updater = Updater(cf.TOKEN, use_context=True)
    handlers(updater.dispatcher)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()