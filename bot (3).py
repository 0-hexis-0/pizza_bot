import time
from random import *
import telebot
from telebot import types
from random import choice
from nltk import edit_distance
from time import *
import json


bot = telebot.TeleBot('6022267530:AAFvxOFkOq1tnEhOCZBbbxW40_8ydne3QHQ')


BOT_CONFIG = {
    "привет": ['Привет', 'Здравствуйте', 'Салам'],
    'как дела': ['Нормально', 'Хорошо'],
    'пока': ['До свидания', 'Пока']
}

PIZZA_SIZES = {
    'большую': 100,
    'среднюю': 75,
    'маленькую': 50
}
user_data = {}
zakaz = 0

ADMINS = [711136853,
          993627590]

prv_ord = False
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.first_name}</b>, ты можешь заказать пиццу тут, для справки напиши <u>/help</u>. А для заказа используй <u>/order</u> ', parse_mode='html')

def load_previous_order(user_id):
    with open('order.json', 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                if data['user_id'] == user_id:
                    return data
            except json.JSONDecodeError:
                continue
    return None

@bot.message_handler(commands=['order'])
def order(message):
    global zakaz
    zakaz = 1
    bot.send_message(message.chat.id, 'Подключение оператора...')
    #sleep(randint(3,20))
    bot.send_message(message.chat.id, 'Оператор подключился')
    bot.send_message(message.chat.id, choice(BOT_CONFIG['привет']))
    previous_order = load_previous_order(message.chat.id)
    if previous_order:
        bot.send_message(message.chat.id,
                         f"Ваш предыдущий заказ: {previous_order['pizza_size']} {previous_order['pizza_type']}. Оплата: {previous_order['payment_method']}. Доставка по адресу: {previous_order['delivery_address']}")


@bot.message_handler(commands=['menu'])
def menu(message):
    bot.send_message(message.chat.id, 'Вот наше меню:')
    peperoni = open('./peperoni.jpg', 'rb')
    margarita = open('./margarita.jpg', 'rb')
    sir  = open('./4sira.jpg', 'rb')
    hawaiana = open('./hawaiana.jpg', 'rb')
    bot.send_photo(message.chat.id, peperoni, caption = 'Пеперони')
    bot.send_photo(message.chat.id, margarita, caption = 'Маргарита')
    bot.send_photo(message.chat.id, sir, caption = '4 сыра')
    bot.send_photo(message.chat.id, hawaiana, caption = 'Гавайская')

@bot.message_handler(commands=['site'])
def site(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Перейти на сайт', url='https://youtu.be/dQw4w9WgXcQ')
    markup.row(btn1)
    bot.send_message(message.chat.id, 'Самая вкусная пицца здесь 🍕', reply_markup=markup)

def filter_text(text):
    text = text.lower()
    alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя -"
    result = [c for c in text if c in alphabet]
    return ''.join(result)

def match_text(text, example):
    text = filter_text(text)
    example = example.lower()
    distance = edit_distance(text, example) / len(example)
    return distance < 0.4



@bot.message_handler()
def handle(message):
    global zakaz, process_order, process_address, size, show_buttons, user_data, show_buttons_size, prv_ord
    user_text = message.text
    previous_order = load_previous_order(message.chat.id)
    if zakaz >= 1:
        if match_text(user_text, 'привет') and zakaz == 1:
            zakaz = 2
            user_data = {}
            show_buttons_size(message.chat.id)
        elif match_text(user_text, 'Повтор') and zakaz == 1:
            bot.send_message(message.chat.id, f'Вы хотите {previous_order["pizza_size"]} {previous_order["pizza_type"]} , оплата – {previous_order["payment_method"]} , доставить по адресу {previous_order["delivery_address"]}')
            zakaz = 7
            prv_ord = True
        elif zakaz == 7:
            finish(message.chat.id, user_text)
        elif 'payment' in user_data and 'address' not in user_data:
            process_address(message.chat.id, user_text)
        elif zakaz == 6:
            process_address(message.chat.id, user_text)
        else:
            bot.send_message(message.chat.id, 'Извините, я не понимаю ваш запрос.')
    elif match_text(user_text, 'привет'):
        bot.send_message(message.chat.id, f'Привет, <b>{message.from_user.first_name}</b>, ты можешь заказать пиццу тут, для справки напиши <u>/help</u>. А для заказа используй <u>/order</u>', parse_mode='html')
    else:
        bot.send_message(message.chat.id, 'Извините, я не понимаю ваш запрос.')

    def size(user_id, user_text):
        if match_text(user_text, 'большую'):
            user_data['size'] = 'большую'
            show_buttons(message.chat.id)
            zakaz = 3
        elif match_text(user_text, 'среднюю'):
            user_data['size'] = 'среднюю'
            show_buttons(message.chat.id)
            zakaz = 3
        elif match_text(user_text, 'маленькую'):
            user_data['size'] = 'маленькую'
            show_buttons(message.chat.id)
            zakaz = 3


    def show_buttons(user_id):
        markup = types.InlineKeyboardMarkup()
        pizza_buttons = [
            types.InlineKeyboardButton('Пеперони', callback_data='пеперони'),
            types.InlineKeyboardButton('4 сыра', callback_data='4 сыра'),
            types.InlineKeyboardButton('Маргарита', callback_data='маргарита'),
            types.InlineKeyboardButton('Гавайская', callback_data='гавайская')
        ]
        markup.add(*pizza_buttons)
        pizza = open('./pizza.png', 'rb')
        bot.send_photo(message.chat.id, pizza, caption='Выберите пиццу:', reply_markup=markup)
        zakaz = 4

def process_order(user_id, pizza_size):
    bot.send_message(user_id, f'Вы выбрали {user_data["size"]} {pizza_size}.')
    bot.send_message(user_id, 'Как вы будете платить?')
    markup = types.InlineKeyboardMarkup()
    pay_buttons = [
        types.InlineKeyboardButton('Безнал', callback_data='картой'),
        types.InlineKeyboardButton('наличка', callback_data='наличными'),
        types.InlineKeyboardButton('Онлайн', callback_data='онлайн'),]
    markup.add(*pay_buttons)
    bot.send_message(user_id,  'Выберите способ олаты:', reply_markup=markup)
    zakaz = 5

    user_data['payment'] = True

def process_address(user_id, address):
    global zakaz
    user_data['address'] = address
    bot.send_message(user_id, f'Вы хотите {user_data["size"]} {user_data["type"]} , оплата – {user_data["payment"]}, доставить по адресу {user_data["address"]}?')
    zakaz = 7


def pizza(user_id, user_text):
    if match_text(user_text, 'пеперони'):
        process_order(user_id, 'пеперони')
    elif match_text(user_text, '4 сыра'):
        process_order(user_id, '4 сыра')
    elif match_text(user_text, 'маргарита'):
        process_order(user_id, 'маргарита')
    elif match_text(user_text, 'гавайскую'):
        process_order(user_id, 'гавайскую')

def finish(user_id, user_text):
    global zakaz, user_data, prv_ord, r
    r = randint(1,  742974395)
    if match_text(user_text, 'да') and prv_ord == False:
        bot.send_message(user_id, 'Спасибо за заказ! Пицца будет доставлена в ближайшее время.')
        for adm in ADMINS:
            bot.send_message(adm, f'Заказ №{r}: {user_data["size"]} {user_data["type"]}. Оплата {user_data["payment"]}. Доставка {user_data["address"]} ')

        # Сохраняем данные в JSON файл
        data = {
            'user_id': user_id,
            'pizza_type': user_data['type'],
            'pizza_size': user_data['size'],
            'payment_method': user_data['payment'],
            'delivery_address': user_data['address']
        }
        save_order(user_id, data)
    elif prv_ord == True and match_text(user_text, 'да'):
        bot.send_message(user_id, 'Спасибо за заказ! Пицца будет доставлена в ближайшее время.')
        previous_order = load_previous_order(user_id)
        for adm in ADMINS:
            bot.send_message(adm, f'Заказ №{r}: {previous_order["pizza_size"]} {previous_order["pizza_type"]}. Оплата {previous_order["payment_method"]}. Доставка {previous_order["delivery_address"]}')
    else:
        bot.send_message(user_id, 'Давайте повторим ещё раз')
        bot.send_message(user_id, 'Какую пиццу вы хотите? Большую, среднюю или маленькую?')
        user_data = {}
        zakaz = 2

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global pizza, process_order,size
    if call.message:
        if call.data in ['пеперони', '4 сыра', 'маргарита', 'гавайская']:
            user_data['type'] = call.data
            pizza(call.message.chat.id, call.data)
        if call.data in ['наличными', 'картой', 'онлайн']:
            user_data['payment'] = call.data
            bot.send_message(call.message.chat.id, 'Напиши адресс доставки')
            zakaz = 6
        if call.data in ['большую', 'среднюю', 'маленькую']:
            size(call.message.chat.id, call.data)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)


def show_buttons_size(user_id):
    markup = types.InlineKeyboardMarkup()
    pizza_buttons = [
        types.InlineKeyboardButton('Большую', callback_data='большую'),
        types.InlineKeyboardButton('Среднюю', callback_data='среднюю'),
        types.InlineKeyboardButton('Маленькую', callback_data='маленькую'),
    ]
    markup.add(*pizza_buttons)
    bot.send_message(user_id, 'Какую пиццу вы хотите?:', reply_markup=markup)

def save_order(user_id, data):
    with open('order.json', 'a') as file:
        file.write(json.dumps(data) + '\n')

bot.infinity_polling()