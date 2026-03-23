import telebot
import os
import requests
from flask import Flask
from threading import Thread
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8750662714:AAGWgxAMvajmhAiG8-3fTqiuRIOMW241QjM")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def get_rates():
    """Получает курсы валют из Frankfurter API (данные ЕЦБ)"""
    try:
        # Получаем курсы относительно евро
        url = "https://api.frankfurter.app/latest?from=EUR"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if "rates" in data:
            rates_eur = data["rates"]
            
            # Курс евро к тенге
            eur_to_kzt = rates_eur.get("KZT", 535.00)
            
            # Получаем курс доллара к евро
            usd_to_eur = rates_eur.get("USD", 1.05)
            
            return {
                "USD": eur_to_kzt / usd_to_eur,     # USD в тенге
                "EUR": eur_to_kzt,                  # EUR в тенге
                "RUB": rates_eur.get("RUB", 0) * eur_to_kzt,
                "CNY": rates_eur.get("CNY", 0) * eur_to_kzt,
                "KZT": 1.0
            }
    except Exception as e:
        print(f"API error: {e}")
    
    # Резервные курсы (если API недоступен)
    return {
        "USD": 495.50,
        "EUR": 538.20,
        "RUB": 5.95,
        "CNY": 68.30,
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

Привет! Я показываю актуальные курсы валют от Европейского Центробанка.

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
        bot.remove_webhook()
        bot.infinity_polling()
    except Exception as e:
        print(f"Bot error: {e}")

if __name__ == "__main__":
    print("Starting bot...")
    thread = Thread(target=run_bot)
    thread.start()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
