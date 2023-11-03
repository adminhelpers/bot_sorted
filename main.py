import telebot
from requests import get
from telebot import types
from pymongo import MongoClient
import time
import subprocess
from datetime import datetime, date, timedelta
import os
import traceback


cluster = MongoClient("mongodb+srv://dollarbaby:dollarbabys1703@cluster0.emygmrh.mongodb.net/?retryWrites=true&w=majority")
db = cluster["Cluster0"]
data_base = db["sclud"]

bot = telebot.TeleBot('5515463608:AAFmyO9G-3Sk9JtUJVmpwOuPdJxgPoopFrM')

@bot.message_handler(commands=['start']) # /start
def start_message(message):
    if data_base.count_documents({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}) == 0:
        data_base.insert_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id,
                                "index_send": [], "name_tag": [], "index_list_tag": "None",
                               "stephandler": 1, "tovar": "None", "data": "None", "dataset": []})
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    for i in index_send:
        try:
            bot.delete_message(message.chat.id, i)
        except:
            print(f"[DEBUG#262]: Сообщение [{i}] было удалено р`аньше.")
    data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})

    markup_inline = types.InlineKeyboardMarkup()
    item_one = types.InlineKeyboardButton(text='Взаимодействие', callback_data='info')

    markup_inline.add(item_one)
    bot.delete_message(message.chat.id, message.id)
    bot.send_message(message.chat.id, '* Бот активирован | ▪*\n\n'
                          'Для начала работы используй кнопку *взаимодействия*\n', parse_mode = "Markdown", reply_markup = markup_inline)

@bot.message_handler(commands=['setadmin'])
def get_message_admin_set(message):
    message_text = message.text.split(' ')
    bot.delete_message(message.chat.id, message.id)
    if '@' in message_text[1].split()[0]:
        markup_inline = types.InlineKeyboardMarkup()
        item_one = types.InlineKeyboardButton(text='Назначить', callback_data='access_on')
        item_two = types.InlineKeyboardButton(text='Разжаловать', callback_data='access_off')

        markup_inline.add(item_one, item_two)
        access_message = bot.send_message(message.chat.id, 'Система автоматического доступа | ▪\n\n'
                                                            f'Какое действие необходимо выполнить с правами администратора для пользователя {message_text[1]}?\n',
                                                            reply_markup = markup_inline)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        index_send.append(access_message.id)
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": index_send}})

        name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]
        name_tag.append(message_text[1])
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"name_tag": name_tag}})
    else:
        delete_message = bot.send_message(message.chat.id, text='Команда использована не правильно.')
        time.sleep(3)
        bot.delete_message(delete_message.chat.id, delete_message.id)

@bot.message_handler(content_types=['text']) #[i for i in  Обработчик сообщения
def send_text(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]
    if message.text.lower() == 'привет': bot.send_message(message.chat.id, 'Приветик)')

    if message.text.lower() == 'взаимодействие':
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try:
                bot.delete_message(message.chat.id, i)
            except:
                print(f"[DEBUG#262]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                             {"$set": {"index_send": [], "name_tag": [], "index_list_tag": "None",
                                       "stephandler": 1, "tovar": "None", "data": "None", "dataset": []}})
        if not message.from_user.id in data_base.find_one({"type": "access"})["ids"] and not message.from_user.username in data_base.find_one({"type": "access"})["tags"]:
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            item_activity = types.KeyboardButton('Взаимодействие')
            markup_reply.add(item_activity)
            bot.delete_message(message.chat.id, message.id)
            error_permissions = bot.send_message(message.chat.id, '⚠ Ошибка прав доступа\n\nВзаимодействие с ботом доступно только администратору.',
                                            parse_mode = "Markdown", reply_markup=markup_reply)
            time.sleep(10)
            bot.delete_message(error_permissions.chat.id, error_permissions.id)
        else:
            bot.delete_message(message.chat.id, message.id)
            markup_inline = types.InlineKeyboardMarkup()
            item_add = types.InlineKeyboardButton(text='Продано', callback_data='cell')
            markup_inline.add(item_add)
            item_edit = types.InlineKeyboardButton(text='Добавить на склад', callback_data='add')
            markup_inline.add(item_edit)
            item_delete = types.InlineKeyboardButton(text='Статистика', callback_data='stats')
            markup_inline.add(item_delete)
            dates = [f'  » *{i["name"]}* - *{i["count"]} шт.*\n' for i in data_base.find({"type": "товар"})]
            string_date = 'Отсутствует;' if len(dates) == 0 else ''.join(dates)
            auto_mark = bot.send_message(message.chat.id, '*Перечень товаров:*\n\n'
                                                              f'{string_date}', parse_mode= "Markdown", reply_markup = markup_inline)

