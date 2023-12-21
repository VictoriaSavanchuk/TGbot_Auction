import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import gspread
import json
import sqlite3 as sl
from keyboards import * 
import os
import shutil
import threading



with open ('config.json') as settings:
    config = json.load(settings)
    Token = config.get("telegram_token")
    database = config.get("database_path")
    geocoder_api = config.get("geocoder_api")
    chanel = config.get("chanel_id")
    queries = config.get("queries")

    
bot = telebot.TeleBot(Token)
con = sl.connect(database, check_same_thread=False)     #check_same_thread=False  обращение в разных потоках
message_lock = threading.Lock()

# создаю словарь для обновления админ
administrators_dict = {}
# текущие лоты, кот учавствуют в аукционе
buffer = {
    "Lots_to_add": [],  # Перед постом добавляются id лотов для проверки через "Moderation"
    "Moderation": {},  # Лоты которые, отправляются всем админам со статусом SUPER_ADMIN или SUPPORT
    "Approved": [],  # Лоты которые, будут отправляться на канал
    "Active": {}  # Лоты которые уже находятся на канале
}

#регистрация обработчика для получения текста, через название кнопки
handler_register =["title", "price", "geolocation", "description", "additional_info"]       

with con:
    admin_for_top_up_your_balance = con.execute(queries['find_admin_for_top_up_your_balance']).fetchone()
    #print(admin_for_top_up_your_balance)  #('@Zenagar',)
    texts_dict = { "create_lot": "Заполните всю необходимую информацию о новом лоте:\n",
                  "title": "Укажите название",

                "media": ("Укажите количество отправляемых фотографий? \n"
                        "Максимально возможное количество: 4. \n"
                        "Обязательно выберите нужный вариант для правильного \n"
                        "сохранения ваших изображений"),

                "media_1": "Отправьте 1 изображение",
                "media_2": "Отправьте 2 изображения",
                "media_3": "Отправьте 3 изображения",
                "media_4": "Отправьте 4 изображения",

                "price": "Отправьте стартовую цену лота",

                "geolocation": "Укажите город",

                "description": "Укажите описание",

                "additional_info": "Укажите дополнительную информацию",

                "recreate_lot": "Выберите лоты из которых необходимо пересоздать лот",
                "customers": "Выберите лот у которого есть победитель: ",
                "show_history": ("Вы можете посмотреть историю торгов для вашего лота:\n"
                               "Выберите название если вы добавляли лот"),
                "show_finance": f"Для пополнения баланса обратитесь к администратору {admin_for_top_up_your_balance[0]}",
                "deleting_lot": ("Если вы удалите лот из текущего аукциона то площадка\n"
                               "отнимет от баланса комиссию в размере 5% от текущей\n"
                               "стоимости лота"),
                "/start for admin": ('в бот аукционов @Auction_monett '
                                   'Выберите необходимыe для вас действия:'),
                "admins_settings": "Выберите необходимые действия с администраторами:",
                "/start for user": ('Привет ,я бот аукционов @Auction_monett\n'
                                  'Я помогу вам следить за выбранными лотами ,и регулировать\n'
                                  'ход аукциона.А так же буду следить за вашими накопленными\n'
                                  'балами.\n'
                                  'Удачных торгов 🤝'),
                "my_lots": "Выберите лот в котором вы участвуете",
                "no_lots": "Вы еще не участвовали в лотах",
                "rules": ("После окончания торгов,победитель должен выйти на связь с\n"
                        "продавцом\n"
                        "самостоятельно в течении суток‼️\n"
                        "Победитель обязан выкупить лот в течении ТРЁХ дней,после\n"
                        "окончания аукциона🔥\n"
                        "НЕ ВЫКУП ЛОТА - ПЕРМАНЕНТНЫЙ БАН ВО ВСЕХ\n"
                        "НУМИЗМАТИЧЕСКИХ СООБЩЕСТВАХ И АУКЦИОНАХ🤬\n"
                        "Что бы узнать время окончания аукциона,нажмите на ⏰\n"
                        "Анти-снайпер - Ставка сделанная за 10 минут до\n"
                        "конца,автоматически переносит\n"
                        "Аукцион на 10 минут вперёд ‼️\n\n"
                        "Работают только проверенные продавцы,их Отзывы суммарно\n"
                        "достигают 10000+ на различных площадках.\n"
                        "Дополнительные Фото можно запросить у продавца.\n"
                        "Случайно сделал ставку?🤔\n"
                        "Напиши продавцу‼️\n\n\n"
                        "Отправка почтой,стоимость пересылки указана под фото.\n"
                        "Лоты можно копить ,экономя при этом на почте.\n"
                        "Отправка в течении трёх дней после оплаты‼️"),
                "help_info": (f"Свяжитесь с нами, если у вас возникли вопросы {admin_for_top_up_your_balance[0]}\n"
                            f"При проблемах или нахождении ошибок пишите {admin_for_top_up_your_balance[0]}"),
                "names": {
                  "title": "Название",
                  "images": "Изображение",
                  "price": "Стартовая цена",
                  "geolocation": "Геолокация",
                  "description": "Описание",
                  "additional_info": "Доп.Информация"
                  },
                "save_lot": "Подтвердите сохранение",
                "selled_lots": "Выберите из проданных лотов:",

                "unselled_lots": "Выберите из не-проданных лотов:",
                "customers": "Выберите лот у которого есть победитель: ",

                "no_customers": "Пока по вашим лотам победителей нет",

                "show_history": ("Вы можете посмотреть историю торгов для вашего лота:\n"
                               "Выберите название если вы добавляли лот"),
                }  

