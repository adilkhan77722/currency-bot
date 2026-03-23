import telebot
import os
import requests
import time
import sys
from flask import Flask
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8750662714:AAGWgxAMvajmhAiG8-3fTqiuRIOMW241QjM")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_rates():
    """Получает курсы валют с сайта Нацбанка РК"""
    try:
        url = "https://nationalbank.kz/rss/rates_all.xml"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            rates = {}
            for item in root.findall(".//item"):
                title = item.find("title").text if item.find("title") is not None else ""
                description = item.find("description").text if item.find("description") is not None else ""
                
                if "(" in title and ")" in title:
                    code = title.split("(")[-1].split(")")[0]
                    try:
                        rate = float(description.replace(",", "."))
                        rates[code] = rate
                    except:
                        pass
            
            rates["KZT"] = 1.0
            
            if "USD" in rates and "EUR" in rates and "RUB" in rates and "CNY" in rates:
                return {
                    "USD": rates["USD"],
                    "EUR": rates["EUR"],
                    "RUB": rates["RUB"],
                    "CNY": rates["CNY"],
                    "KZT": 1.0
                }
    except Exception as e:
        print(f"API error: {e}")
    
    # Резервные курсы
    return {
        "USD": 481.49,
        "EUR": 556.33,
        "RUB": 5.85,
        "CNY": 69.92,
        "KZT": 1.0
    }

def create_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🇰🇿 Тенге"), KeyboardButton("🇺🇸 Доллар"))
    markup.add(KeyboardButton("🇪🇺 Евро"), KeyboardButton("🇷🇺 Рубль"))
    markup.add(KeyboardButton("🇨🇳 Юань"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    text = """💱 *Курс валют к тенге* 💱

Привет! Я показываю актуальные курсы валют.

*Доступные валюты:*
🇰🇿 Тенге
🇺🇸 Доллар
🇪🇺 Евро
🇷🇺 Рубль
🇨🇳 Юань

👇 *Нажми на кнопку*"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=create_keyboard())

@bot.message_handler(func=lambda message: True)
def handle(message):
    rates = get_rates()
    text = message.text
    
    if "Доллар" in text:
        bot.send_message(message.chat.id, f"🇺🇸 *Доллар USD*\n\n1 USD = {rates['USD']:.2f} ₸\n100 USD = {rates['USD'] * 100:.2f} ₸", parse_mode="Markdown")
    elif "Евро" in text:
        bot.send_message(message.chat.id, f"🇪🇺 *Евро EUR*\n\n1 EUR = {rates['EUR']:.2f} ₸\n100 EUR = {rates['EUR'] * 100:.2f} ₸", parse_mode="Markdown")
    elif "Рубль" in text:
        bot.send_message(message.chat.id, f"🇷🇺 *Рубль RUB*\n\n1 RUB = {rates['RUB']:.2f} ₸\n100 RUB = {rates['RUB'] * 100:.2f} ₸", parse_mode="Markdown")
    elif "Юань" in text:
        bot.send_message(message.chat.id, f"🇨🇳 *Юань CNY*\n\n1 CNY = {rates['CNY']:.2f} ₸\n100 CNY = {rates['CNY'] * 100:.2f} ₸", parse_mode="Markdown")
    elif "Тенге" in text:
        bot.send_message(message.chat.id, "🇰🇿 *Тенге KZT*\n\n1 KZT = 1 ₸", parse_mode="Markdown")

@app.route('/')
def index():
    return "Bot is running!"

def run_bot():
    try:
        print("Stopping old webhook...")
        bot.remove_webhook()
        time.sleep(2)
        print("Starting bot polling...")
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    print("Starting bot...")
    thread = Thread(target=run_bot)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
