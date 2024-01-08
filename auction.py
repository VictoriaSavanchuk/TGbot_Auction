import time
import datetime 
from datetime import timedelta
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import json
import sqlite3 as sl
from keyboards import * 
import os
import shutil
import schedule
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

#для настройки карточек лота
remaining_time = None
timer_thread = None


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

# словарь, в котором хрранится текст, используемый в боте
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
                "no_customers": "Пока по вашим лотам победителей нет",
                "show_history": ("Вы можете посмотреть историю торгов для вашего лота:\n"
                               "Выберите название если вы добавляли лот"),
                "show_finance": f"Для пополнения баланса обратитесь к администратору {admin_for_top_up_your_balance[0]}",
                "deleting_lot": ("Если вы удалите лот из текущего аукциона то площадка\n"
                               "отнимет от баланса комиссию в размере 5% от текущей\n"
                               "стоимости лота"),
                "/start for admin": ('в бот аукционов @Auction_monett '
                                   'Выберите необходимыe для вас действия:'),
                "admins_settings": "Выберите необходимые действия с администраторами:",
                "add_admin": "Поиск пользователя по ссылке:",

                "change_admin": "Выберите администратора которого хотите изменить",
  
                "delete_admin": "Выберите администратора которого хотите удалить",
                "changing_options": "Выберите необходимое что хотите изменить",

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
                "card_info": ("После окончания торгов,победитель\n"
                            "должен выйти на связь с продавцом\n"
                            "самостоятельно в течении\n"
                            "суток. Победитель обязан выкупить лот\n"
                            "в течении ТРЁХ дней,после окончания\n"
                            "аукциона.\n"
                            "НЕ ВЫКУП ЛОТА - БАН."),
                "start_auction": ("Короткий аукцион 🔥🤳\n"
                                "Окончание: "
                                f"{(datetime.datetime.now().date() + timedelta(days=1)).strftime('%d.%m.%Y')}💥\n"
                                "С 23:00-00:00\n"
                                "По МСК\n\n"
                                "Работают только проверенные продавцы,их Отзывы сумарно\n"
                                "достигают 10000+ на различных площадках.\n"
                                "Дополнительные Фото можно запросить у продавца.\n"
                                "Случайно сделал ставку?🤔\n"
                                "Напиши продавцу‼️\n\n\n"
                                "Отправка почтой только по РОССИИ,стоимость пересылки\n"
                                "указана под фото.\n"
                                "Лоты можно копить ,экономя при этом на почте.\n"
                                "Отправка в течении трёх дней после оплаты‼️\n\n"
                                "После окончания торгов,победитель должен выйти на связь\n"
                                "с продавцом\n"
                                "самостоятельно в течении суток‼️\n"
                                "Победитель обязан выкупить лот в течении ТРЁХ дней,после\n"
                                "окончания аукциона🔥\n"
                                "НЕ ВЫКУП ЛОТА - ПЕРМАНЕНТНЫЙ БАН ВО ВСЕХ\n"
                                "НУМИЗМАТИЧЕСКИХ СООБЩЕСТВАХ И АУКЦИОНАХ🤬\n"
                                "Что бы узнать время окончания аукциона,нажмите на ⏰\n\n"
                                "Для участия нажмите УЧАСТВОВАТЬ,\n"
                                "Далее вас перенёс в чат с ботом,\n"
                                "Нажмите СТАРТ и вам будет доступен калькулятор ставок.\n"
                                "Повторяйте эту процедуру при добавлении новых лотов.\n\n\n"
                                "Антиснайпер - Ставка сделанная за 10 минут до\n"
                                "конца,автоматически переносит\n"
                                "Аукцион на 10 минут вперёд ‼️"),
                "notification_of_victory": ("💥Поздравляем с победой💥, напоминаем вам\n"
                                          "что вы должны выйти на связь с продавцом\n"
                                          "в течении суток, и вы обязаны выкупить лот\n"
                                          "в течении трёх дней, после получения этого\n"
                                          "сообщения, за нарушение этого правила:\n"
                                          "вы больше не сможете участвовать\n"
                                          "и пользоваться услугами площадки"),
                }  

