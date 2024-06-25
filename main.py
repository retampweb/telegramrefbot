import telebot
from telebot import types

# Токен бота
TOKEN = '7205134080:AAElGKDakWGR3upcttIiDytEt5XVFvPC2s4'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
users = {}

# Функция для начала работы с ботом
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Профиль")
    btn2 = types.KeyboardButton("Реферальная программа")
    btn3 = types.KeyboardButton("Стейкинг")
    markup.add(btn1, btn2, btn3)
    
    # Приветственное сообщение
    bot.send_message(chat_id, "Добро пожаловать в бот $CONE! Выберите действие:", reply_markup=markup)
    
    # Инициализация данных пользователя
    users[chat_id] = {'income': 1, 'referrals': [], 'staked': 0}

# Обработка нажатий на кнопки
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "Профиль":
        # Вывод информации о профиле пользователя
        profile_info = f"Ваш доход: {users[chat_id]['income']} $CONE в час\n"
        profile_info += f"Количество рефералов: {len(users[chat_id]['referrals'])}\n"
        profile_info += f"Заблокировано монет: {users[chat_id]['staked']} $CONE"
        bot.send_message(chat_id, profile_info)
    
    elif text == "Реферальная программа":
        # Вывод реферальной ссылки
        ref_link = f"https://t.me/coincone_bot?start={chat_id}"
        bot.send_message(chat_id, f"Ваша реферальная ссылка: {ref_link}")
    
    elif text == "Стейкинг":
        # Обработка стейкинга монет
        stake_amount = int(input("Введите количество монет для стейкинга: "))
        if stake_amount <= users[chat_id]['income']:
            users[chat_id]['income'] -= stake_amount
            users[chat_id]['staked'] += stake_amount
            bot.send_message(chat_id, f"Вы заблокировали {stake_amount} $CONE для стейкинга.")
        else:
            bot.send_message(chat_id, "Недостаточно монет для стейкинга.")

# Обработка реферальных ссылок
@bot.message_handler(commands=['start'])
def handle_referral(message):
    chat_id = message.chat.id
    
    # Получение реферального кода из ссылки
    ref_code = message.text.split()[1]
    
    # Добавление реферала к рефереру
    if ref_code in users:
        users[ref_code]['referrals'].append(chat_id)
        
        # Увеличение дохода реферера
        income_increase = users[ref_code]['income'] * 0.1
        users[ref_code]['income'] += income_increase
        
        # Приветственное сообщение для реферала
        bot.send_message(chat_id, f"Вы успешно присоединились к реферальной программе! Ваш доход: {users[chat_id]['income']} $CONE в час.")
    
    # Инициализация данных нового пользователя
    users[chat_id] = {'income': 1, 'referrals': [], 'staked': 0}

# Запуск бота
bot.polling()
