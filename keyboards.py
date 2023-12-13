from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json

class Start:
    def __init__(self):
        self.keyboard = InlineKeyboardMarkup()
        
    def is_admin_keyboard(self):
        create_lot = InlineKeyboardButton("Создать лот", callback_data=json.dumps(['/start', "create_lot"]))
        recreate_lot = InlineKeyboardButton("Повторное создание лота",
                                            callback_data=json.dumps(['/start', "recreate_lot"]))
        customers = InlineKeyboardButton("Покупатели", callback_data=json.dumps(['/start', "customers"]))
        show_history = InlineKeyboardButton("История торгов", callback_data=json.dumps(['/start', "show_history"]))
        show_finance = InlineKeyboardButton("Финансы", callback_data=json.dumps(['/start', "show_finance"]))
        deleting_lot = InlineKeyboardButton("Удаление лота из текущего аукциона",
                                            callback_data=json.dumps(['/start', "deleting_lot"]))
        self.keyboard.add(create_lot, recreate_lot, customers, show_history, show_finance, deleting_lot, row_width=1)
        return self

        
    def is_super_admin_keyboard(self):
        create_lot = InlineKeyboardButton("Создать лот", callback_data=json.dumps(['/start', "create_lot"]))
        recreate_lot = InlineKeyboardButton("Повторное создание лота",
                                            callback_data=json.dumps(['/start', "recreate_lot"]))
        customers = InlineKeyboardButton("Покупатели", callback_data=json.dumps(['/start', "customers"]))
        show_history = InlineKeyboardButton("История торгов", callback_data=json.dumps(['/start', "show_history"]))
        show_finance = InlineKeyboardButton("Финансы", callback_data=json.dumps(['/start', "show_finance"]))
        deleting_lot = InlineKeyboardButton("Удаление лота из текущего аукциона",
                                            callback_data=json.dumps(['/start', "deleting_lot"]))
        admins_settings = InlineKeyboardButton("Настройка администраторов",
                                               callback_data=json.dumps(['/start', "admins_settings"]))
        self.keyboard.add(create_lot, recreate_lot, customers,
                          show_history, show_finance, deleting_lot, admins_settings, row_width=1)
        return self
    
    def is_user_keyboard(self):
        my_lots = InlineKeyboardButton("Мои лоты", callback_data=json.dumps(['/start', "my_lots"]))
        rules = InlineKeyboardButton("Правила", callback_data=json.dumps(['/start', "rules"]))
        help_info = InlineKeyboardButton("Помощь", callback_data=json.dumps(['/start', "help_info"]))
        self.keyboard.add(my_lots)
        self.keyboard.row(rules, help_info)    #добавляю клавиатуру ниже 2 кнопки в одну строку
        return self
    
class MainMenu:

    def __init__(self):
        self.keyboard = InlineKeyboardMarkup()

    def get_menu(self):
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(main_menu)
        return self