# Словарь который, содержит в себе ссылки на объекты Inline клавиатур telebot.types
actions = { 
    # Просмотр всех Лотов в которых участвует пользователь
    #значение для ключа "my_lots"  представляет собой лямбда-функцию, которая использует lots в качестве аргумента и возвращает 
    # клавиатуру (предположительно объект или значение, связанное с кнопками) из метода user_participated_lots() класса BiddingHistory.
    "my_lots": lambda lots: BiddingHistory(lots).user_participated_lots().keyboard,     
           # Здесь только главное меню
    "rules": MainMenu().get_menu().keyboard,
    # Здесь только главное меню и написать в поддержку
    "help_info": MainMenu().get_menu().keyboard,
     # Текст по обращению к супер админу для пополнения баланса и действия с лотами
    "my_balance": "",
    "create_lot": Lot().creating_lot().keyboard,
    "recreate_lot": Lot().recreate_lot().keyboard,
    "title": None,
    "media": Lot().quantity_of_images().keyboard,
    "media_1": None,
    "media_2": None,
    "media_3": None,
    "media_4": None,
    "price": None,
    "geolocation": None,
    "description": None,
    "additional_info": None,
    "save_lot": Lot().saving_confirmation().keyboard,
    "selled_lots": lambda lots: BiddingHistory(lots).recreate_lot().keyboard,
    "unselled_lots": lambda lots: BiddingHistory(lots).recreate_lot().keyboard,
    "customers": lambda lots: BiddingHistory(lots).won_lot().keyboard,
    "show_history": lambda lots: BiddingHistory(lots).show().keyboard,
    "deleting_lot": lambda lots: BiddingHistory(lots).delete_lot().keyboard,
}

def update_administrator(case):
    if case == 'Обновить администраторов':
        with con:
            administrators = con.execute(queries['find_admins']).fetchall()
            #print(administrators)    #[(2, 4, 'SUPER_ADMIN', None, None, None, 4, 'Аркадзя', 'None', 451784658, '@Zenagar', None, None, None), (3, 2, 'ADMIN', None, None, None, 2, 'Светлана', 'Захарчук', 1252225243, None, None, None, None)]
        for admin in administrators:
            access_level = admin[2]
            phone = admin[3]
            email = admin[4]
            status = admin[5]
            first_name = admin[7]
            last_name = admin[8]
            telegram_id = admin[9]
            telegram_link = admin[10]
            balance = admin[11]
            
            administrators_dict.update({telegram_id:{'access_level':access_level,
                                                  'phone':phone,
                                                  'email':email,
                                                  'status':status,
                                                  'first_name':first_name,
                                                  'last_name':last_name,
                                                  'telegram_link':telegram_link,
                                                  'balance': balance                                             
                                                  
                                        }})

