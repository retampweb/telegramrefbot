import telebot
from telebot import types
from collections import defaultdict
from operator import itemgetter
import re
import requests
import time

# Токен бота
TOKEN = '7272910298:AAFFNc7MqBl-TXDOWK9fXTABwlhCM1_DVuc'

# Создание экземпляра бота
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения данных пользователей
users = defaultdict(lambda: {'income': 1, 'referrals': {}, 'staked': 0, 'total_referral_income': 0, 'last_subscription_check': 0, 'last_daily_report': 0})

# Канал для подписки
CHANNEL_USERNAME = 'darkice_proj'

# Количество монет за подписку
SUBSCRIPTION_REWARD = 10

# Частота проверки подписки и рассылки (в секундах)
CHECK_INTERVAL = 24 * 60 * 60  # 1 раз в сутки

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
    btn5 = types.KeyboardButton("Получить монеты")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    
    # Приветственное сообщение
    bot.send_message(chat_id, "Добро пожаловать! Выберите действие:", reply_markup=markup)
    
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
    
    elif text == "Получить монеты":
        get_subscription_reward(chat_id)

def show_profile(chat_id):
    # Вывод информации о профиле пользователя
    profile_info = f"Ваш доход: {users[chat_id]['income']} $Daice в час\n"
    profile_info += f"Количество рефералов: {sum(len(level) for level in users[chat_id]['referrals'].values())}\n"
    profile_info += f"Заблокировано монет: {users[chat_id]['staked']} $Daice"
    bot.send_message(chat_id, profile_info)

def show_dashboard(chat_id):
    # Вывод информации о личном кабинете
    dashboard_info = f"Ваш баланс: {users[chat_id]['income']} $Daice\n"
    dashboard_info += f"Заблокировано монет: {users[chat_id]['staked']} $Daice\n"
    dashboard_info += f"Доход от рефералов: {users[chat_id]['total_referral_income']} $Daice\n"
    dashboard_info += f"Ежедневный доход от стейкинга: {users[chat_id]['staked'] * 0.05} $Daice\n\n"
    
    # Проверка подписки на канал
    if is_user_subscribed(chat_id):
        last_check = users[chat_id]['last_subscription_check']
        time_since_last_check = message.date - last_check
        
        if time_since_last_check >= CHECK_INTERVAL:
            dashboard_info += f"Вы можете получить {SUBSCRIPTION_REWARD} $Daice за подписку на канал!"
        else:
            time_remaining = CHECK_INTERVAL - time_since_last_check
            dashboard_info += f"Вы сможете получить {SUBSCRIPTION_REWARD} $Daice через {format_time(time_remaining)} за подписку на канал."
    else:
        dashboard_info += f"Подпишитесь на {CHANNEL_USERNAME}, чтобы получать {SUBSCRIPTION_REWARD} $Daice!"
    
    bot.send_message(chat_id, dashboard_info)

def get_subscription_reward(chat_id):
    if is_user_subscribed(chat_id):
        last_check = users[chat_id]['last_subscription_check']
        time_since_last_check = message.date - last_check
        
        if time_since_last_check >= CHECK_INTERVAL:
            users[chat_id]['income'] += SUBSCRIPTION_REWARD
            users[chat_id]['last_subscription_check'] = message.date
            bot.send_message(chat_id, f"Вы получили {SUBSCRIPTION_REWARD} $Daice за подписку на канал!")
        else:
            time_remaining = CHECK_INTERVAL - time_since_last_check
            bot.send_message(chat_id, f"Вы сможете получить еще {SUBSCRIPTION_REWARD} $Daice через {format_time(time_remaining)} за подписку на канал.")
    else:
        bot.send_message(chat_id, f"Подпишитесь на {CHANNEL_USERNAME}, чтобы получать {SUBSCRIPTION_REWARD} $Daice!")

def is_user_subscribed(chat_id):
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getChatMember?chat_id=@{CHANNEL_USERNAME}&user_id={chat_id}")
        member_status = response.json()["result"]["status"]
        return member_status in ["member", "administrator", "creator"]
    except:
        return False

def format_time(seconds):
    days = seconds // (24 * 60 * 60)
    seconds -= days * (24 * 60 * 60)
    hours = seconds // (60 * 60)
    seconds -= hours * (60 * 60)
    minutes = seconds // 60
    seconds -= minutes * 60
    
    time_parts = []
    if days > 0:
        time_parts.append(f"{days}д")
    if hours > 0:
        time_parts.append(f"{hours}ч")
    if minutes > 0:
        time_parts.append(f"{minutes}м")
    if seconds > 0:
        time_parts.append(f"{seconds}с")
    
    return " ".join(time_parts)

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
    bot.send_message(chat_id, f"Вы успешно присоединились к реферальной программе Dark Ice Project! Ваш доход: {users[chat_id]['income']} $Daice в час.")

def process_staking(chat_id):
    # Обработка стейкинга монет
    msg = bot.send_message(chat_id, "Введите количество монет $Daice для стейкинга:")
    bot.register_next_step_handler(msg, do_staking)

def do_staking(message):
    chat_id = message.chat.id
    try:
        stake_amount = int(message.text)
        if stake_amount <= users[chat_id]['income']:
            users[chat_id]['income'] -= stake_amount
            users[chat_id]['staked'] += stake_amount
            bot.send_message(chat_id, f"Вы заблокировали {stake_amount} $Daice для стейкинга.")
            
            # Начисление дохода от стейкинга
            daily_reward = stake_amount * 0.05
            users[chat_id]['income'] += daily_reward
            bot.send_message(chat_id, f"Ваш ежедневный доход от стейкинга: {daily_reward} $Daice")
        else:
            bot.send_message(chat_id, "Недостаточно монет $Daice для стейкинга.")
    except ValueError:
        bot.send_message(chat_id, "Некорректное значение. Введите целое число.")

def show_referral_link(chat_id):
    # Вывод реферальной ссылки
    ref_link = f"https://t.me/daiceproj_bot?start={chat_id}"
    bot.send_message(chat_id, f"Ваша реферальная ссылка: {ref_link}")

# Функция для ежедневной рассылки
def send_daily_report():
    for chat_id in users:
        last_report = users[chat_id]['last_daily_report']
        time_since_last_report = time.time() - last_report
        
        if time_since_last_report >= CHECK_INTERVAL:
            daily_income = users[chat_id]['income'] - (users[chat_id]['staked'] * 0.05)
            daily_report = f"Заберите ежедневный бонус!\n\n"
            daily_report += f"Ваш доход за последние 24 часа:\n"
            daily_report += f"- Доход от рефералов: {users[chat_id]['total_referral_income']} $Daice\n"
            daily_report += f"- Доход от стейкинга: {users[chat_id]['staked'] * 0.05} $Daice\n"
            daily_report += f"- Итого: {daily_income} $Daice\n\n"
            daily_report += f"И это еще не рекорд!"
            
            bot.send_message(chat_id, daily_report)
            users[chat_id]['last_daily_report'] = time.time()

# Запуск бота и ежедневной рассылки
while True:
    try:
        send_daily_report()
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(10)
