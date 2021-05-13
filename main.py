import os
import telebot
import requests
import io
from telebot import types

API_SERVER = "http://127.0.0.1:5000/"

bot = telebot.TeleBot(os.getenv("CERTS_BOT_TOKEN"))

start_markup = types.ReplyKeyboardMarkup()
btn_get_cert = types.KeyboardButton('Получить сертификат')
start_markup.add(btn_get_cert)

cancel_markup = types.ReplyKeyboardMarkup()
btn_cancel = types.KeyboardButton('Отмена')
cancel_markup.add(btn_cancel)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Начало",
                 reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Получить сертификат":
        bot.send_message(message.chat.id, "Введите ваш email",
                         reply_markup=cancel_markup)
        bot.register_next_step_handler(message, get_cert)


def get_cert(message):
    if message.text == "Отмена":
        bot.send_message(message.chat.id, "Ок",
                         reply_markup=start_markup)
        return

    email = message.text
    all_users = requests.get(API_SERVER + "api/users").json()["users"]
    user = list(filter(lambda x: x["email"] == email, all_users))

    if not len(user):
        bot.send_message(message.chat.id, "Пользователь не найден, попробуйте еще раз",
                         reply_markup=cancel_markup)
        bot.register_next_step_handler(message, get_cert)
        return

    all_certs = requests.get(API_SERVER + "api/certificates").json()["certificates"]
    user_certs = list(filter(lambda x: x["user_id"] == user[0]["id"], all_certs))

    if not len(user_certs):
        bot.send_message(message.chat.id, "Сертификаты не найдены, попробуйте еще раз",
                         reply_markup=cancel_markup)
        bot.register_next_step_handler(message, get_cert)
        return

    for cert in user_certs:
        img = requests.get(API_SERVER + "/download_cert/" + str(cert["id"])).content
        img_io = io.BytesIO(img)
        bot.send_photo(message.chat.id, img_io)
        bot.send_message(message.chat.id, "Вот все ваши сертификаты",
                         reply_markup=start_markup)



print("strt")
bot.polling()