@bot.callback_query_handler(func=lambda call: True) # Ответы на инлайны
def answer(call):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["name_tag"]]
    index_list_tag = data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_list_tag"]
    stephandler = data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["stephandler"]
    tovar = data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["tovar"]
    data = data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["data"]
    dataset = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["dataset"]]

    chat_id = []
    chat_id.append(call.message.chat.id)
    chat_id.append(f'Пользовательская сторона ошибки:\n\n'
                   f'CALL DATA: {call.data}\n'
                   f'FROM USER: {call.from_user.username} [ID: {call.from_user.id}]\n'
                   f'TIME: {time.strftime("%d.%m.%Y || %H:%M:%S")}')
    try:
        # Информация по взаимодействию
        if call.data == 'info':
            if not call.from_user.id in data_base.find_one({"type": "access"})["ids"] and not call.from_user.username in data_base.find_one({"type": "access"})["tags"]:
                bot.answer_callback_query(callback_query_id=call.id,
                                          text='⚠ Ошибка прав доступа\n\nВзаимодействие с ботом доступно только администратору.', show_alert=True)
            else:
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"index_send": [], "name_tag": []}})
                markup_inline = types.InlineKeyboardMarkup()
                item_add = types.InlineKeyboardButton(text='Продано', callback_data='cell')
                markup_inline.add(item_add)
                item_edit = types.InlineKeyboardButton(text='Добавить на склад', callback_data='add')
                markup_inline.add(item_edit)
                item_delete = types.InlineKeyboardButton(text='Статистика', callback_data='stats')
                markup_inline.add(item_delete)
                dates = [f'  » *{i["name"]}* - *{i["count"]} шт.*\n' for i in data_base.find({"type": "товар"})]
                string_date = "Отсутствует;" if len(dates) == 0 else ''.join(dates)
                auto_mark = bot.send_message(call.message.chat.id, '*Перечень товаров:*\n\n'
                                                                  f'{string_date}', parse_mode= "Markdown", reply_markup = markup_inline)
                time.sleep(30)
                try:
                    bot.delete_message(auto_mark.chat.id, auto_mark.id)
                except:
                    print(f"[DEBUG#142]: Сообщение было удалено раньше.")

        if call.data == 'add':
            bot.delete_message(call.message.chat.id, call.message.id)
            dates = [f'  » *{i["name"]}* - *{i["count"]} шт.*\n' for i in data_base.find({"type": "товар"})]
            string_date = ''.join(dates)
            if not len(dates) == 0:
                add_step = bot.send_message(call.message.chat.id, '▪ *| Добавление товара в перечень*\n'
                                                                 f'Список товаров на прилавке:\n{string_date}\nУкажите название товара:\n'
                                                                  'Для того что бы отменить действие, введите  *Отмена*', parse_mode = "Markdown")
            else:
                add_step = bot.send_message(call.message.chat.id,f'▪ *| Добавление товара в перечень*\n'
                                                                   f'Укажите название товара\n\n'
                                                                   f'Для того что бы отменить действие, введите *Отмена*', parse_mode = "Markdown")
            bot.register_next_step_handler(add_step, add_count_function)
            index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            index_send.append(add_step.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": index_send}})

        if call.data == 'cell':
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"name_tag": []}})
            bot.delete_message(call.message.chat.id, call.message.id)
            dates = [f'  » *{i["name"]}* - *{i["count"]} шт.*\n' for i in data_base.find({"type": "товар"})]
            string_date = ''.join(dates)
            if not len(dates) == 0:
                index_list_tag = call.data
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                     {"$set": {"index_list_tag": call.data}})
                markup_inline = types.InlineKeyboardMarkup()
                k_index, j_index, i_indexes = 0, 0, []
                array_data = [data["name"] for data in data_base.find({"type": "товар"})]
                if len(array_data) >= (9*stephandler - 9):
                    for i in range(0, 9):
                        while k_index != 9:
                            while j_index != 3:
                                if k_index == len(array_data): break
                                else:
                                    if len(array_data) == 1: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index-1]}', callback_data=f'{array_data[k_index-1]}')
                                    else: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index]}', callback_data=f'{array_data[k_index]}')
                                    j_index += 1
                                    k_index += 1
                                    i_indexes.append(item_add)
                            j_index = 0
                            try:
                                markup_inline.add(i_indexes[0], i_indexes[1], i_indexes[2])
                            except:
                                try:  markup_inline.add(i_indexes[0], i_indexes[1])
                                except:
                                    try: markup_inline.add(i_indexes[0])
                                    except: break
                            i_indexes = []
                    if len(array_data) > 0:
                        item_add = types.InlineKeyboardButton(text=f'По всем товарам', callback_data=f'все товары')
                        markup_inline.add(item_add)
                    if len(array_data) > 9:
                        next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                        markup_inline.add(next_step)
                next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
                markup_inline.add(next_step)
                add_step = bot.send_message(call.message.chat.id, '▪ *| Удаление товара*\n'
                                                                  f'Список товаров на прилавке:\n{string_date}\nУкажите название товара.\n'
                                                                  'Для того что бы отменить действие, введите  *Отмена*',
                                                                  parse_mode="Markdown", reply_markup=markup_inline)
                index_send = [i for i in
                              data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
                index_send.append(add_step.id)
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"index_send": index_send}})
                dataset = [i for i in
                              data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["dataset"]]
                dataset.append(call.data)
                dataset.append(add_step)
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                     {"$set": {"index_send": dataset}})
                #bot.register_next_step_handler(add_step, cell_count_function)
            else:
                add_step = bot.send_message(call.message.chat.id, f'▪ *| Удаление товара*\n'
                                                                  f'Удаление товара невозможно, так как список пуст.\n\n',
                                                                  parse_mode="Markdown")
                time.sleep(10)
                bot.delete_message(add_step.chat.id, add_step.id)

        if call.data in ["yes_cell", "no_cell"]:
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            item_activity = types.KeyboardButton('Взаимодействие')
            markup_reply.add(item_activity)
            if call.data == "yes_cell":
                for i in data_base.find({"type": "товар"}):
                    if i["name"].lower() == name_tag[0].lower():
                        if int(i["count"]) - int(name_tag[1]) == 0:
                            data_base.delete_one({"_id": i["_id"]})
                        else:
                            data_base.update_one({"_id": i["_id"]}, {"$set": {"count": int(i["count"]) - int(name_tag[1])}})
                        add_step = bot.send_message(call.message.chat.id, '▪ *| Удаление товара*\n'
                                                                     f'Вы убрали *{name_tag[1]} единиц* товара *"{name_tag[0]}"* со склада.\n'
                                                                     f'Указанная сумма за продажу: *{name_tag[2]} рублей*',
                                                                     parse_mode="Markdown", reply_markup=markup_reply)
                        year = time.strftime("%Y")
                        month = time.strftime("%m")
                        day = time.strftime("%d")
                        id = int(year) * 365
                        month2 = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
                        month_id = 0
                        for i in range(1, int(month) + 1): month_id += int(month2[i])
                        id += month_id
                        id += int(day)
                        times = time.strftime("%H:%M:%S")
                        data_base.insert_one({"type": "stats", "name": name_tag[0].lower(), "moution": "remove", "count": int(name_tag[1]),
                                              "year": year, "month": month, "day": day, "id": id, "action": int(name_tag[2]),
                                              "time": times, "autor": f'{call.from_user.username} [ID: {call.from_user.id}]',
                                              "datetime": f'{time.strftime("%d.%m.%Y")}'})
                        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
                        for i in index_send:
                            try: bot.delete_message(call.message.chat.id, i)
                            except: print(f"[DEBUG#149]: Сообщение[{i}] было удалено раньше.")
                        data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set":
                                                                                                           {"index_send": [], "name_tag": []}})
                        time.sleep(10)
                        bot.delete_message(add_step.chat.id, add_step.id)
                        break
            else:
                add_step = bot.send_message(call.message.chat.id, '▪ *| Удаление товара*\n'
                                                                  f'Действие отменено, сессия завершена',
                                                                  parse_mode="Markdown", reply_markup=markup_reply)
                index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
                for i in index_send:
                    try: bot.delete_message(call.message.chat.id, i)
                    except: print(f"[DEBUG#161]: Сообщение [{i}] было удалено раньше.")
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"index_send": [], "name_tag": []}})
                time.sleep(10)
                bot.delete_message(add_step.chat.id, add_step.id)

        if call.data in ['access_on', 'access_off']:
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"tovar": call.data}})
            data = 'аннулировать' if call.data == 'access_off' else 'активировать'

            markup_inline = types.InlineKeyboardMarkup()
            item_one = types.InlineKeyboardButton(text='Подтвердить', callback_data='access_yes')
            item_two = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')

            markup_inline.add(item_one, item_two)

            access_send = bot.send_message(call.message.chat.id, '* Система автоматического доступа | ▪*\n\n'
                              f'Подтвердите действие: *{data} права администратора пользователю*?\n',
                              parse_mode = "Markdown", reply_markup = markup_inline)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            index_send.append(access_send.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"index_send": index_send}})

        if call.data == 'access_yes':
            tags = [i for i in data_base.find_one({"type": "access"})["tags"]]
            if tovar == "access_off":
                tags.remove(name_tag[0].replace("@", ""))
            else: tags.append(name_tag[0].replace("@", ""))
            data_base.update_one({"type": "access"}, {"$set": {"tags": tags}})
            yes_access = bot.send_message(call.message.chat.id, '* Система автоматического доступа | ▪*\n\n'
                              f'Действие: *{data} права администратора пользователю успешно выполнено*\n',
                              parse_mode = "Markdown")
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            for i in index_send:
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    print(f"[DEBUG#308]: Сообщение [{i}] было удалено раньше.")
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": [], "name_tag": [], "tovar": "None", "data": "None"}})
            time.sleep(10)
            bot.delete_message(yes_access.chat.id, yes_access.id)

        if call.data == 'stats':
            markup_inline = types.InlineKeyboardMarkup()
            item_add = types.InlineKeyboardButton(text='День', callback_data='day')
            markup_inline.add(item_add)
            item_edit = types.InlineKeyboardButton(text='Неделя', callback_data='week')
            markup_inline.add(item_edit)
            item_delete = types.InlineKeyboardButton(text='Месяц', callback_data='moon')
            markup_inline.add(item_delete)

            next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup_inline.add(next_step)
            stats_message = bot.send_message(call.message.chat.id, '▪ *| Статистика*\nВыберите период, за который нужно показать статистику.\n\n'
                                                                   'Для отмены используйте "*Отмена*"',
                                                                    parse_mode="Markdown", reply_markup=markup_inline)
            index_send.append(stats_message.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"index_send": index_send}})

        if call.data in ['day', 'week', 'moon']:
            array_check = []
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_list_tag": call.data}})
            markup_inline = types.InlineKeyboardMarkup()
            k_index, j_index, i_indexes = 0, 0, []
            array_data = [data["name"] for data in data_base.find({"type": "товар"})]
            for data in data_base.find({"type": "stats"}):
                if not data["name"] in array_data:
                    array_data.append(data["name"])
            if len(array_data) >= (9*stephandler - 9):
                for i in range(0, 9):
                    while k_index != 9:
                        while j_index != 2:
                            if k_index == len(array_data): break
                            if len(array_data) == 1:
                                item_add = types.InlineKeyboardButton(text=f'{array_data[k_index-1]}', callback_data=f'{array_data[k_index-1]}')
                                array_check.append(array_data[k_index-1])
                            else:
                                item_add = types.InlineKeyboardButton(text=f'{array_data[k_index]}', callback_data=f'{array_data[k_index]}')
                                array_check.append(array_data[k_index])
                            j_index += 1
                            k_index += 1
                            i_indexes.append(item_add)
                        j_index = 0
                        try:
                            markup_inline.add(i_indexes[0], i_indexes[1], i_indexes[2])
                        except:
                            try:  markup_inline.add(i_indexes[0], i_indexes[1])
                            except:
                                try: markup_inline.add(i_indexes[0])
                                except: break
                        i_indexes = []
                if len(array_data) > 0:
                        item_add = types.InlineKeyboardButton(text=f'По всем товарам', callback_data=f'все товары')
                        markup_inline.add(item_add)

                if len(array_data) > 9:
                    next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                    markup_inline.add(next_step)

            next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup_inline.add(next_step)
            stats_message = bot.send_message(call.message.chat.id, '▪ *| Статистика*'
                                                                   '\nУкажите товар из списка, по которому нужна статистика.\n\n'
                                                                   'Для отмены используйте "*Отмена*"',
                                                                   parse_mode="Markdown", reply_markup=markup_inline)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            index_send.append(stats_message.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": index_send}})
            #bot.register_next_step_handler(stats_message, stats_day_function)

        if call.data == 'next_step':
            stephandler += 1
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"stephandler": stephandler}})
            markup_inline = types.InlineKeyboardMarkup()
            k_index, j_index, i_indexes = 0, 0, []
            array_data = [data["name"] for data in data_base.find({"type": "товар"})]
            for data in data_base.find({"type": "stats"}):
                if not data["name"] in array_data:
                    array_data.append(data["name"])

            n = 0
            for i in range(0, 9*stephandler + 1):
                if n == 1: break
                if i >= (9 * stephandler - 9) and i < 9*stephandler:
                    k_index = i
                    while k_index <= 9*stephandler:
                        if n == 1: break
                        while j_index != 2:
                            if k_index == len(array_data):
                                n = 1
                                break
                            if len(array_data) == 1: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index-1]}', callback_data=f'{array_data[k_index-1]}')
                            else: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index]}', callback_data=f'{array_data[k_index]}')
                            j_index += 1
                            k_index += 1
                            i_indexes.append(item_add)
                        j_index = 0
                        try:
                            markup_inline.add(i_indexes[0], i_indexes[1], i_indexes[2])
                        except:
                            try:  markup_inline.add(i_indexes[0], i_indexes[1])
                            except:
                                try: markup_inline.add(i_indexes[0])
                                except: break
                        i_indexes = []
            array_data = []

            if len(array_data) > 0:
                item_add = types.InlineKeyboardButton(text=f'По всем товарам', callback_data=f'все товары')
                markup_inline.add(item_add)
            if k_index < len(array_data) and stephandler != 1:
                prew_step = types.InlineKeyboardButton(text='Предыдущая страница', callback_data='prew_step')
                next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                markup_inline.add(prew_step, next_step)
            else:
                if k_index < len(array_data):
                    next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                    markup_inline.add(next_step)
                if stephandler != 1:
                    next_step = types.InlineKeyboardButton(text='Предыдущая страница', callback_data='prew_step')
                    markup_inline.add(next_step)

            next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup_inline.add(next_step)
            dell = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='▪ *| Статистика*'
                                                                   '\nУкажите название товара из списка, по которому нужна статистика.\n\n'
                                                                   'Для отмены используйте "*Отмена*"',
                                                                   parse_mode="Markdown", reply_markup=markup_inline)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            index_send.append(dell.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": index_send}})

        if call.data == 'prew_step':
            stephandler -= 1
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id}, {"$set": {"stephandler": stephandler}})
            markup_inline = types.InlineKeyboardMarkup()
            k_index, j_index, i_indexes = 0, 0, []
            array_data = [data["name"] for data in data_base.find({"type": "товар"})]
            for data in data_base.find({"type": "stats"}):
                if not data["name"] in array_data:
                    array_data.append(data["name"])

            n = 0
            for i in range(0, 9*stephandler + 1):
                if i >= (9 * stephandler - 9) and i <= 9*stephandler:
                    k_index = i
                    while k_index <= 9*stephandler-1:
                        if n == 1: break
                        while j_index != 2:
                            if k_index == 9*stephandler-1:
                                n = 1
                            if len(array_data) == 1: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index-1]}', callback_data=f'{array_data[k_index-1]}')
                            else: item_add = types.InlineKeyboardButton(text=f'{array_data[k_index]}', callback_data=f'{array_data[k_index]}')
                            j_index += 1
                            k_index += 1
                            i_indexes.append(item_add)
                        j_index = 0
                        markup_inline.add(i_indexes[0], i_indexes[1], i_indexes[2])
                        i_indexes = []

            array_data = []

            if len(array_data) > 0:
                item_add = types.InlineKeyboardButton(text=f'По всем товарам', callback_data=f'все товары')
                markup_inline.add(item_add)
            if k_index < len(array_data) and stephandler != 1:
                prew_step = types.InlineKeyboardButton(text='Предыдущая страница', callback_data='prew_step')
                next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                markup_inline.add(prew_step, next_step)
            else:
                if k_index < len(array_data):
                    next_step = types.InlineKeyboardButton(text='Следущая страница', callback_data='next_step')
                    markup_inline.add(next_step)
                if stephandler != 1:
                    next_step = types.InlineKeyboardButton(text='Предыдущая страница', callback_data='prew_step')
                    markup_inline.add(next_step)
            next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
            markup_inline.add(next_step)
            dell = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='▪ *| Статистика*'
                                                                   '\nУкажите название товара из списка, по которому нужна статистика.\n\n'
                                                                   'Для отмены используйте "*Отмена*"',
                                                                   parse_mode="Markdown", reply_markup=markup_inline)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            index_send.append(dell.id)
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": index_send}})

        if call.data == 'cancel':
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            for i in index_send:
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    print(f"[DEBUG#513]: Сообщение [{i}] было удалено раньше.")
            index_send, name_tag = [], []
            tovar = "None"
            index_list_tag = "None"
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set":
                                      {"index_send": [], "name_tag": [], "tovar": "Mone", "index_list_tag": "None"}})

        mons = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

        if call.data in [data["name"] for data in data_base.find({"type": "товар"})] or call.data == 'все товары':
            if len(dataset) >= 1:
                dell = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='▪ *| Удаление товара*\n\n'
                                                             f'Укажите количество товара "*{call.data}*" которое было продано\n'
                                                             f'*Пример:* 5\n'
                                                             f'Для того что бы отменить действие, введи *Отмена*',
                                                            parse_mode="Markdown")
                name_tag.append(call.data)
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                     {"$set": {"name_tag": name_tag}})
                bot.register_next_step_handler(dell, cell_count_function_step)
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                     {"$set": {"dataset": []}})
            else:
                data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                     {"$set": {"stephandler": 1, "tovar": call.data}})
                if index_list_tag == "day":
                    stats_message = bot.send_message(call.message.chat.id, '▪ *| Статистика*'
                                                                          '\nУкажите день, за который нужно показать статистику.\n\n*Пример:* 04.07.2023\n'
                                                                          'Для отмены используйте "*Отмена*"',
                                                                          parse_mode="Markdown")
                    bot.register_next_step_handler(stats_message, stats_day_function_date)

                    index_send = [i for i in
                                  data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})[
                                      "index_send"]]
                    index_send.append(stats_message.id)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"index_send": index_send}})
                    name_tag.append(call.data)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"name_tag": name_tag, "index_list_tag": "None"}})

                if index_list_tag == "week":
                    markup_inline = types.InlineKeyboardMarkup()
                    item_add = types.InlineKeyboardButton(text='Неделю назад', callback_data='oneweek')
                    markup_inline.add(item_add)
                    item_edit = types.InlineKeyboardButton(text='Две недели назад', callback_data='twoweek')
                    markup_inline.add(item_edit)
                    item_delete = types.InlineKeyboardButton(text='Три недели назад', callback_data='threeweek')
                    markup_inline.add(item_delete)
                    item_delete = types.InlineKeyboardButton(text='Четыре недели назад', callback_data='fourweek')
                    markup_inline.add(item_delete)
                    next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
                    markup_inline.add(next_step)
                    stats_message = bot.send_message(call.message.chat.id, '▪ *| Статистика*'
                                                                          '\nУкажите период, за который нужно показать статистику.\n'
                                                                          'Для отмены используйте "*Отмена*"',
                                                                          parse_mode="Markdown", reply_markup=markup_inline)
                    index_send = [i for i in
                                  data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})[
                                      "index_send"]]
                    index_send.append(stats_message.id)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"index_send": index_send}})
                    name_tag.append(call.data)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"name_tag": name_tag, "index_list_tag": "None"}})

                if index_list_tag == "moon":
                    month = time.strftime("%m")
                    markup_inline = types.InlineKeyboardMarkup()
                    array_add_mon = []
                    for i in range(1, int(month)):
                        item_add = types.InlineKeyboardButton(text=f'{mons[i - 1]}', callback_data=f'{mons[i - 1]}')
                        if not i % 2 == 0:
                            array_add_mon.append(item_add)
                        else:
                            markup_inline.add(array_add_mon[0], item_add)
                            array_add_mon = []
                    if len(array_add_mon) == 1:
                        markup_inline.add(array_add_mon[1])
                    item_add = types.InlineKeyboardButton(text=f'Этот месяц', callback_data=mons[int(time.strftime("%m")) - 1])
                    markup_inline.add(item_add)

                    next_step = types.InlineKeyboardButton(text='Отмена', callback_data='cancel')
                    markup_inline.add(next_step)
                    stats_message = bot.send_message(call.message.chat.id, '▪ *| Статистика*'
                                                                          '\nУкажите месяц, за который нужно показать статистику.\n\n'
                                                                          'Для отмены используйте "*Отмена*"',
                                                                          parse_mode="Markdown", reply_markup=markup_inline)
                    index_send = [i for i in
                                  data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})[
                                      "index_send"]]
                    index_send.append(stats_message.id)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"index_send": index_send}})
                    name_tag.append(call.data)
                    data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                         {"$set": {"name_tag": name_tag, "index_list_tag": "None"}})

        if call.data in mons:
            number_moon = mons.index(call.data) + 1
            month_id = int(time.strftime("%m"))

            number_moon = mons.index(call.data) + 1
            month2 = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
            mons_number = mons.index(call.data) + 1
            if call.data == mons[month_id + 1]:
                number_moon = month_id
                year = time.strftime("%Y")
                month = number_moon
                day = 1
                id_action = int(year) * 365
                month_id = 0
                for i in range(1, int(month) + 1): month_id += month2[i]
                id_action += month_id
                id_action += int(day)
                day_2 = time.strftime("%d")
                id_actual = int(id_action) - int(day_2)

            else:
                year = time.strftime("%Y")
                month = number_moon
                day = 1
                id_action = int(year) * 365
                month_id = 0
                for i in range(1, int(month) + 1): month_id += month2[i]
                id_action += month_id
                id_action += int(day)

                year = time.strftime("%Y")
                month = number_moon + 1
                day = 1
                id_actual = int(year) * 365
                month_id = 0
                for i in range(1, int(month) + 1): month_id += month2[i]
                id_actual += month_id
                id_actual += int(day)


            obfile = open(f'статистика-за-{call.data}={call.from_user.id}.txt', 'w', encoding='utf-8')
            obfile.write(f'[System]: Запрос статистики за {call.data} по товару "{tovar}".\n\n')
            all_cell_count, all_cell_money, all_add_count = 0, 0, 0
            all_cell_count_s, all_cell_money_s, all_add_count_s = 0, 0, 0
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0
            obfile.write(
                f'\n--------------------------\n\n[System]: Лог добавления товара "{tovar}" на склад за {call.data}:\n\n')
            for date in range(id_action, id_actual + 1):
                if tovar == 'все товары':
                    for tovars in data_base.find({"type": "stats", "moution": "add", "id": date}):
                        for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "add", "id": date}):
                            obfile.write(
                                f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}\n')
                            all_add_one += int(i["count"])
                            all_add_count += int(i["count"])
                        if not all_add_one == 0:
                            obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                                     f'[Всего добавлено товара "{tovars["name"]}" за день]: {all_add_one} единиц\n\n.')
                        all_add_one = 0
                else:
                    for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "add", "id": date}):
                        obfile.write(f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара пользователем {i["autor"]}\n')
                        all_add_count += int(i["count"])
                    if not all_add_count == 0:
                        obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                                     f'[Добавлено за день]: {all_add_count} единиц товара;')

            obfile.write(
                f'\n\n--------------------------\n\n[System]: Лог продажи товара *{tovar}* со склада за {call.data}:\n\n')
            for date in range(id_action, id_actual + 1):
                if tovar == 'все товары':
                    for tovars in data_base.find({"type": "stats", "moution": "remove", "id": date}):
                        for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "remove", "id": date}):
                            obfile.write(
                                f'[{i["datetime"]} | {i["time"]}]: Убрано {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                            all_cell_count += int(i["count"])
                            all_cell_money += int(i["action"])
                            all_cell_one += int(i["count"])
                            all_cell_sone += int(i["action"])
                        if not all_cell_one == 0:
                            obfile.write(f'[Всего продано товара "{tovars["name"]}" за день {i["datetime"]}]: {all_cell_one} единиц на сумму {all_cell_sone}.\n\n')
                        all_cell_one, all_cell_sone = 0, 0
                else:
                    for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "remove", "id": date}):
                        obfile.write(
                            f'[{i["datetime"]} | {i["time"]}]: Убрано {i["count"]} единиц товара пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                        all_cell_count += int(i["count"])
                        all_cell_money += int(i["action"])
                    if not all_cell_count == 0:
                        obfile.write(f'\n[System]: Общая статистика в цифрах за {call.data}:\n'
                                 f'[Продано за день]: {all_cell_count} единиц товара\n'
                                 f'[Общая сумма с проданного товара за день]: {all_cell_money}')

                    obfile.write(f'\n\n--------------------------\n\n')
                all_add_count_s += all_add_count
                all_cell_money_s += all_cell_money
                all_cell_count_s += all_cell_count
                all_cell_count, all_cell_money, all_add_count = 0, 0, 0
            obfile.write(f'[System]: Общая статистика в цифрах за {call.data}:\n'
                         f'[Добавлено ВСЕГО]: {all_add_count_s} единиц товара;\n'
                         f'[Продано ВСЕГО]: {all_cell_count_s} единиц товара\n'
                         f'[Общая сумма с проданного товара]: {all_cell_money_s}\n\n')
            obfile.write(f'[System]: Файл закрыт за отсутствием статистических данных.')
            obfile.close()
            bot.send_document(call.message.chat.id, open(f'статистика-за-{call.data}={call.from_user.id}.txt', 'rb'))
            os.remove(f'статистика-за-{call.data}={call.from_user.id}.txt')
            all_cell_count_s, all_cell_money_s, all_add_count_s = 0, 0, 0
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0
            index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            for i in index_send:
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    print(f"[DEBUG#203]: Сообщение [{i}] было удалено раньше.")
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"index_send": [], "name_tag": []}})

        if call.data in ['oneweek', 'twoweek', 'threeweek', 'fourweek']:
            year = time.strftime("%Y")
            month = time.strftime("%m")
            day = time.strftime("%d")
            id = int(year) * 365
            month2 = {1: 31, 2:28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
            month_id = 0
            for i in range(1, int(month) + 1): month_id += month2[i]
            id += month_id
            id += int(day)

            if call.data == 'oneweek':
                id_action = int(id) - 7
                id_actual = int(id)
            if call.data == 'twoweek':
                id_action = int(id) - 14
                id_actual = int(id) - 7
            if call.data == 'treeweek':
                id_action = int(id) - 21
                id_actual = int(id) - 14
            if call.data == 'fourweek':
                id_action = int(id) - 28
                id_actual = int(id) - 21

            deshif = {"oneweek": "прошлую неделю",
                     "twoweek": "2 недели назад",
                     "treeweek": "2 недели назад",
                     "fourweek": "2 недели назад"}

            obfile = open(f'статистика-за-{deshif[call.data].replace(" ", "-")}={call.from_user.id}.txt', 'w', encoding='utf-8')
            obfile.write(f'[System]: Запрос статистики за {deshif[call.data]} по товару "{tovar}".\n\n')
            all_cell_count, all_cell_money, all_add_count = 0, 0, 0
            all_cell_count_s, all_cell_money_s, all_add_count_s = 0, 0, 0
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0
            obfile.write(f'\n--------------------------\n\n[System]: Лог добавления товара "{tovar}" на склад за {deshif[call.data]}:\n\n')
            for date in range(id_action, id_actual+1):
                if tovar == 'все товары':
                    for tovars in data_base.find({"type": "stats", "moution": "add", "id": date}):
                        for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "add", "id": date}):
                            obfile.write(f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}\n')
                            all_add_one += int(i["count"])
                            all_add_count += int(i["count"])
                        if not all_add_one == 0:
                            obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                                        f'[Всего добавлено товара "{tovars["name"]}" за день]: {all_add_one} единиц\n\n.')
                        all_add_one = 0
                else:
                    for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "add", "id": date}):
                        obfile.write(f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара пользователем {i["autor"]}\n')
                        all_add_count += int(i["count"])
                    if not all_add_count == 0:
                        obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                             f'[Добавлено за день]: {all_add_count} единиц товара;')

                    obfile.write(f'\n\n--------------------------\n\n[System]: Лог продажи товара *{tovar}* со склада за {deshif[call.data]}:\n\n')
            for date in range(id_action, id_actual+1):
                if tovar == 'все товары':
                    for tovars in data_base.find({"type": "stats", "moution": "remove", "id": date}):
                        for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "remove", "id": date}):
                            obfile.write(f'[{i["datetime"]} | {i["time"]}]: Убрано {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                            all_cell_count += int(i["count"])
                            all_cell_money += int(i["action"])
                            all_cell_one += int(i["count"])
                            all_cell_sone += int(i["action"])
                        obfile.write(f'[Всего продано товара "{tovars["name"]}" за день {i["datetime"]}]: {all_cell_one} единиц на сумму {all_cell_sone}.\n\n')
                        all_cell_one, all_cell_sone = 0, 0
                else:
                    for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "remove", "id": date}):
                        obfile.write(f'[{i["datetime"]} | {i["time"]}]: Убрано {i["count"]} единиц товара пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                        all_cell_count += int(i["count"])
                        all_cell_money += int(i["action"])
                    if not all_cell_count == 0:
                        obfile.write(f'\n[System]: Общая статистика в цифрах за {deshif[call.data]}:\n'
                                 f'[Продано за день]: {all_cell_count} единиц товара\n'
                                 f'[Общая сумма с проданного товара за день]: {all_cell_money}')

                obfile.write(f'\n\n--------------------------\n\n')
                all_add_count_s += all_add_count
                all_cell_money_s += all_cell_money
                all_cell_count_s += all_cell_count
                all_cell_count, all_cell_money, all_add_count = 0, 0, 0
            obfile.write(f'[System]: Общая статистика в цифрах за {deshif[call.data]}:\n'
                         f'[Добавлено ВСЕГО]: {all_add_count_s} единиц товара;\n'
                         f'[Продано ВСЕГО]: {all_cell_count_s} единиц товара\n'
                         f'[Общая сумма с проданного товара]: {all_cell_money_s}\n\n')
            obfile.write(f'[System]: Файл закрыт за отсутствием статистических данных.')
            obfile.close()
            bot.send_document(call.message.chat.id, open(f'статистика-за-{deshif[call.data].replace(" ", "-")}={call.from_user.id}.txt', 'rb'))
            os.remove(f'статистика-за-{deshif[call.data].replace(" ", "-")}={call.from_user.id}.txt')
            all_cell_count_s, all_cell_money_s, all_add_count_s = 0, 0, 0
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0

            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
            for i in index_send:
                try:
                    bot.delete_message(call.message.chat.id, i)
                except:
                    print(f"[DEBUG#647]: Сообщение [{i}] было удалено раньше.")
            data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                                 {"$set": {"name_tag": [], "index_send": []}})

    except Exception:
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        item_activity = types.KeyboardButton('Взаимодействие')
        markup_reply.add(item_activity)
        cancel_message = bot.send_message(chat_id[0], '*▪ Неизвестная ошибка*\n\n'
                                                   'Для безопасности и целостности данных *сессия бота была перезапущена*, отчёт об ошибке доставлен разработчику.\n\n'
                                                   'Если У Вас остались сообщения от бота, отправленные выше - *удалите их вручную*, они больше неактивны.\n'
                                                   'Вы можете *не удалять сообщение об активации бота*, так как оно всё ещё активно, в случае удаления используйте */start*.\n\n'
                                                   'Это сообщение будет *удалено автоматически*, после следущего удачного использования.\n\n'
                                                   'Используйте кнопки *взаимодействия* и повторите попытку.',
                                                    parse_mode="Markdown", reply_markup=markup_reply)
        obfile = open(f'error-{call.from_user.id}.txt', 'w', encoding='utf-8')
        obfile.write(f'[System]: Техническая информация ошибки:\n{traceback.format_exc()}\n\n{chat_id[1]}')
        obfile.close()
        bot.send_document(chat_id=532678880, document=open(f'error-{call.from_user.id}.txt', 'rb'))
        os.remove(f'error-{call.from_user.id}.txt')
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
        for i in index_send:
            try:
                bot.delete_message(chat_id[0], i)
            except:
                print(f"[DEBUG#778]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                             {"$set": {"index_send": [], "name_tag": [], "index_list_tag": "None", "stephandler": 1, "tovar": "None", "data": "None", "dataset": []}})

        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id})["index_send"]]
        index_send.append(cancel_message.id)
        data_base.update_one({"type": "async", "chat_id": call.message.chat.id, "user_id": call.from_user.id},
                             {"$set": {"index_send": index_send}})
        chat_id = []

