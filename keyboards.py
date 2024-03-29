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
    
    def saving_confirmation(self):
        yes = InlineKeyboardButton("Подтверждаю", callback_data=json.dumps(['/save', "confirm"]))
        no = InlineKeyboardButton("Отменить", callback_data=json.dumps(['/start', "create_lot"]))
        self.keyboard.add(no, yes, row_width=2)
        return self

    def recreate_lot(self):
        selled_lots = InlineKeyboardButton("Проданные лоты", callback_data=json.dumps(['/start', "selled_lots"]))
        unselled_lots = InlineKeyboardButton("Не проданные лоты", callback_data=json.dumps(['/start', "unselled_lots"]))
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(selled_lots, unselled_lots, main_menu, row_width=1)
        return self
    
    
class BiddingHistory:   #история торгов

    def __init__(self, info):
        self.info = info
        self.keyboard = InlineKeyboardMarkup()
        
    def show(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, callback_data=json.dumps(['/history', lot_id]))
            self.keyboard.add(title, row_width=1)
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(main_menu)
        return self
        
    def user_participated_lots(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, url=f"https://t.me/lePetitecocoBot?start={lot_id}")
            self.keyboard.add(title, row_width=1)
        main_menu = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(main_menu)
        return self
    
    def recreate_lot(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, callback_data=json.dumps(['/recreate', lot_id]))
            self.keyboard.add(title)
        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "recreate_lot"]))
        self.keyboard.add(back)
        return self
    
    def won_lot(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, callback_data=json.dumps(['/customer', lot_id]))
            self.keyboard.add(title)
        home = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(home)
        return self
    
    def winner(self):
        user_id = self.info
        payed = InlineKeyboardButton("Оплатил", callback_data=json.dumps(['/winner', user_id]))
        strike = InlineKeyboardButton("Страйк за неоплату", callback_data=json.dumps(['/winner', user_id]))  #/winner -доработать в callback
        back = InlineKeyboardButton("Назад", callback_data=json.dumps(["/start", "customers"]))
        self.keyboard.add(payed, strike, back, row_width=1)
        return self
    
    def delete_bid(self):
        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "show_history"]))
        if self.info == "ACTIVE_LOT":
            delete = InlineKeyboardButton("Удалить ставку", callback_data=json.dumps(['/bids', "delete"]))  #/bids -доработать в callback
            self.keyboard.add(delete, back, row_width=1)
        else:
            self.keyboard.add(back)
        return self
    
    def delete_lot(self):
        for lot_info in self.info:
            lot_id, lot_title = lot_info[0], lot_info[1]
            title = InlineKeyboardButton(lot_title, callback_data=json.dumps(['/delete', lot_id]))
            self.keyboard.add(title)
        home = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(home)
        return self
    

class Card:

    def __init__(self, lot_id):
        self.keyboard = InlineKeyboardMarkup()
        self.lot_id = lot_id

    def chanel_card(self):
        timer = InlineKeyboardButton("🕒", callback_data=json.dumps(['/card', "timer"]))
        info = InlineKeyboardButton("ℹ️", callback_data=json.dumps(['/card', "card_info"]))
        link = InlineKeyboardButton("Открыть лот", url=f"https://t.me/lePetitecocoBot?start={self.lot_id}")
        self.keyboard.row(timer, info)
        self.keyboard.add(link)
        return self

    def bot_card(self):
        timer = InlineKeyboardButton("🕒", callback_data=json.dumps(['/card', "timer"]))
        info = InlineKeyboardButton("ℹ️", callback_data=json.dumps(['/card', "card_info"]))
        make_bid = InlineKeyboardButton("Сделать ставку", callback_data=json.dumps(['/card_bids', self.lot_id]))
        hidden_bid_settings = InlineKeyboardButton("Настроить скрытую ставку",
                                                   callback_data=json.dumps(['/card', "hidden_bid_settings"]))
        photo_video = InlineKeyboardButton("Смотреть фото/видео",
                                           callback_data=json.dumps(['/card_media', self.lot_id]))
        self.keyboard.row(timer, info)
        self.keyboard.add(make_bid, hidden_bid_settings, photo_video, row_width=1)
        return self

class Support:  #поддержка

    def __init__(self, lot_id):
        self.keyboard = InlineKeyboardMarkup()
        self.lot_id = lot_id

    def approvement(self):
        accept = InlineKeyboardButton("Одобрить", callback_data=json.dumps(['/accept', self.lot_id]))
        decline = InlineKeyboardButton("Отклонить", callback_data=json.dumps(['/decline', self.lot_id]))
        self.keyboard.add(decline, accept, row_width=2)
        return self
    
class SuperAdmin:

    def __init__(self):
        self.keyboard = InlineKeyboardMarkup()

    def options(self):
        add = InlineKeyboardButton("Добавить администратора", callback_data=json.dumps(['/SuperAdmin', "add_admin"]))
        change = InlineKeyboardButton("Изменить администратора", callback_data=json.dumps(['/SuperAdmin', "change_admin"]))
        delete = InlineKeyboardButton("Удалить администратора", callback_data=json.dumps(['/SuperAdmin', "delete_admin"]))
        home = InlineKeyboardButton("Главное меню", callback_data=json.dumps(["/home", "menu"]))
        self.keyboard.add(add, change, delete, home, row_width=1)
        return self

    def add(self):
        telegram_link = InlineKeyboardButton("Найти пользователя по ссылке",
                                             callback_data=json.dumps(['/admin_add', "telegram_link"]))
        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "admins_settings"]))
        self.keyboard.add(telegram_link, back, row_width=1)
        return self

    def changes(self, admins):
        for admin_id, users_link in admins:
            admin = InlineKeyboardButton(users_link, callback_data=json.dumps(['/admin_changes', admin_id]))
            self.keyboard.add(admin, row_width=1)

        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "admins_settings"]))
        self.keyboard.add(back,row_width=1)
        return self

    def changes_in_admin(self, admin_id):
        status = InlineKeyboardButton("Изменить статус", callback_data=json.dumps(['/change_status', admin_id]))
        balance = InlineKeyboardButton("Изменить баланс", callback_data=json.dumps(['/change_balance', admin_id]))
        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/SuperAdmin', "change_admin"]))
        self.keyboard.add(status, balance, back, row_width=1)
        return self

    def delete(self, admins):
        for admin_id, users_link in admins:
            admin = InlineKeyboardButton(users_link, callback_data=json.dumps(['/admin_delete', admin_id]))
            self.keyboard.add(admin, row_width=1)

        back = InlineKeyboardButton("Назад", callback_data=json.dumps(['/start', "admins_settings"]))
        self.keyboard.add(back, row_width=1)
        return self
