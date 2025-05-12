import os
import base64
import time
import json
import requests
import telebot
import telebot.apihelper
from PIL import Image
from datetime import datetime

# 🔐 Константы
TELEGRAM_TOKEN = '7660835183:AAHo41BZJD-pvWA_r8lERB4Kz_mPK72ZPD0'
FOLDER_ID = 'b1gq945gphdkvsc6dnli'
TOKEN_FILE = 'generated/iam_token.json'

# 📥 Функция загрузки актуального IAM-токена из файла
def load_iam_token():
    try:
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            token_data = json.load(f)
            return token_data["iam_token"]
    except Exception as e:
        raise Exception(f"❌ Не удалось загрузить IAM-токен: {e}")

# 🤖 Настройка Telegram
telebot.apihelper.SESSION_TIMEOUT = 120
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 📁 Папка для изображений
if not os.path.exists("generated"):
    os.makedirs("generated")

# 🔄 Генерация изображения через Yandex API
def generate_image(text):
    IAM_TOKEN = load_iam_token()

    print("📤 Запрос в Yandex API...")
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
    headers = {
        "Authorization": f"Bearer {IAM_TOKEN}",
        "X-Folder-Id": FOLDER_ID
    }
    data = {
        "modelUri": f"art://{FOLDER_ID}/yandex-art/latest",
        "generationOptions": {
            "seed": "1863",
            "aspectRatio": {"widthRatio": "2", "heightRatio": "1"}
        },
        "messages": [{"weight": "1", "text": text}]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=(10, 120))
        response.raise_for_status()
        print("✅ Запрос отправлен.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка запроса: {e}")

    request_id = response.json().get("id")
    print(f"📨 ID запроса: {request_id}")
    result_url = f"https://llm.api.cloud.yandex.net/operations/{request_id}"

    for attempt in range(30):
        print(f"⏳ Проверка статуса... Попытка {attempt + 1}/30")
        try:
            result_response = requests.get(result_url, headers=headers, timeout=(5, 30))
            result_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка при получении статуса: {e}")

        result = result_response.json()
        if result.get("done", False):
            image_base64 = result.get("response", {}).get("image")
            if not image_base64:
                raise Exception("⚠️ Ответ не содержит изображение.")

            raw_path = "generated/generated_image_raw.jpeg"
            final_path = "generated/generated_image.jpeg"
            with open(raw_path, "wb") as f:
                f.write(base64.b64decode(image_base64))

            # Масштабируем изображение с сохранением пропорций (до 600x600)
            with Image.open(raw_path) as img:
                img = img.convert("RGB")
                img.thumbnail((600, 600), Image.LANCZOS)
                img.save(final_path, "JPEG", optimize=True, quality=85)

            print("🖼️ Изображение сохранено.")
            return final_path

        time.sleep(3)

    raise TimeoutError("⏱️ Время ожидания генерации истекло.")

# 📷 Обработка команды /picture
@bot.message_handler(commands=['picture'])
def send_picture(message):
    try:
        text = message.text.split(' ', 1)[1].strip()
        bot.send_message(message.chat.id, "🛠 Генерирую изображение, пожалуйста, подождите...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📥 Запрос: {text}")

        image_path = generate_image(text)

        with open(image_path, 'rb') as doc:
            bot.send_document(message.chat.id, doc, caption="✅ Вот ваше изображение!")

    except IndexError:
        bot.reply_to(message, "❗ Укажите текст после команды. Пример:\n/picture роза в росе", parse_mode="Markdown")
    except TimeoutError as e:
        bot.reply_to(message, f"⌛ {e}")
        print(f"⛔ Таймаут: {e}")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {e}")
        print(f"🛑 Ошибка: {e}")

# 👋 Команда /start (дополнительно)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "👋 Привет! Я бот, который может сгенерировать изображение по твоему описанию.\n\n"
        "Напиши команду:\n`/picture` + текст описания.\n\nПример:\n`/picture роза в каплях росы`",
        parse_mode="Markdown"
    )

# ▶️ Старт бота
print("=" * 50)
print("🤖 AI Image Telegram Bot запущен успешно!")
print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("💬 Ожидаю команд в Telegram...")
print("=" * 50)

bot.polling()