def stats_day_function_date(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]
    tovar = data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["tovar"]

    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_activity = types.KeyboardButton('Взаимодействие')
    markup_reply.add(item_activity)
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    index_send.append(message.id)
    data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": index_send}})
    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Просмотр статистики"*',
                                          parse_mode="Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try:
                bot.delete_message(message.chat.id, i)
            except:
                print(f"[DEBUG#203]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                             {"$set": {"name_tag": [], "index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        try:
            day_struction = message.text.split('.')
            year = int(day_struction[2])
            month = int(day_struction[1])
            day = int(day_struction[0])
            date = int(year) * 365
            month2 = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
            month_id = 0
            for i in range(1, int(month) + 1): month_id += int(month2[i])
            date += month_id
            date += int(day)

            obfile = open(f'stats-{date}={message.from_user.id}.txt', 'w', encoding='utf-8')
            obfile.write(f'[System]: Запрос статистики за {message.text} по товару {tovar}.\n\n')
            all_cell_count, all_cell_money, all_add_count = 0, 0, 0
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0
            obfile.write(f'\n--------------------------\n\n[System]: Лог добавления товара "{tovar}" на склад за {message.text}:\n\n')
            if tovar == 'все товары':
                for tovars in data_base.find({"type": "stats", "moution": "add", "id": date}):
                    print('ADD +')
                    for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "add", "id": date}):
                        obfile.write(f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}')
                        all_add_one += int(i["count"])
                        all_add_count += int(i["count"])
                    if not all_add_one == 0:
                        obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                                f'[Всего добавлено товара "{tovars["name"]}" за день]: {all_add_one} единиц.\n\n')
                    all_add_one = 0
            else:
                for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "add", "id": date}):
                    obfile.write(f'[{i["datetime"]} | {i["time"]}]: Добавлено {i["count"]} единиц товара пользователем {i["autor"]}\n')
                    all_add_count += int(i["count"])
                if not all_add_count == 0:
                    obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                        f'[Добавлено за день]: {all_add_count} единиц товара;')
                all_add_one = 0


            obfile.write(f'\n\n--------------------------\n\n[System]: Лог продажи товара "{tovar}" со склада за {message.text}:\n\n')
            if tovar == 'все товары':
                for tovars in data_base.find({"type": "stats", "moution": "remove", "id": date}):
                    print('REMOVE +')
                    for i in data_base.find({"type": "stats", "name": tovars["name"], "moution": "remove", "id": date}):
                        obfile.write(f'[{i["time"]}]: Продано {i["count"]} единиц товара "{tovars["name"]}" пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                        all_cell_count += int(i["count"])
                        all_cell_money += int(i["action"])
                        all_cell_one += int(i["count"])
                        all_cell_sone += int(i["action"])
                if not all_cell_count == 0:
                    obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                             f'[Продано за день]: {all_cell_one} единиц товара\n'
                             f'[Общая сумма с проданного товара за день]: {all_cell_sone}\n\n')
                all_cell_one, all_cell_sone = 0, 0
            else:
                for i in data_base.find({"type": "stats", "name": tovar.lower(), "moution": "remove", "id": date}):
                    obfile.write(f'[{i["time"]}]: Убрано {i["count"]} единиц товара пользователем {i["autor"]}. Указанная сумма: {i["action"]} рублей\n')
                    all_cell_count += int(i["count"])
                    all_cell_money += int(i["action"])
                if not all_cell_count == 0:
                    obfile.write(f'\n[System]: Общая статистика в цифрах за {i["datetime"]}:\n'
                         f'[Продано за день]: {all_cell_count} единиц товара\n'
                         f'[Общая сумма с проданного товара за день]: {all_cell_money}')

                obfile.write(f'\n\n--------------------------\n\n')
            obfile.write(f'[System]: Общая статистика в цифрах за {message.text}:\n'
                         f'[Добавлено ВСЕГО]: {all_add_count} единиц товара;\n'
                         f'[Продано ВСЕГО]: {all_cell_count} единиц товара\n'
                         f'[Общая сумма с проданного товара]: {all_cell_money}\n\n')
            obfile.write(f'[System]: Файл закрыт за отсутствием статистических данных.')
            obfile.close()
            bot.send_document(message.chat.id, open(f'stats-{date}={message.from_user.id}.txt', 'rb'))
            os.remove(f'stats-{date}={message.from_user.id}.txt')
            all_cell_one, all_cell_sone, all_add_one = 0, 0, 0

            index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            for i in index_send:
                try:
                    bot.delete_message(message.chat.id, i)
                except:
                    print(f"[DEBUG#743]: Сообщение[{i}] было удалено раньше.")
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"name_tag": [], "index_send": []}})
            all_cell_count, all_cell_money, all_add_count = 0, 0, 0
        except:
            stats_message = bot.send_message(message.chat.id, '▪ *| Статистика*'
                                                                   '\nДата указана в неправильном формате, попробуйте снова\n\n*Пример:* 04.07.2023\n'
                                                                   'Для отмены используйте "*Отмена*"', parse_mode="Markdown")
            index_send.append(stats_message.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            bot.register_next_step_handler(stats_message, stats_day_function_date)

'''
def cell_count_function(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]
    
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_activity = types.KeyboardButton('Взаимодействие')
    markup_reply.add(item_activity)
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    index_send.append(message.id)
    data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": index_send}})
    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Удаление товара"*',
                                          parse_mode="Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try: bot.delete_message(message.chat.id, i)
            except: print(f"[DEBUG#177]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        if not message.text.lower() in [i["name"].lower() for i in data_base.find({"type": "товар"})]:
            cancel_message = bot.send_message(message.chat.id, f'▪ *| Удаление товара*\n'
                                                              f'Удаление невозможно, так как указанного товара нет в списке.\n'
                                                              f'Укажите правильное название товара.\n\n'
                                                              'Для того что бы отменить действие, введите  *Отмена*',
                                                              parse_mode="Markdown")
            bot.register_next_step_handler(cancel_message, cell_count_function)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(cancel_message.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
        else:
            add_step = bot.send_message(message.chat.id, '▪ *| Удаление товара*\n\n'
                                                         f'Укажите количество товара "*{message.text}*" которое было продано\n'
                                                         f'*Пример:* 5\n'
                                                         f'Для того что бы отменить действие, введи *Отмена*',
                                                        parse_mode="Markdown")
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(message.id)
            name_tag.append(message.text)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"name_tag": name_tag}})
            index_send.append(add_step.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            bot.register_next_step_handler(add_step, cell_count_function_step)
'''

def cell_count_function_step(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]

    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_activity = types.KeyboardButton('Взаимодействие')
    markup_reply.add(item_activity)
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    index_send.append(message.id)
    data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": index_send}})
    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Удаление товара"*', parse_mode= "Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try: bot.delete_message(message.chat.id, i)
            except: print(f"[DEBUG#778]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        try:
            count = int(message.text)
            n = 1
        except:
            n = 0
            bot.delete_message(message.chat.id, message.id)
            cancel_message = bot.send_message(message.chat.id, '*Вы указали неверный формат значения.*\n\nНеобходимо указать количество товара в единицах\n*Пример:* 1',
                                                                parse_mode="Markdown")
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(cancel_message.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            bot.register_next_step_handler(cancel_message, cell_count_function_step)

        if n == 1:
            count_id = 0
            for i in data_base.find({"type": "товар"}):
                if i["name"].lower() == name_tag[0].lower():
                    count_id = i["_id"]

            count_active = int(data_base.find_one({"_id": count_id})["count"])
            if int(message.text) > count_active:
                bot.delete_message(message.chat.id, message.id)
                cancel_message = bot.send_message(message.chat.id,
                                                  '*Вы указали неверное значение.*\n\nУказанное число превышает количество товара на складе'
                                                  f'\n*Товара на складе сейчас:* {count_active}\n\n'
                                                  f'Введите правильное значение, для отмены, используйте *Отмена*',
                                                  parse_mode="Markdown")
                index_send = [i for i in
                              data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
                index_send.append(cancel_message.id)
                data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                     {"$set": {"index_send": index_send}})
                bot.register_next_step_handler(cancel_message, cell_count_function_step)

            else:
                add_step = bot.send_message(message.chat.id, '▪ *| Удаление товара*\n\n'
                        f'Укажите общую сумму в рублях, полученную за продажу товара "*{name_tag[0]}*" в количестве *{message.text}* штук.\n'
                        f'*Пример:* 70000\n'
                        f'Для того что бы отменить действие, введи *Отмена*', parse_mode="Markdown")
                bot.register_next_step_handler(add_step, cell_count_function_two_step)
                name_tag.append(message.text)
                index_send = [i for i in
                              data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
                index_send.append(add_step.id)
                data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                     {"$set": {"index_send": index_send, "name_tag": name_tag}})

def cell_count_function_two_step(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]

    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_activity = types.KeyboardButton('Взаимодействие')
    markup_reply.add(item_activity)
    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Удаление товара"*',
                                          parse_mode="Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try: bot.delete_message(message.chat.id, i)
            except: print(f"[DEBUG#262]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        try:
            count = int(message.text)
            n = 1
        except:
            n = 0
            bot.delete_message(message.chat.id, message.id)
            cancel_message = bot.send_message(message.chat.id,
                                              '*Вы указали неверный формат значения.*\n\nНеобходимо указать сумму в рублях\n*Пример:* 70000',
                                              parse_mode="Markdown")
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(cancel_message.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            bot.register_next_step_handler(cancel_message, cell_count_function_two_step)

        if n == 1:
            markup_inline = types.InlineKeyboardMarkup()
            item_add = types.InlineKeyboardButton(text='Да', callback_data='yes_cell')
            item_edit = types.InlineKeyboardButton(text='Нет', callback_data='no_cell')
            markup_inline.add(item_add, item_edit)
            auto_mark = bot.send_message(message.chat.id, f'▪ *| Удаление товара*\n'
                                                          f'Подтвердите действие:\n\n'
                                                          f'Убрать *{name_tag[1]} шт* товара *"{name_tag[0]}"* на сумму {message.text} со склада?',
                                         parse_mode="Markdown",
                                         reply_markup=markup_inline)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(message.id)
            index_send.append(auto_mark.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            name_tag.append(int(message.text))
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"name_tag": name_tag}})

def add_count_function(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]

    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        item_activity = types.KeyboardButton('Взаимодействие')
        markup_reply.add(item_activity)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Добавление товара"*', parse_mode= "Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try: bot.delete_message(message.chat.id, i)
            except: print(f"[DEBUG#303]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        index_send.append(message.id)
        add_step = bot.send_message(message.chat.id, '▪ *| Добавление товара в перечень*\n\n'
                                                          f'Укажите количество товара.\n'
                                                          f'*Пример:* 5\n'
                                                          f'Для того что бы отменить действие, введи *Отмена*',
                                    parse_mode="Markdown", )
        bot.register_next_step_handler(add_step, add_count_function_step)
        name_tag.append(message.text)
        index_send.append(add_step.id)
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                             {"$set": {"index_send": index_send, "name_tag": name_tag}})

def add_count_function_step(message):
    index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
    name_tag = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["name_tag"]]
    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    item_activity = types.KeyboardButton('Взаимодействие')
    markup_reply.add(item_activity)
    if message.text.lower() == 'отмена' or message.text.lower() == 'отменить':
        bot.delete_message(message.chat.id, message.id)
        cancel_message = bot.send_message(message.chat.id, 'Вы отменили действие *| ▪ "Добавление товара"*', parse_mode= "Markdown", reply_markup=markup_reply)
        index_send = [i for i in data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
        for i in index_send:
            try: bot.delete_message(message.chat.id, i)
            except: print(f"[DEBUG#328]: Сообщение [{i}] было удалено раньше.")
        data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id}, {"$set": {"index_send": []}})
        time.sleep(5)
        bot.delete_message(cancel_message.chat.id, cancel_message.id)
    else:
        try:
            count = int(message.text)
            n = 1
        except:
            n = 0
            bot.delete_message(message.chat.id, message.id)
            cancel_message = bot.send_message(message.chat.id, '*Вы указали неверный формат значения.*\n\nНеобходимо указать количество товара в единицах\n*Пример:* 1',
                                              parse_mode="Markdown")
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            index_send.append(cancel_message.id)
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"index_send": index_send}})
            bot.register_next_step_handler(cancel_message, add_count_function_step)

        if n == 1:
            add_step = bot.send_message(message.chat.id, '▪ *| Добавление товара в перечень*\n'
                                                         f'Вы добавили товар *"{name_tag[0]}"* в количестве *{count} шт* в перечень товаров.\n\n',
                                                         parse_mode="Markdown", reply_markup=markup_reply)
            year = time.strftime("%Y")
            month = time.strftime("%m")
            day = time.strftime("%d")
            id = int(year) * 365
            month2 = {1: 31, 2:28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
            month_id = 0
            for i in range(1, int(month) + 1): month_id += month2[i]
            id += month_id
            id += int(day)
            times = time.strftime("%H:%M:%S")

            data_base.insert_one({"type": "stats", "name": name_tag[0].lower(), "moution": "add", "count": int(count),
                                  "year": year, "month": month, "day": day, "id": id, "time": times,
                                  "autor": f'{message.from_user.username} [ID: {message.from_user.id}]', "datetime": f'{time.strftime("%d.%m.%Y")}'})
            if not name_tag[0].lower() in [i["name"].lower() for i in data_base.find({"type": "товар"})]:
                data_base.insert_one({"type": "товар", "name": name_tag[0], "count": count})
            else:
                for i in data_base.find({"type": "товар"}):
                    if i["name"].lower() == name_tag[0].lower():
                        count_one = int(data_base.find_one({"_id": i["_id"]})["count"])
                        data_base.update_one({"_id": i["_id"]}, {"$set": {"count": count_one + count}})

            bot.delete_message(message.chat.id, message.id)
            index_send = [i for i in
                          data_base.find_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id})["index_send"]]
            for i in index_send:
                try: bot.delete_message(message.chat.id, i)
                except: print(f"[DEBUG#371]: Сообщение [{i}] было удалено раньше.")
            data_base.update_one({"type": "async", "chat_id": message.chat.id, "user_id": message.from_user.id},
                                 {"$set": {"name_tag": [], "index_send": []}})
            time.sleep(10)
            bot.delete_message(add_step.chat.id, add_step.id)


def on_ready():
    print('██████╗░░█████╗░████████╗  ░█████╗░░█████╗░████████╗██╗██╗░░░██╗░█████╗░████████╗███████╗██████╗░\n'
          '██╔══██╗██╔══██╗╚══██╔══╝  ██╔══██╗██╔══██╗╚══██╔══╝██║██║░░░██║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗\n'
          '██████╦╝██║░░██║░░░██║░░░  ███████║██║░░╚═╝░░░██║░░░██║╚██╗░██╔╝███████║░░░██║░░░█████╗░░██║░░██║\n'
          '██╔══██╗██║░░██║░░░██║░░░  ██╔══██║██║░░██╗░░░██║░░░██║░╚████╔╝░██╔══██║░░░██║░░░██╔══╝░░██║░░██║\n'
          '██████╦╝╚█████╔╝░░░██║░░░  ██║░░██║╚█████╔╝░░░██║░░░██║░░╚██╔╝░░██║░░██║░░░██║░░░███████╗██████╔╝\n'
          '╚═════╝░░╚════╝░░░░╚═╝░░░  ╚═╝░░╚═╝░╚════╝░░░░╚═╝░░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═════╝░')

if __name__ == '__main__':
    on_ready()
    bot.polling(none_stop=True, interval=0)