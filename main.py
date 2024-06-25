import telebot
from telebot import types
from collections import defaultdict
from operator import itemgetter

# Токен бота
TOKEN = '7205134080:AAElGKDakWGR3upcttIiDytEt5XVFvPC2s4'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
users = defaultdict(lambda: {'income': 1, 'referrals': {}, 'staked': 0, 'total_referral_income': 0, 'username': ''})

# Список администраторов (chat_id)
admins = ['1065837405', '']

# Функция для начала работы с ботом
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Создание клавиатуры для выбора языка
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("English")
    btn2 = types.KeyboardButton("Русский")
    markup.add(btn1, btn2)
    
    # Приветственное сообщение с выбором языка
    bot.send_message(chat_id, "Please select your language / Выберите ваш язык:", reply_markup=markup)
    
    # Обработка выбора языка
    @bot.message_handler(content_types=['text'])
    def handle_language(message):
        chat_id = message.chat.id
        language = message.text
        
        if language == "English":
            msg = bot.send_message(chat_id, "Please enter your username:")
            bot.register_next_step_handler(msg, process_username_en)
        elif language == "Русский":
            msg = bot.send_message(chat_id, "Введите ваш логин:")
            bot.register_next_step_handler(msg, process_username_ru)
        else:
            bot.send_message(chat_id, "Invalid language selection. Please try again.")

def process_username_en(message):
    chat_id = message.chat.id
    username = message.text
    users[chat_id]['username'] = username
    
    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Profile")
    btn2 = types.KeyboardButton("Referral program")
    btn3 = types.KeyboardButton("Staking")
    btn4 = types.KeyboardButton("Dashboard")
    btn5 = types.KeyboardButton("Leaderboard")
    btn6 = types.KeyboardButton("Admin panel")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    # Приветственное сообщение
    bot.send_message(chat_id, f"Welcome, {username}! Select an action:", reply_markup=markup)
    
    # Обработка реферальной ссылки
    ref_code = message.text.split()[1] if len(message.text.split()) > 1 else None
    if ref_code and ref_code in users:
        add_referral(chat_id, ref_code)

# Обработка нажатий на кнопки
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "Profile" or text == "Профиль":
        show_profile(chat_id)
    
    elif text == "Referral program" or text == "Реферальная программа":
        show_referral_link(chat_id)
    
    elif text == "Staking" or text == "Стейкинг":
        process_staking(chat_id)
    
    elif text == "Dashboard" or text == "Личный кабинет":
        show_dashboard(chat_id)
    
    elif text == "Leaderboard" or text == "Таблица лидеров":
        show_leaderboard()
    
    elif text == "Admin panel" or text == "Админ панель":
        if str(chat_id) in admins:
            show_admin_panel(chat_id)
        else:
            bot.send_message(chat_id, "You are not authorized to access the admin panel.")

def show_admin_panel(chat_id):
    # Создание клавиатуры для админ-панели
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Add referral")
    btn2 = types.KeyboardButton("Add coins")
    btn3 = types.KeyboardButton("Remove coins")
    btn4 = types.KeyboardButton("Back")
    markup.add(btn1, btn2, btn3, btn4)
    
    # Отправка сообщения с админ-панелью
    bot.send_message(chat_id, "Welcome to the admin panel. Select an action:", reply_markup=markup)
    
    # Обработка действий в админ-панели
    @bot.message_handler(content_types=['text'])
    def handle_admin_actions(message):
        chat_id = message.chat.id
        text = message.text
        
        if text == "Add referral":
            msg = bot.send_message(chat_id, "Enter the user's username to add as a referral:")
            bot.register_next_step_handler(msg, add_referral_admin)
        
        elif text == "Add coins":
            msg = bot.send_message(chat_id, "Enter the user's username and the amount of coins to add, separated by a space:")
            bot.register_next_step_handler(msg, add_coins_admin)
        
        elif text == "Remove coins":
            msg = bot.send_message(chat_id, "Enter the user's username and the amount of coins to remove, separated by a space:")
            bot.register_next_step_handler(msg, remove_coins_admin)
        
        elif text == "Back":
            show_profile(chat_id)

def add_referral_admin(message):
    chat_id = message.chat.id
    username = message.text
    
    # Поиск пользователя по логину
    for user_id, user_data in users.items():
        if user_data['username'] == username:
            add_referral(user_id, chat_id)
            bot.send_message(chat_id, f"Referral {username} added successfully.")
            return
    
    bot.send_message(chat_id, "User not found.")

def add_coins_admin(message):
    chat_id = message.chat.id
    parts = message.text.split()
    
    if len(parts) != 2:
        bot.send_message(chat_id, "Invalid format. Please enter the username and amount of coins separated by a space.")
        return
    
    username = parts[0]
    amount = int(parts[1])
    
    # Поиск пользователя по логину и добавление монет
    for user_id, user_data in users.items():
        if user_data['username'] == username:
            users[user_id]['income'] += amount
            bot.send_message(chat_id, f"{amount} $Daice added to {username}'s balance.")
            return
    
    bot.send_message(chat_id, "User not found.")

def remove_coins_admin(message):
    chat_id = message.chat.id
    parts = message.text.split()
    
    if len(parts) != 2:
        bot.send_message(chat_id, "Invalid format. Please enter the username and amount of coins separated by a space.")
        return
    
    username = parts[0]
    amount = int(parts[1])
    
    # Поиск пользователя по логину и удаление монет
    for user_id, user_data in users.items():
        if user_data['username'] == username:
            if users[user_id]['income'] >= amount:
                users[user_id]['income'] -= amount
                bot.send_message(chat_id, f"{amount} $Daice removed from {username}'s balance.")
            else:
                bot.send_message(chat_id, f"Insufficient balance for {username}.")
            return
    
    bot.send_message(chat_id, "User not found.")

# Остальные функции бота (show_profile, show_referral_link, process_staking, show_dashboard, show_leaderboard, add_referral) остаются без изменений

# Запуск бота
bot.polling()
