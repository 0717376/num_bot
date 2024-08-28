import telebot
from telebot import types
import random
import os

# Получение токена из переменных окружения
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

# Хранение данных пользователей
user_data = {}

# Список ID стикеров с похвалой
praise_stickers = [
    'CAACAgIAAxkBAAEICjZmzjQgDJ0dcXz7nunXQk1jLLYPdQACDhsAApwiuEkaScQf14vkKzUE',
    'CAACAgIAAxkBAAEIClxmzjbcOWPBbtVWwwJik-zx4oB7ZAAC4RUAArRM2EnZ3DPB3rAICDUE',
    'CAACAgIAAxkBAAEICl5mzjcLVSLr3I2bJv4UWETYYX0uIgAC6yMAAj_lAUl35ZIodwxRkzUE',
    'CAACAgIAAxkBAAEIC1Rmzrbw_JA70hUz5_BWRcRk0UYyygACKAADobYRCH5VjnpjDnyLNQQ',
    'CAACAgIAAxkBAAEIC1Zmzrb-Krn9a0dIojZcmTZQCQS78gACIQADobYRCLB2DtJROSocNQQ',
    'CAACAgIAAxkBAAEIC1hmzrcq0eyW2GOwhU_eqBWEI7mbqAAC_xUAAgd-mEgrOaYxLXYgcDUE',
    'CAACAgIAAxkBAAEIC1pmzrdLhmxoeY7sk4cwNo9fvk-qWgAC4BkAAgWGEUsQOIwgB92ENjUE',
    'CAACAgIAAxkBAAEIC1xmzreB43ysBA0V2_467G1ye3hJ0wACEgADsND4DJVGMt3eogspNQQ',
    'CAACAgQAAxkBAAEIC15mzreS5gMCTuhaMEmZa8wxeZenfgAClwADzjkIDUAhLnyAYFYaNQQ',
    'CAACAgIAAxkBAAEIC2Jmzrfx8q8k7P60DIBDzYjivTJU5gACqwIAAhxxMAKXUlbZPNg4ajUE',
    'CAACAgIAAxkBAAEIC2Rmzrgsn-3ZxgLAU-cDLcNmS_O8awAC9wgAAhhC7gjpheyLD1rqiTUE',
    'CAACAgQAAxkBAAEIC15mzreS5gMCTuhaMEmZa8wxeZenfgAClwADzjkIDUAhLnyAYFYaNQQ',
    'CAACAgIAAxkBAAEIC1JmzrbP3lb6jnPAI5QeO6YP53tayQACEQADobYRCIFNsq5T0aHMNQQ'
]

def generate_question():
    """Генерация вопроса и вариантов ответов на основе таблицы умножения от 1 до 9"""
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    correct_answer = a * b
    options = [correct_answer]
    while len(options) < 4:
        wrong_answer = random.randint(1, 81)
        if wrong_answer != correct_answer and wrong_answer not in options:
            options.append(wrong_answer)
    random.shuffle(options)
    return f"{a} × {b}", correct_answer, options

def get_main_keyboard():
    """Создание основной клавиатуры"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(types.KeyboardButton('Играть'), types.KeyboardButton('Статистика'))
    keyboard.add(types.KeyboardButton('Сбросить статистику'))
    return keyboard

def get_game_keyboard(options):
    """Создание клавиатуры для выбора ответа с добавлением кнопки 'Главное меню'"""
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(str(option)) for option in options])
    keyboard.add(types.KeyboardButton('Главное меню'))
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Приветствие нового пользователя и отображение главного меню"""
    user_data[message.chat.id] = {
        "score": 0,
        "max_score": 0,
        "current_streak": 0,
        "difficulty": 1
    }
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}! Давай поиграем в таблицу умножения!", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Играть')
def play_game(message):
    """Начало игры"""
    question, correct_answer, options = generate_question()
    markup = get_game_keyboard(options)
    bot.send_message(message.chat.id, f"Сколько будет {question}?", reply_markup=markup)
    bot.register_next_step_handler(message, check_answer, correct_answer)

def check_answer(message, correct_answer):
    """Проверка ответа пользователя и обновление статистики"""
    if message.text == 'Главное меню':
        send_welcome(message)
        return

    user = user_data[message.chat.id]
    try:
        if int(message.text) == correct_answer:
            user['current_streak'] += 1
            user['score'] = max(user['score'], user['current_streak'])
            user['max_score'] = max(user['max_score'], user['current_streak'])
            
            sticker = random.choice(praise_stickers)
            bot.send_sticker(message.chat.id, sticker)
            bot.send_message(message.chat.id, f"Правильно! Молодец, {message.from_user.first_name}! 🎉\nТвой текущий счет: {user['current_streak']}\nТвой рекорд: {user['max_score']}")
        else:
            bot.send_message(message.chat.id, f"Не совсем верно, но ты молодец, что стараешься! Правильный ответ: {correct_answer}.")
            user['current_streak'] = 0
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, выбери один из предложенных вариантов ответа.")
    
    play_game(message)

@bot.message_handler(func=lambda message: message.text == 'Статистика')
def show_stats(message):
    """Показ статистики пользователя"""
    user = user_data.get(message.chat.id, {"score": 0, "max_score": 0})
    bot.send_message(message.chat.id, f"Твоя статистика:\nТекущий счет: {user['score']}\nРекорд: {user['max_score']}", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Сбросить статистику')
def reset_stats(message):
    """Сброс статистики пользователя"""
    user_data[message.chat.id] = {
        "score": 0,
        "max_score": 0,
        "current_streak": 0,
        "difficulty": 1
    }
    bot.send_message(message.chat.id, "Твоя статистика была сброшена.", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: message.text == 'Главное меню')
def go_to_main_menu(message):
    """Возвращение в главное меню"""
    send_welcome(message)

bot.polling()