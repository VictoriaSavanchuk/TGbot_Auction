import time
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
import gspread
import json
import sqlite3 as sl

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
buffer = {}
#регистрация обработчика для получения текста, через название кнопки
handler_register =[]         

def update_administrator(case):
    if case == 'Обновить администраторов':
        with con:
            administrators = con.execute(queries['find_admins']).fetchall()
            print(administrators)
            print("\n\n")
        for admin in administrators:
            print(admin)
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

def personal_cabinet():
    pass

@bot.message_handler(content_types=['text'])

def start(message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    telegram_id = message.from_user.id
    telegram_link = "@" + message.from_user.username
    menu = {'/start':'', '/help':''}
    
    with con:
        searching = con.execute(queries['find_user'], [telegram_id]).fetchall()
        
        if not searching:    #если пустой список
            con.execute(queries['add_user'], [first_name, last_name, telegram_id, telegram_link])
    if message.text in menu.keys():
        pass
            
    
    
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id, )
    id = call.message.chat.id
    flag = call.data[0]
    data = call.data[1:]
    if flag == "1": 
        pass
    
  
print("Ready")
update_administrator(case='Обновить администраторов')
bot.infinity_polling()