def personal_cabinet(telegram_id, type_of_message, message_id, call_id):
    
    #если присутствует call_id (идентификатор callback-запроса), выполняется функция 
    # bot.answer_callback_query с передачей callback_query_id=call_id.
    if call_id is not None:
        bot.answer_callback_query(callback_query_id=call_id, )

    if telegram_id in administrators_dict.keys():
        if administrators_dict[telegram_id]["access_level"] == "SUPER_ADMIN":
            starting = Start().is_super_admin_keyboard().keyboard
        else:
            starting = Start().is_admin_keyboard().keyboard
        name = administrators_dict[telegram_id]['first_name']
        telegram_link = administrators_dict[telegram_id]['telegram_link']
        text = f"Добро пожаловать {name}, {telegram_link} " + texts_dict['/start for admin']

    else:
        starting = Start().is_user_keyboard().keyboard
        text = texts_dict['/start for user']

    # Использование нового подхода для отправки типа сообщений send или edit
    #В зависимости от значения type_of_message выбирается соответствующая функция и аргументы для отправки
    # сообщения или редактирования существующего сообщения.
    send = {"send": [bot.send_message, {'chat_id': telegram_id, "text": text, "reply_markup": starting}],
            "edit": [bot.edit_message_text, {'chat_id': telegram_id, 'message_id': message_id, "text": text,
                                             "reply_markup": starting}]}
    #переменные function и kwargs получают значение из словаря send в соответствии с type_of_message.
    function, kwargs = send[type_of_message][0], send[type_of_message][1]
    #вызываю ф-ию чтобы отправить сообщение или отредактировать существующее сообщение
    function(**kwargs)

def cabinet_actions(button_info, telegram_id, message_id, type_of_message, call_id):
    lots, text = None, None

    if call_id is not None:
        bot.answer_callback_query(callback_query_id=call_id, )
    
    lot_info_queries = {"customers": "lot_id_title-winners",
                        "show_history": "lot_id_title",
                        "selled_lots": "get_selled_lots",
                        "unselled_lots": "get_unselled_lots"}
    if button_info in lot_info_queries.keys():
        with con:
            lots = con.execute(queries[lot_info_queries[button_info]], [telegram_id]).fetchall()

    
    if button_info == "my_lots":  # Лоты которые, открыл пользователь в кабинете пользователя
        lots = []
        if buffer["Active"] is not None:
            for lot_id in buffer['Active'].keys():
                if "bids" in buffer["Active"][str(lot_id)].keys():   #ставка
                    if telegram_id in buffer["Active"][str(lot_id)]['bids'].keys():
                        with con:
                            title = con.execute(queries["lot_title"], [int(lot_id)]).fetchall()[0][0]
                        lots.append([lot_id, title])  
            
    elif button_info == "deleting_lot":  # Лоты которые админ хочет удалить
        lots = []
        if buffer["Active"] is not None:
            for lot_id in buffer['Active'].keys():
                with con:
                    users_telegram_id = con.execute(queries["lot_is_users?"], [int(lot_id)]).fetchall()[0][0]
                    if users_telegram_id == telegram_id:
                        title = con.execute(queries["lot_title"], [int(lot_id)]).fetchall()[0][0]
                        lots.append([lot_id, title])   
    
    selected_action = actions[button_info]
    # является ли selected_action вызываемым объектом, то есть функцией или методом.
    if callable(selected_action):  # callable() - это встроенная функция в Python, которая возвращает True, если переданный объект может быть вызван, и False в противном случае.
        selected_action = selected_action(lots)   #вызывает этот объект, передавая lots в качестве аргумента.
        
    if button_info == 'rules':
        text = texts_dict["rules"]    
    if button_info == 'help_info':
        text = texts_dict["help_info"]  
    elif button_info == "my_lots":  # текст если лотов нет, путём проверки длины клавиатуры
        if len(selected_action.keyboard) == 1:
            text = texts_dict["no_lots"]   #вместо отображения клавиатуры с лотами будет отправлено соответствующее текстовое сообщение
    else:
        text = texts_dict[button_info]
        #для администратора
    if button_info == "create_lot":
        if "new_lot" not in administrators_dict[telegram_id].keys():
            administrators_dict[telegram_id].update(
                {
                    "new_lot":
                        {
                            "title": None,
                            "images": None,
                            "price": None,
                            "geolocation": None,
                            "description": None,
                            "additional_info": None
                        }
                }
            )

        # Цикл который, подсчитывает количество добавленных изображений
        for key, value in administrators_dict[telegram_id]["new_lot"].items():
            if key != "images" and value is None:
                value = "Нет"
            elif key == "images":
                image_directory = f"Media/{telegram_id}"
                if os.path.exists(image_directory):
                    image_quantity = len(os.listdir(image_directory))
                    value = image_quantity
                else:
                    value = "Нет"
            text += f"{texts_dict['names'][key]}: {value}\n" 
            print(text)
                        
    send = {"send": [bot.send_message, {'chat_id': telegram_id, "text": text, "reply_markup": selected_action}],
            "edit": [bot.edit_message_text, {'chat_id': telegram_id, 'message_id': message_id, "text": text,
                                             "reply_markup": selected_action}]}

    function, kwargs = send[type_of_message][0], send[type_of_message][1]
    function(**kwargs)
    
