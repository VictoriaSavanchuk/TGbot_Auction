import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import gspread
import json
import sqlite3 as sl
from keyboards import * 

with open ('config.json') as settings:
    config = json.load(settings)
    Token = config.get("telegram_token")
    database = config.get("database_path")
    geocoder_api = config.get("geocoder_api")
    chanel = config.get("chanel_id")
    queries = config.get("queries")

    
bot = telebot.TeleBot(Token)
con = sl.connect(database, check_same_thread=False)     #check_same_thread=False  обращение в разных потоках

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
handler_register =[]       

with con:
    admin_for_top_up_your_balance = con.execute(queries['find_admin_for_top_up_your_balance']).fetchone()
    #print(admin_for_top_up_your_balance)  #('@Zenagar',)
    texts_dict = { "create_lot": "Заполните всю необходимую информацию о новом лоте:\n",
               "recreate_lot": "Выберите лоты из которых необходимо пересоздать лот",
                "customers": "Выберите лот у которого есть победитель: ",
                "show_history": ("Вы можете посмотреть историю торгов для вашего лота:\n"
                               "Выберите название если вы добавляли лот"),
                "show_finance": f"Для пополнения баланса обратитесь к администратору {admin_for_top_up_your_balance[0]}",
                "deleting_lot": ("Если вы удалите лот из текущего аукциона то площадка\n"
                               "отнимет от баланса комиссию в размере 5% от текущей\n"
                               "стоимости лота"),
                "/start for admin": ('в бот аукционов @lePetitecocoBot '
                                   'Выберите необходимыe для вас действия:'),
                "admins_settings": "Выберите необходимые действия с администраторами:",
                "/start for user": ('Привет ,я бот аукционов @lePetitecocoBot\n'
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
                            f"При проблемах или нахождении ошибок пишите {admin_for_top_up_your_balance[0]}"),}  

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
    
    if button_info == "my_lots":  # Лоты которые, открыл пользователь в кабинете пользователя
        lots = []
        if buffer["Active"] is not None:
            for lot_id in buffer['Active'].keys():
                if "bids" in buffer["Active"][str(lot_id)].keys():   #ставка
                    if telegram_id in buffer["Active"][str(lot_id)]['bids'].keys():
                        with con:
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
     
                        
    send = {"send": [bot.send_message, {'chat_id': telegram_id, "text": text, "reply_markup": selected_action}],
            "edit": [bot.edit_message_text, {'chat_id': telegram_id, 'message_id': message_id, "text": text,
                                             "reply_markup": selected_action}]}

    function, kwargs = send[type_of_message][0], send[type_of_message][1]
    function(**kwargs)
    
    
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
                }
    
    function, args = callback[flag][0], callback[flag][1]

    function(*args)
    
  
print("Ready")
update_administrator(case='Обновить администраторов')
bot.infinity_polling()