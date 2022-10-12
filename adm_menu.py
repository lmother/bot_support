from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def add_user_in(file, level, user_id, user_name):
    try:
        with open(file, 'a', encoding='utf-8') as f:
                f.write(str(user_id) + ' ' + str(user_name) + ' ' 
                + level + '\n')
    except:
            print(f'Ошибка записи пользователя в файл: {file}')

def admin_menu(context, id, new_user_id, user_name):
    keyboard = [
        [
            InlineKeyboardButton("add_admin", callback_data='1:' + new_user_id + ':' + user_name),
            InlineKeyboardButton("allow", callback_data='2:' + new_user_id + ':' + user_name),
            InlineKeyboardButton("deny", callback_data='0:' + new_user_id + ':' + user_name),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id = id, text = '🧐 Что будем делать с новым пользователем:', reply_markup=reply_markup)


def add_buttons(update, _):
    query = update.callback_query
    variant = query.data.split(':')
    chat = update.effective_chat
    query.answer()
    if len(variant) < 3:
        print('Мало информации о новом пользователе')
        return
    if variant[0] == '1':
        add_user_in('users', '1', variant[1], variant[2])
        query.edit_message_text(text='Пользователь добавлен как админ')
    if variant[0] == '2':
        add_user_in('users', '2', variant[1], variant[2])
        query.edit_message_text(text='Пользователь добавлен 🤓')
    else:
        add_user_in('b_list', '0', variant[1], variant[2])
        query.edit_message_text(text='Пользователь добавлен в черный список ☠️')
