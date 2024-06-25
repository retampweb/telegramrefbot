import telebot
from telebot import types
from collections import defaultdict
from operator import itemgetter

# Токен бота
TOKEN = '7205134080:AAElGKDakWGR3upcttIiDytEt5XVFvPC2s4'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
users = defaultdict(lambda: {'income': 1, 'referrals': {}, 'staked': 0, 'total_referral_income': 0})

# Функция для начала работы с ботом
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    
    # Создание клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Профиль")
    btn2 = types.KeyboardButton("Реферальная программа")
    btn3 = types.KeyboardButton("Стейкинг")
    btn4 = types.KeyboardButton("Личный кабинет")
    btn5 = types.KeyboardButton("Таблица лидеров")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    # Приветственное сообщение
    bot.send_message(chat_id, "Добро пожаловать в бот $CONE! Выберите действие:", reply_markup=markup)
    
    # Обработка реферальной ссылки
    ref_code = message.text.split()[1] if len(message.text.split()) > 1 else None
    if ref_code and ref_code in users:
        add_referral(chat_id, ref_code)

# Обработка нажатий на кнопки
@bot.message_handler(content_types=['text'])
def handle_text(message):
    chat_id = message.chat.id
    text = message.text
    
    if text == "Профиль":
        show_profile(chat_id)
    
    elif text == "Реферальная программа":
        show_referral_link(chat_id)
    
    elif text == "Стейкинг":
        process_staking(chat_id)
    
    elif text == "Личный кабинет":
        show_dashboard(chat_id)
    
    elif text == "Таблица лидеров":
        show_leaderboard()

def show_profile(chat_id):
    # Вывод информации о профиле пользователя
    profile_info = f"Ваш доход: {users[chat_id]['income']} $CONE в час\n"
    profile_info += f"Количество рефералов: {sum(len(level) for level in users[chat_id]['referrals'].values())}\n"
    profile_info += f"Заблокировано монет: {users[chat_id]['staked']} $CONE"
    bot.send_message(chat_id, profile_info)

def show_referral_link(chat_id):
    # Вывод реферальной ссылки
    ref_link = f"https://t.me/coincone_bot?start={chat_id}"
    bot.send_message(chat_id, f"Ваша реферальная ссылка: {ref_link}")

def process_staking(chat_id):
    # Обработка стейкинга монет
    msg = bot.send_message(chat_id, "Введите количество монет для стейкинга:")
    bot.register_next_step_handler(msg, do_staking)

def do_staking(message):
    chat_id = message.chat.id
    try:
        stake_amount = int(message.text)
        if stake_amount <= users[chat_id]['income']:
            users[chat_id]['income'] -= stake_amount
            users[chat_id]['staked'] += stake_amount
            bot.send_message(chat_id, f"Вы заблокировали {stake_amount} $CONE для стейкинга.")
        else:
            bot.send_message(chat_id, "Недостаточно монет для стейкинга.")
    except ValueError:
        bot.send_message(chat_id, "Некорректное значение. Введите целое число.")

def show_dashboard(chat_id):
    # Вывод информации о личном кабинете
    dashboard_info = f"Ваш баланс: {users[chat_id]['income']} $CONE\n"
    dashboard_info += f"Заблокировано монет: {users[chat_id]['staked']} $CONE\n"
    dashboard_info += f"Доход от рефералов: {users[chat_id]['total_referral_income']} $CONE\n"
    dashboard_info += f"Доход от стейкинга в сутки: {users[chat_id]['staked'] * 0.05} $CONE"
    bot.send_message(chat_id, dashboard_info)

def add_referral(chat_id, ref_code):
    # Добавление реферала к рефереру
    level = 0
    parent = ref_code
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
    bot.send_message(chat_id, f"Вы успешно присоединились к реферальной программе! Ваш доход: {users[chat_id]['income']} $CONE в час.")

def show_leaderboard():
    # Получение списка пользователей, отсортированных по количеству рефералов
    leaderboard = sorted(users.items(), key=lambda x: sum(len(level) for level in x[1]['referrals'].values()), reverse=True)[:100]
    
    # Формирование сообщения с таблицей лидеров
    leaderboard_msg = "Таблица лидеров:\n\n"
    leaderboard_msg += "Место | Пользователь | Количество рефералов\n"
    leaderboard_msg += "-" * 50 + "\n"
    
    for i, (user_id, user_data) in enumerate(leaderboard, start=1):
        referral_count = sum(len(level) for level in user_data['referrals'].values())
        leaderboard_msg += f"{i}. {user_id} | {referral_count}\n"
    
    # Отправка сообщения с таблицей лидеров
    bot.send_message(chat_id, leaderboard_msg)

# Запуск бота
bot.polling()
