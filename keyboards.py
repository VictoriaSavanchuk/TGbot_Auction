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

class Lot:

    def __init__(self):
        self.keyboard = InlineKeyboardMarkup()

    def creating_lot(self):
        title = InlineKeyboardButton("Название", callback_data=json.dumps(['/lot', "title"]))
        input_media = InlineKeyboardButton("Добавить изображения", callback_data=json.dumps(['/lot', "media"]))
        initial_price = InlineKeyboardButton("Стартовая цена",
                                             callback_data=json.dumps(['/lot', "price"]))
        geolocation = InlineKeyboardButton("Геолокация товара",
                                           callback_data=json.dumps(['/lot', "geolocation"]))
        description = InlineKeyboardButton("Описание", callback_data=json.dumps(['/lot', "description"]))
        additional_info = InlineKeyboardButton("Доп.информация",
                                               callback_data=json.dumps(['/lot', "additional_info"]))
        save_lot = InlineKeyboardButton("Сохранить Лот",
                                        callback_data=json.dumps(['/lot', "save_lot"]))
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(title, input_media, initial_price, geolocation,
                          description, additional_info, save_lot, main_menu, row_width=1)
        return self
    
    def quantity_of_images(self):
        one_image = InlineKeyboardButton("1 изображение", callback_data=json.dumps(['/lot', "media_1"]))
        two_image = InlineKeyboardButton("2 изображения", callback_data=json.dumps(['/lot', "media_2"]))
        three_image = InlineKeyboardButton("3 изображения", callback_data=json.dumps(['/lot', "media_3"]))
        four_image = InlineKeyboardButton("4 изображения", callback_data=json.dumps(['/lot', "media_4"]))
        backward = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "create_lot"]))
        self.keyboard.add(one_image, two_image, three_image, four_image, backward, row_width=1)
        return self
    
class BiddingHistory:   #история торгов

    def __init__(self, info):
        self.info = info
        self.keyboard = InlineKeyboardMarkup()
        
    def user_participated_lots(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, url=f"https://t.me/lePetitecocoBot?start={lot_id}")
            self.keyboard.add(title, row_width=1)
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(main_menu)
        return self