def creating_lot(button_info, telegram_id, message_id, message, call_id):
    if call_id is not None:
        bot.answer_callback_query(callback_query_id=call_id, )
#Если button_info начинается с "media_", обработка медиа-кнопок(создается папка folder_path для хранения медиа-файлов пользователя, 
# и если папка уже существует, она удаляется.) в словаре administrators_dict обновляются информация о новом лоте пользователя,
# указывая количество выбранных изображений.
    if button_info.startswith("media_"):
        folder_path = f"Media/{str(telegram_id)}"
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        administrators_dict[telegram_id]["new_lot"]["images"] = int(button_info[-1])

    selected_action = actions[button_info]
    text = texts_dict[button_info]

    bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=text, reply_markup=selected_action)
#Если button_info содержится в handler_register вызывается bot.register_next_step_handler() для регистрации следующего
# обработчика get_info. Получаю доп инф от пользователя для создания лота.
    if button_info in handler_register:
        bot.register_next_step_handler(message, get_info, button_info)
        
def recreate_lot(telegram_id, lot_id, message_id, call_id):
    if lot_id not in buffer["Lots_to_add"]:

        bot.answer_callback_query(callback_query_id=call_id, text="Лот добавлен на проверку")
        info = "Лот добавлен на проверку модераторам"

    else:

        bot.answer_callback_query(callback_query_id=call_id, text="Лот уже в очереди")
        info = "Лот находится на проверке"

    main_menu = MainMenu().get_menu().keyboard
    bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=info, reply_markup=main_menu)
    
    
   #сохраняет лот в базе данных и перемещает изображения лота из временной папки в папку, соответствующую идентификатору лота 