# Словарь который, содержит в себе ссылки на объекты Inline клавиатур telebot.types
actions = { 
    "admins_settings": SuperAdmin().options().keyboard,
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
    "show_finance": MainMenu().get_menu().keyboard,
    # Просмотр всех Лотов в которых участвует пользователь
    #значение для ключа "my_lots"  представляет собой лямбда-функцию, которая использует lots в качестве аргумента и возвращает 
    # клавиатуру (предположительно объект или значение, связанное с кнопками) из метода user_participated_lots() класса BiddingHistory.
    "my_lots": lambda lots: BiddingHistory(lots).user_participated_lots().keyboard,   
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
    #покупатели, история торгов, проданные лоты, не проданные лоты
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
            #print(text)
            
    elif button_info == "show_finance":
        with con:
            balance = con.execute(queries['get_balance'], [telegram_id]).fetchall()[0][0]
        if balance == None:
            text += f"\nВаш текущий баланс равен 0"
        else:
            text += f"\nВаш текущий баланс: {balance}"
                        
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
 
#повторное создание лота      
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
    
    #удаление лота из текущего аукциона
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

#НАСТРОЙКА КАРТОЧКИ ЛОТА
# Спец функция для обработки двух кнопок которые, не отправляют текст, а содержат информацию, принимает два аргумента: call_id и button_info.
def card_info(call_id, button_info):
    if button_info == "timer":
        #Объявляется переменная remaining_time как глобальная
        global remaining_time

        if remaining_time is not None:
            #производится расчет оставшегося времени в днях, часах, минутах и секундах
            days = remaining_time.days
            hours, remainder = divmod(remaining_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            #сообщение об оставшемся времени продолжения аукциона данного лота
            message = f"Осталось {days} дней {hours} часов {minutes} минут {seconds} секунд"
            bot.answer_callback_query(callback_query_id=call_id, text=message)

    elif button_info == "card_info":
        message = texts_dict[button_info]
        #С помощью метода bot.answer_callback_query отправляется ответ на вызов call_id с текстом сообщения, и 
        # параметр show_alert установлен в значение True, чтобы показать предупреждение.
        bot.answer_callback_query(callback_query_id=call_id, text=message, show_alert=True)
    
# Обработка нажатие кнопки отправить фото/видео, в которой, создаётся медиа группа
def card_media(telegram_id, message_id, lot_id, call_id):
    message = "✅Отправили вам фото и видео"
    bot.answer_callback_query(callback_query_id=call_id, text=message)

    with con:
        image_links = con.execute(queries["get_images_link"], [lot_id]).fetchall()[0]   #возвращает ссылки на изображения для указанного lot_id
        lot_price = con.execute(queries["lot_price"], [lot_id]).fetchall()[0][0]        #возвращает цену для указанного lot_id

    text = lot_information(lot_id)

    if "bids" in buffer["Active"][str(lot_id)].keys():      #Если в buffer["Active"][str(lot_id)] присутствует ключ "bids", то находится
        #максимальное значение ставки (last_bid) из словаря buffer["Active"][str(lot_id)]["bids"] + строка "Следующая ставка: " 
        # и значение last_bid в рублях
        last_bid = max(buffer["Active"][str(lot_id)]["bids"].values())
        text += "Следующая ставка: " + str(last_bid) + "₽"
    else:
        text += "Следующая ставка: " + str(lot_price) + "₽"

    media_group = []
    #итерация по ссылкам на изображения в image_links
    for link in image_links:
        #Если текущая ссылка является первой ссылкой (link is image_links[0]), то создается медиа-объект InputMediaPhoto с открытым 
        # файлом изображения (open(link, 'rb')) и текстом caption, равным text. Этот медиа-объект добавляется в список media_group
        if link is image_links[0]:
            media_group.append(telebot.types.InputMediaPhoto(open(link, 'rb'), caption=text))
        else:  #иначе создается медиа-объект InputMediaPhoto с открытым файлом изображения (open(link, 'rb')) и также добавляется в список media_group
            media_group.append(telebot.types.InputMediaPhoto(open(link, 'rb')))
    #для отправки группы медиа-объектов, связана с исходным сообщением, идентифицируемым по message_id.
    bot.send_media_group(chat_id=telegram_id, media=media_group, reply_to_message_id=message_id)

# Функция для ставок : обновить информацию о ставках и лидерах в сообщениях канала и пользователям после принятия новой ставки
# и отобразить информацию о следующей ставке
def card_bids(telegram_id, lot_id, call_id):
    message = "Ставка принята"
    bot.answer_callback_query(callback_query_id=call_id, text=message)

    with con:
        lot_price = con.execute(queries['lot_price'], [lot_id]).fetchall()[0][0]    #цена для указанного lot_id
        users_link = con.execute(queries['users_link'], [telegram_id]).fetchall()[0][0]   #ссылк на пользователя с указанным telegram_id
    #Если ключ отсутствует, то в словарь buffer["Active"][lot_id] добавляется ключ "bids" со значением {telegram_id: lot_price}
    if "bids" not in buffer["Active"][str(lot_id)].keys():
        buffer["Active"][lot_id].update({"bids": {telegram_id: lot_price}})
    else:  
        #находится максимальное значение ставки (last_bid) из словаря buffer["Active"][str(lot_id)]["bids"], и в словарь добавляется ставка пользователя 
        #с увеличением на 100 от last_bid.
        last_bid = max(buffer["Active"][str(lot_id)]["bids"].values())
        buffer["Active"][str(lot_id)]["bids"].update({telegram_id: last_bid + 100})

    last_bid = max(buffer["Active"][str(lot_id)]["bids"].values())    #максимальное значение ставки
    #Создается новая ставка (new_bid), равная last_bid + 100  и Записывается текущая дата и время 
    new_bid = last_bid + 100
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with con:
        user_id = con.execute(queries["user_id"], [telegram_id]).fetchall()[0][0]
         #вставляем запись о ставке в бд с параметрами: lot_id, user_id, last_bid и current_datetime.
        con.execute(queries["insert_bid_to_lot"], [lot_id, user_id, last_bid, current_datetime]) 

    second_place, third_place = None, None
    #Проверяется количество элементов в словаре buffer["Active"]
    if len(buffer["Active"][str(lot_id)]["bids"].items()) == 2:  # Если количество равно 2, то находится второе место (значение и ключ со вторым максимальным значением ставки) и ссылка на пользователя для этого места.
        sorted_items = sorted(buffer["Active"][str(lot_id)]["bids"].items(), key=lambda x: x[1], reverse=True)[1]
        with con:
            second_place_users_link = con.execute(queries["users_link"], [sorted_items[0]]).fetchall()[0][0]

        second_place = f"\n🥈 {sorted_items[1]}₽ {second_place_users_link[1:3]}***"
        third_place = None
     # Если количество больше 2, то находятся и второе и третье места (значения и ключи со вторым и третьим максимальными значениями ставок) и ссылки на пользователей для этих мест.
    elif len(buffer["Active"][str(lot_id)]["bids"].items()) > 2: 
        sorted_items = sorted(buffer["Active"][str(lot_id)]["bids"].items(), key=lambda x: x[1], reverse=True)[1:3]
        with con:
            second_place_users_link = con.execute(queries["users_link"], [sorted_items[0][0]]).fetchall()[0][0]
            third_place_users_link = con.execute(queries["users_link"], [sorted_items[1][0]]).fetchall()[0][0]    

        second_place = f"\n🥈 {sorted_items[0][1]}₽ {second_place_users_link[1:3]}***"
        third_place = f"\n🥉 {sorted_items[1][1]}₽ {third_place_users_link[1:3]}***"

    text = lot_information(lot_id)
    text += "Следующая ставка: " + str(new_bid) + "₽"

    # ("Ваша скрытая ставка: " + "0" + "₽"))

    liders = f"\n\n🥇 {last_bid}₽ {users_link[1:3]}***"  #информацию о лидере (последняя ставка) с использованием ссылки на пользователя.
    #Если второе место (second_place) не None, то liders добавляется информация о втором месте.
    #Если третье место (third_place) не None, то liders добавляется информация о третьем месте.
    if second_place is not None:
        liders += second_place

    if third_place is not None:
        liders += third_place
    #переменные keyboard_for_chanel и keyboard_for_bot, c клавиатурами для канала и бота для указанного lot_id.
    keyboard_for_chanel = Card(lot_id).chanel_card().keyboard
    keyboard_for_bot = Card(lot_id).bot_card().keyboard

    chanel_message_id = buffer["Active"][str(lot_id)]["message"]

    # print(buffer)

    bot.edit_message_caption(caption=(text +
                                      liders),
                             chat_id=chanel,
                             message_id=chanel_message_id,
                             reply_markup=keyboard_for_chanel)    #для редактирования подписи сообщения в канале с указанными параметрами

    for user_id, users_message in buffer["Active"][str(lot_id)]["user_opened"].items():
        # здесь необходимо учитывать скрытую ставку
        bot.edit_message_caption(caption=(text +
                                          liders),  # прямо здесь добавлять скрытую ставку и лидеров
                                 chat_id=user_id,
                                 message_id=users_message,
                                 reply_markup=keyboard_for_bot)
        
# Функция approvement для отмены или одобрения лота перед постом в канал
def approvement(lot_id, call_id, case):
    if case == "accept":

        message = "Вы одобрили лот"
        bot.answer_callback_query(callback_query_id=call_id, text=message)

        buffer['Approved'].append(lot_id)

        for user_id, message in buffer["Moderation"][str(lot_id)].items():
            bot.delete_message(user_id, message)

        del buffer["Moderation"][str(lot_id)]

        send_lot(case="start_auction")

    elif case == "decline":

        message = "Вы отменили лот"
        bot.answer_callback_query(callback_query_id=call_id, text=message)

        for user_id, message in buffer["Moderation"][str(lot_id)].items():
            bot.delete_message(user_id, message)

        with con:
            user_id = con.execute(queries['get_tg-id_by_lot-id'], [lot_id]).fetchall()[0][0]
            lot_title = con.execute(queries['lot_title'], [lot_id]).fetchall()[0][0]

        message = f"К сожалению ваш лот {lot_title} не прошёл проверку, свяжитесь с поддержкой"
        bot.send_message(user_id, message)

        del buffer["Moderation"][str(lot_id)]


# Функция send_lot используются планировщиком для отправки и остановки лотов в канал
def send_lot(case):
    # Сообщение которое, отправляется перед стартом аукциона и закрепляется ежедневно
    if case == "notification":
        pinned_message = bot.send_message(chanel, texts_dict["start_auction"])
        bot.pin_chat_message(chanel, pinned_message.id)

    # Проверка админами со статусом SUPER_ADMIN или SUPPORT лотов перед постом
    elif case == "approvement":
        for lot_id in buffer["Lots_to_add"]:
            keyboard = Support(lot_id).approvement().keyboard

            with con:
                lot_price = con.execute(queries["lot_price"], [lot_id]).fetchall()[0][0]
                image_links = con.execute(queries["get_images_link"], [lot_id]).fetchall()[0]

            text = lot_information(lot_id)
            text += "Следующая ставка: " + str(lot_price) + "₽"

            for user_id, values in administrators_dict.items():

                for key, value in values.items():

                    if value == "SUPER_ADMIN" or value == "SUPPORT":

                        with open(image_links[0], 'rb') as image:

                            message = bot.send_photo(chat_id=user_id,
                                                     photo=image,
                                                     caption=text,
                                                     reply_markup=keyboard)

                        if str(lot_id) not in buffer['Moderation'].keys():
                            buffer['Moderation'].update({str(lot_id): {user_id: message.id}})
                        else:
                            buffer['Moderation'][str(lot_id)].update({user_id: message.id})

        buffer['Lots_to_add'].clear()

    # Отправка лота в канал в случае одобрение администратором
    elif case == "start_auction":

        for lot_id in buffer["Approved"]:
            keyboard = Card(lot_id).chanel_card().keyboard

            with con:
                lot_price = con.execute(queries["lot_price"], [lot_id]).fetchall()[0][0]
                image_links = con.execute(queries["get_images_link"], [lot_id]).fetchall()[0]

            text = lot_information(lot_id)
            text += "Следующая ставка: " + str(lot_price) + "₽"

            with open(image_links[0], 'rb') as image:
                message = bot.send_photo(chat_id=chanel, photo=image, caption=text, reply_markup=keyboard)

            buffer["Active"].update({str(lot_id): {"message": message.id}})

        buffer["Approved"].clear()

        global timer_thread
        if timer_thread is None or not timer_thread.is_alive():
            timer_thread = threading.Thread(target=timer)
            timer_thread.start()

    # Завершение аукциона по истечению времени потока счетчика времени
    if case == "stop_auction":
        for lot_id in buffer["Active"].keys():
            lot_message = buffer["Active"][str(lot_id)]["message"]

            with con:
                lot_price = con.execute(queries["lot_price"], [lot_id]).fetchall()[0][0]

            text = lot_information(lot_id)
            text += "Следующая ставка: " + str(lot_price) + "₽"

            if "bids" not in buffer["Active"][lot_id].keys() or buffer["Active"][lot_id]["bids"] is None:
                text += "\n\n🏁 Аукцион закончен. Победителей нет.."

            else:
                sorted_items = sorted(buffer["Active"][lot_id]["bids"].items(), key=lambda x: x[1], reverse=True)[0]
                with con:
                    user_id = con.execute(queries["user_id"], [sorted_items[0]]).fetchall()[0][0]
                    user_link = con.execute(queries["users_link"], [sorted_items[0]]).fetchall()[0][0]
                    sellers_link = con.execute(queries["lot_sellers_link"], [lot_id]).fetchall()[0][0]
                    bid_id = con.execute(queries["get_bid_id"], [user_id, sorted_items[1]]).fetchall()[0][0]
                    lot_title = con.execute(queries["lot_title"], [lot_id]).fetchall()[0][0]
                    con.execute(queries["set_winner"], [user_id, lot_id, bid_id])

                text_to_winner = texts_dict['notification_of_victory']

                text_to_winner += ("\n\nИнформация о лоте:\n"
                                   f"Название: {lot_title}\n"
                                   f"Ваша ставка: {sorted_items[1]}₽\n"
                                   f"Продавец: 👉 {sellers_link}")

                bot.send_message(chat_id=sorted_items[0], text=text_to_winner)

                text += f"\n\n🏆{sorted_items[1]}₽ {user_link[1:3]}***"

            bot.edit_message_reply_markup(chat_id=chanel, message_id=lot_message, reply_markup=None)
            bot.edit_message_caption(caption=text, chat_id=chanel, message_id=lot_message)

            if "user_opened" in buffer["Active"][str(lot_id)].keys():
                for user_id, message_id in buffer["Active"][str(lot_id)]["user_opened"].items():
                    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)
                    bot.edit_message_caption(caption=text, chat_id=user_id, message_id=message_id)

            buffer["Active"].clear()


    
#НАСТРОЙКА АДМИНИСТРАТОРОВ
def super_admin(telegram_id, message_id, button_info, call_id):
    bot.answer_callback_query(callback_query_id=call_id, )
    text = None
    if button_info == "add_admin":
        text = texts_dict[button_info]
        keyboard = SuperAdmin().add().keyboard
        # Вызов клавиатуры с кнопкой поиск по Telegram_link

    elif button_info == "change_admin":
        text = texts_dict[button_info]
        with con:
            admins = con.execute(queries['admins_settings']).fetchall()
            keyboard = SuperAdmin().changes(admins).keyboard

        # Найти всех администраторов и передать в клавиатуру
        # Нужны данные ADMINISTRATORS.ID USERS.TELEGRAM_LINK

    elif button_info == "delete_admin":
        text = texts_dict[button_info]
        with con:
            admins = con.execute(queries['admins_settings']).fetchall()
            keyboard = SuperAdmin().delete(admins).keyboard

        # Найти всех администраторов и передать в клавиатуру
        # Нужны данные ADMINISTRATORS.ID USERS.TELEGRAM_LINK

    bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=text, reply_markup=keyboard)    
  
