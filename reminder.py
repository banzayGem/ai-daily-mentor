import os
import requests
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = (
    "Ты мой напарник и ментор. Напиши короткое (3-4 предложения) утреннее "
    "напоминание в Telegram: напомни прочитать 20 страниц книги 'Человеческий фактор', "
    "порешать задачи по Python и держать фокус на стажировке и наших больших целях. "
    "Пиши энергично, по-дружески и без воды."
)

models = ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite", "gemma-4-31b-it"]
text = None

for model_name in models:
    try:
        print(f"Пробую модель {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        text = response.text
        break
    except Exception as e:
        print(f"Модель {model_name} временно недоступна: {e}")

if text:
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": text}
    res = requests.post(url, json=payload, timeout=15)

    if res.status_code == 200:
        print("Уведомление успешно улетело в Telegram!")
    else:
        print("Ошибка Telegram:", res.text)
else:
    print("Все модели сейчас заняты.")
