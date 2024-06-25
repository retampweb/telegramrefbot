Вот полный код бота с исправленными ошибками и оптимизацией:

```python
import telebot
from telebot import types
from collections import defaultdict
from operator import itemgetter
import re

# Токен бота
TOKEN = '7205134080:AAElGKDakWGR3upcttIiDytEt5XVFvPC2s4'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
users = defaultdict(lambda: {'income': 1, 'referrals': {}, 'staked': 0, 'total_referral_income': 0, 'username': ''})

# Список администраторов (chat_id)
admins = ['1065837405']

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

def process_username_ru(message):
    chat_id = message.chat.id
    username = message.text
    users[chat_id]['username'] = username
    
    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Профиль")
    btn2 = types.KeyboardButton("Реферальная программа")
    btn3 = types.KeyboardButton("Стейкинг")
    btn4 = types.KeyboardButton("Личный кабинет")
    btn5 = types.KeyboardButton("Таблица лидеров")
    btn6 = types.KeyboardButton("Админ панель")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    
    # Приветственное сообщение
    bot.send_message(chat_id, f"Добро пожаловать, {username}! Выберите действие:", reply_markup=markup)
    
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
        show_leaderboard(chat_id)
    
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

def show_profile(chat_id):
    # Вывод информации о профиле пользователя
    profile_info = f"Your income: {users[chat_id]['income']} $Daice per hour\n" if users[chat_id]['username'] else f"Ваш доход: {users[chat_id]['income']} $Daice в час\n"
    profile_info += f"Username: {users[chat_id]['username']}\n" if users[chat_id]['username'] else ""
    profile_info += f"Number of referrals: {sum(len(level) for level in users[chat_id]['referrals'].values())}\n"
    profile_info += f"Staked: {users[chat_id]['staked']} $Daice"
    bot.send_message(chat_id, profile_info)

def show_referral_link(chat_id):
    # Вывод реферальной ссылки
    ref_link = f"https://t.me/YourBotName?start={users[chat_id]['username']}"
    bot.send_message(chat_id, f"Your referral link: {ref_link}" if users[chat_id]['username'] else f"Ваша реферальная ссылка: {ref_link}")

def process_staking(chat_id):
    # Обработка стейкинга монет
    msg = bot.send_message(chat_id, "Enter the amount of $Daice to stake:" if users[chat_id]['username'] else "Введите количество монет $Daice для стейкинга:")
    bot.register_next_step_handler(msg, do_staking)

def do_staking(message):
    chat_id = message.chat.id
    try:
        stake_amount = int(message.text)
        if stake_amount <= users[chat_id]['income']:
            users[chat_id]['income'] -= stake_amount
            users[chat_id]['staked'] += stake_amount
            bot.send_message(chat_id, f"You have staked {stake_amount} $Daice." if users[chat_id]['username'] else f"Вы заблокировали {stake_amount} $Daice для стейкинга.")
        else:
            bot.send_message(chat_id, "Insufficient $Daice for staking." if users[chat_id]['username'] else "Недостаточно монет $Daice для стейкинга.")
    except ValueError:
        bot.send_message(chat_id, "Invalid value. Please enter an integer." if users[chat_id]['username'] else "Некорректное значение. Введите целое число.")

def show_dashboard(chat_id):
    # Вывод информации о личном кабинете
    dashboard_info = f"Your balance: {users[chat_id]['income']} $Daice\n" if users[chat_id]['username'] else f"Ваш баланс: {users[chat_id]['income']} $Daice\n"
    dashboard_info += f"Username: {users[chat_id]['username']}\n" if users[chat_id]['username'] else ""
    dashboard_info += f"Staked: {users[chat_id]['staked']} $Daice\n"
    dashboard_info += f"Referral income: {users[chat_id]['total_referral_income']} $Daice\n"
    dashboard_info += f"Daily staking reward: {users[chat_id]['staked'] * 0.05} $Daice"
    bot.send_message(chat_id, dashboard_info)

def add_referral(chat_id, ref_code):
    # Добавление реферала к рефереру
    level = 0
    parent = ref_code
    ref_username = users[chat_id]['username']
    
    while level < 23:
        if parent not in users[parent]['referrals']:
            users[parent]['referrals'][parent] = []
        users[parent]['referrals'][parent].append(chat_id)
        parent = users[parent]['referrals'][parent][0]
        
        # Увеличение дохода реферера в зависимости от уровня
        income_increase = users[chat_id]['income'] * (0.01 + 0.0017 * level)
        users[parent]['income'] += income_increase
        users[parent]['total_referral_income'] += income_increase
        
        level += 1
    
    # Приветственное сообщение для реферала
    bot.send_message(chat_id, f"You have successfully joined the Dark Ice Project referral program! Your income: {users[chat_id]['income']} $Daice per hour." if users[chat_id]['username'] else f"Вы успешно присоединились к реферальной программе Dark Ice Project! Ваш доход: {users[chat_id]['income']} $Daice в час.")

def show_leaderboard(chat_id):
    # Получение списка пользователей, отсортированных по количеству рефералов
    leaderboard = sorted(users.items(), key=lambda x: sum(len(level) for level in x[1]['referrals'].values()), reverse=True)[:100]
    
    # Формирование сообщения с таблицей лидеров
    leaderboard_msg = "Dark Ice Project Leaderboard:\n\n" if users[chat_id]['username'] else "Таблица лидеров Dark Ice Project:\n\n"
    leaderboard_msg += "Place | Username | Referrals\n" if users[chat_id]['username'] else "Место | Пользователь | Количество рефералов\n"
    leaderboard_msg += "-" *