def add_admin(telegram_id, message_id, button_info, call_id):
    bot.answer_callback_query(callback_query_id=call_id, )
    return ""


def change_admin(telegram_id, message_id, admin_id, call_id, case):
    bot.answer_callback_query(callback_query_id=call_id, )
    register_handler = []
    if case == "options":
        keyboard = SuperAdmin().changes_in_admin(admin_id).keyboard
        text = texts_dict['changing_options']

    # bot.edit_message_text(chat_id=telegram_id, message_id=message_id, text=text, reply_markup=keyboard)

    if case == "status":
        print("")
    if case == "balance":
        print("")


def delete_admin(telegram_id, message_id, admin_id, call_id):
    bot.answer_callback_query(callback_query_id=call_id, )
    return ""
    
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
    
    elif message.text.startswith("/start "):

        lot_id = message.text.split()[-1]

        keyboard = Card(lot_id).bot_card().keyboard

        with con:
            image_links = con.execute(queries["get_images_link"], [lot_id]).fetchall()[0]
            lot_price = con.execute(queries["lot_price"], [lot_id]).fetchall()[0][0]

        text = lot_information(lot_id)

        if "bids" in buffer["Active"][str(lot_id)].keys():
            last_bid = max(buffer["Active"][str(lot_id)]["bids"].values())
            for user_id, user_bid in buffer["Active"][str(lot_id)]["bids"].items():
                if user_bid == last_bid:
                    with con:
                        users_link = con.execute(queries['users_link'], [user_id]).fetchall()[0][0]

            text += "Следующая ставка: " + str(last_bid + 100) + "₽" + "\n\n"
            text += f"\n\n🥇 {last_bid}₽ {users_link[1:3]}***"

        else:
            text += "Следующая ставка: " + str(lot_price) + "₽" + "\n\n"

        if "user_opened" in buffer["Active"][str(lot_id)].keys():
            if telegram_id in buffer["Active"][str(lot_id)]["user_opened"].keys():
                bot.delete_message(telegram_id, buffer["Active"][str(lot_id)]["user_opened"][telegram_id])

        with open(image_links[0], 'rb') as image:
            message = bot.send_photo(chat_id=telegram_id, photo=image, caption=text, reply_markup=keyboard)

        if "user_opened" not in buffer["Active"][str(lot_id)].keys():
            buffer["Active"][str(lot_id)].update({"user_opened": {telegram_id: message.id}})
        else:
            buffer["Active"][str(lot_id)]["user_opened"].update({telegram_id: message.id})
            
    
    
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
                #настройка карточки лота
                '/card': (card_info, (call.id, button_info)),
                '/card_media': (card_media, (chat_id, message_id, button_info, call.id)),
                '/card_bids': (card_bids, (chat_id, button_info, call.id)),
                #подтверждение/отмена публикации лота
                '/accept': (approvement, (button_info, call.id, 'accept')),
                '/decline': (approvement, (button_info, call.id, 'decline')),
                '/bids':(),                               #!!!!доработать кнопку "удалить ставку" в истории ставок
                #настройка админов
                '/SuperAdmin': (super_admin, (chat_id, message_id, button_info, call.id)),
                '/admin_add': (add_admin, (chat_id, message_id, button_info, call.id)),
                '/admin_changes': (change_admin, (chat_id, message_id, button_info, call.id, "options")),
                '/change_status': (change_admin, (chat_id, message_id, button_info, call.id, "status")),
                '/change_balance': (change_admin, (chat_id, message_id, button_info, call.id, "balance")),
                '/admin_delete': (delete_admin, (chat_id, message_id, button_info, call.id)),
                }
    
    function, args = callback[flag][0], callback[flag][1]

    function(*args)
 
def timer():
    global remaining_time
    end_time = datetime.datetime.now() + timedelta(hours=24)

    while datetime.datetime.now() < end_time:
        remaining_time = end_time - datetime.datetime.now()

        time.sleep(1)

    send_lot("stop_auction")


def run_scheduler():
    while True:
        schedule.run_pending()
 
print("Ready")

schedule.every().day.at('11:32').do(send_lot, "notification")
schedule.every().day.at('11:33').do(send_lot, "approvement")

update_administrator(case='Обновить администраторов')

if __name__ == '__main__':
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    bot.infinity_polling()