def save_lot(telegram_id, message_id, call_id):
    #Извлекаются данные о лоте 
    title = administrators_dict[telegram_id]["new_lot"]["title"]
    price = administrators_dict[telegram_id]["new_lot"]["price"]
    geolocation = administrators_dict[telegram_id]["new_lot"]["geolocation"]
    description = administrators_dict[telegram_id]["new_lot"]["description"]
    add_info = administrators_dict[telegram_id]["new_lot"]["additional_info"]

    if title is None or price is None or geolocation is None or description is None:
        bot.answer_callback_query(callback_query_id=call_id, text="Заполните все данные")
    else:
        #извлекается идентификатор пользователя (users_id) и идентификатор администратора (admin_id)
        with con:
            users_id = con.execute(queries["searching_user"], [telegram_id]).fetchall()[0][0]
            admin_id = con.execute(queries["admin_id"], [users_id]).fetchall()[0][0]
            #Вставляются данные лота в базу данных 
            con.execute(queries["save_lot"], [admin_id, title, geolocation, price, description, add_info])
            #Получается идентификатор сохраненного лота (lot_id) из базы данных
            lot_id = con.execute(queries["lot_id"], [admin_id]).fetchall()[-1][0]
        
        source_directory = f"Media/{str(telegram_id)}"

        directory = "Lots/"
        folder_name = str(lot_id)
        folder_path = os.path.join(directory, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        #Создается папка для лота с именем, равным lot_id, если она не существует.
        target_directory = f"Lots/{str(lot_id)}"
        file_list = os.listdir(source_directory)
        #Изображения лота перемещаются из временной папки (Media/{telegram_id}) в папку лота (Lots/{lot_id}) с использованием библиотеки shutil
        for file_name in file_list:
            source_path = os.path.join(source_directory, file_name)
            target_path = os.path.join(target_directory, file_name)
            shutil.move(source_path, target_path)
        #Если временная папка (Media/{telegram_id}) существует, она удаляется с помощью shutil.rmtree.
        if os.path.exists(source_directory):
            shutil.rmtree(source_directory)
        #ссылки на изображения лота, проходя по файлам в папке лота и добавляя их в список image_links.
        image_links = []

        for filename in os.listdir(target_directory):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_link = f"{target_directory}/{filename}"
                image_links.append(image_link)
        #Загружаются ссылки на изображения лота в базу данных
        with con:
            for link in image_links:
                con.execute(queries["lot_upload_links"], [lot_id, link])
        #Удаляется информация о новом лоте из словаря administrators_dict
        del administrators_dict[telegram_id]["new_lot"]

        bot.answer_callback_query(callback_query_id=call_id, text="Лот успешно сохранён")

        buffer["Lots_to_add"].append(lot_id)

        personal_cabinet(telegram_id, "edit", message_id, None)

def get_info(message, button_info):
    telegram_id = message.from_user.id
    message_id = message.chat.id
    administrators_dict[telegram_id]["new_lot"][button_info] = message.text
    cabinet_actions("create_lot", telegram_id, message_id, "send", None)
    
# Информация о победителе лота
def winner_info(telegram_id, message_id, lot_id, call_id):
    bot.answer_callback_query(callback_query_id=call_id, )

    with con:
        winners_link = con.execute(queries["get_winners_link"], [lot_id]).fetchall()[0][0]
        user_id = con.execute(queries["get_winners_id"], [lot_id]).fetchall()[0][0]
        lot_title = con.execute(queries["lot_title"], [lot_id]).fetchall()[0][0]

    text = f"Победителем лота: \n {lot_title} \n является: {winners_link}"

    keyboard = BiddingHistory(user_id).winner().keyboard

    bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=text, reply_markup=keyboard)
    
# Функция для просмотра истории
def show_history(telegram_id, message_id, lot_id, call_id):
    bot.answer_callback_query(callback_query_id=call_id, )

    if str(lot_id) in buffer["Active"].keys():
        keyboard = BiddingHistory("ACTIVE_LOT").delete_bid().keyboard
    else:
        keyboard = BiddingHistory(None).delete_bid().keyboard

    with con:
        bids_info = con.execute(queries["get_bids_by_lot"], [lot_id]).fetchall()

    if bids_info:
        text = "История ставок от пользователей по вашему лоту:\n"
        for info in bids_info:
            users_link, bid_amount, bid_date = info[0], info[1], info[2]
            text += f"{users_link}: {bid_amount} - {bid_date}\n"
    else:
        text = "Ставок по вашему лоту пока нет"

    bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=text, reply_markup=keyboard)
    
# Функция lot_information для получения всего текста по лоту
def lot_information(lot_id):
    with con:
        lot_info = con.execute(queries["get_lot_info"], [lot_id]).fetchall()[0]
        lot_title, lot_price, lot_geolocation = lot_info[0], str(lot_info[1]), lot_info[2]
        lot_description, lot_additional_info, sellers_link = lot_info[3], lot_info[4], lot_info[5]

    if lot_additional_info is not None:
        text = (lot_title + "\n" +
                lot_geolocation + "\n" +
                lot_description + "\n" +
                lot_additional_info + "\n" +
                ("Продавец " + sellers_link) + "\n\n")
    else:
        text = (lot_title + "\n" +
                lot_price + "\n" +
                lot_geolocation + "\n" +
                lot_description + "\n" +
                ("Продавец " + sellers_link) + "\n\n")
    return text
    
def delete_lot(telegram_id, message_id, lot_id, call_id):
    message = "🚫Вы удалили лот"
    bot.answer_callback_query(callback_query_id=call_id, text=message)

    lot_message = buffer["Active"][str(lot_id)]["message"]
    text = lot_information(lot_id)

    if 'bids' in buffer["Active"][str(lot_id)].keys():
        lot_price = max(buffer["Active"][str(lot_id)]["bids"].values())
        text += "Следующая ставка: " + str(lot_price + 100) + "₽"

    else:
        with con:
            lot_price = con.execute(queries['lot_price'], [lot_id]).fetchall()[0][0]
        text += "Следующая ставка: " + str(lot_price) + "₽"

    with con:
        balance = con.execute(queries['get_balance'], [telegram_id]).fetchall()[0][0]
        commission = lot_price / 100 * 5
        new_balance = balance - commission
        con.execute(queries['set_balance'], [new_balance, telegram_id])

    text += "\n\n👮‍♀️Лот был удалён администратором"

    bot.edit_message_reply_markup(chat_id=chanel, message_id=lot_message, reply_markup=None)
    bot.edit_message_caption(caption=text, chat_id=chanel, message_id=lot_message)

    if "user_opened" in buffer["Active"][str(lot_id)].keys():
        for user_id, message_id in buffer["Active"][str(lot_id)]["user_opened"].items():
            bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)
            bot.edit_message_caption(caption=text, chat_id=user_id, message_id=message_id)

    personal_cabinet(telegram_id, 'edit', message_id, None)

    
@bot.message_handler(content_types=['photo'])
def handle_image(message):
    telegram_id = message.from_user.id
    message_id = message.chat.id
    if "new_lot" in administrators_dict[telegram_id].keys():
        
        #методы acquire() и release() объекта блокировки для захвата и освобождения блокировки в нужных местах кода.
        #код, следующий за этой строкой, будет выполняться только одним потоком в данный момент времени
        
        message_lock.acquire()
        directory = "Media/"
        folder_name = str(telegram_id)
        folder_path = os.path.join(directory, folder_name)

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        if administrators_dict[telegram_id]["new_lot"]["images"] is not None:
            try:
                count = administrators_dict[telegram_id]["new_lot"]["images"]
                photo = message.photo[-1]
                file_info = bot.get_file(photo.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                file_name = f'image_{photo.file_unique_id}.jpg'
                file_path = os.path.join(folder_path, file_name)

                with open(file_path, 'wb') as new_file:
                    new_file.write(downloaded_file)

                bot.reply_to(message, 'Изображение успешно сохранено.')

                count -= 1
                administrators_dict[telegram_id]["new_lot"]["images"] = count
                if count == 0:
                    administrators_dict[telegram_id]["new_lot"]["images"] = None
                    print(administrators_dict)
                    cabinet_actions("create_lot", telegram_id, message_id, "send", None)
            finally:
                message_lock.release()
        else:
            message_lock.release()

@bot.message_handler(content_types=['text'])

def start(message):
    #print(message)
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    telegram_id = message.from_user.id
    if message.from_user.username == None:
        telegram_link = None
    else:
        telegram_link = "@" + message.from_user.username
    menu = {'/start':personal_cabinet, '/help':''}
    
    with con:
        searching = con.execute(queries['find_user'], [telegram_id]).fetchall()
        
        if not searching:    #если пустой список
            con.execute(queries['add_user'], [first_name, last_name, telegram_id, telegram_link])
    if message.text in menu.keys():
        #Добавляются значения 1 и 2 в список buffer["Lots_to_add"]
        buffer["Lots_to_add"].append(1), buffer["Lots_to_add"].append(2)
        #Вызывается функция menu
        menu[message.text](telegram_id, "send", None, None)
            
    
    
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    #bot.answer_callback_query(callback_query_id=call.id, )
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    call.data = json.loads(call.data)
    #print(call.data)   #['/start', 'rules']
    flag, button_info = call.data[0], call.data[1]
    
    callback = {'/home': (personal_cabinet, (chat_id, "edit", message_id, call.id)),
                '/start': (cabinet_actions, (button_info, chat_id, message_id, "edit", call.id)),
                '/lot': (creating_lot, (button_info, chat_id, message_id, call.message, call.id)),
                '/recreate': (recreate_lot, (chat_id, button_info, message_id, call.id)),
                '/save': (save_lot, (chat_id, message_id, call.id)),
                '/customer': (winner_info, (chat_id, message_id, button_info, call.id)),
                '/history': (show_history, (chat_id, message_id, button_info, call.id)),
                '/delete': (delete_lot, (chat_id, message_id, button_info, call.id)),
                }
    
    function, args = callback[flag][0], callback[flag][1]

    function(*args)
    
  
print("Ready")
update_administrator(case='Обновить администраторов')
bot.infinity_polling()