import os
from datetime import date, datetime, timedelta, timezone
import requests
from google import genai

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
TG_CHAT_ID = os.environ["TG_CHAT_ID"]

# Настройка часового пояса (МСК = UTC+3) и счётчика дней
MSK = timezone(timedelta(hours=3))
now_msk = datetime.now(MSK)
START_DATE = date(2026, 11, 13)
GOAL_DAYS = 100
current_day = (now_msk.date() - START_DATE).days + 1

# Программа фокуса и микро-задачек по дням недели (0 = Пн, 6 = Вс)
WEEKLY_PLAN = {
    0: (
        "Понедельник — Python и алгоритмы",
        "Дай 1 короткую задачку с фрагментом кода на Python (вопрос: что выведет код и почему).",
    ),
    1: (
        "Вторник — Технический английский для IT",
        "Разбери 1 полезный английский термин или фразу из документации/собеседований с примером.",
    ),
    2: (
        "Среда — Дискретная математика и логика",
        "Дай 1 компактную задачу на логику, комбинаторику, графы или булеву алгебру.",
    ),
    3: (
        "Четверг — Python (практика и чистый код)",
        "Покажи 1 приём написания чистого кода на Python (генераторы, словари, обработка исключений).",
    ),
    4: (
        "Пятница — Карьера и подготовка к стажировкам",
        "Дай 1 реальный теоретический вопрос с технического собеседования на позицию Junior/Intern.",
    ),
    5: (
        "Суббота — Архитектура пет-проекта",
        "Предложи 1 небольшую инженерную идею, как можно развить свой пет-проект или API-сервис.",
    ),
    6: (
        "Воскресенье — Ретроспектива и планирование",
        "Помоги подвести итоги недели за 3 вопроса и сформулировать главную цель на следующую неделю.",
    ),
}

focus_title, micro_task_instruction = WEEKLY_PLAN[now_msk.weekday()]

client = genai.Client(api_key=GEMINI_API_KEY)

prompt = (
    f"Ты — персональный AI-ментор для студента-разработчика.\n"
    f"Сегодня: {focus_title}. Прогресс: День #{current_day} из {GOAL_DAYS}.\n"
    f"Составь бодрое, лаконичное утреннее сообщение в Telegram (строго до 900 символов, без сложной Markdown-разметки, можно использовать эмодзи).\n"
    f"Структура сообщения:\n"
    f"1. Короткий фокус дня (2-3 конкретных шага по учёбе и коду).\n"
    f"2. Рубрика «Разминка на 1 минуту»: {micro_task_instruction}\n"
    f"Пиши по делу, без воды и банальных клише."
)

# Быстрая модель стоит первой, остальные — в резерве на случай нагрузки
models = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.7-flash",
    "gemma-4-31b-it",
]

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
    header = f"🚀 День #{current_day}/{GOAL_DAYS} | {focus_title}\n\n"
    full_message = header + text.strip()

    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TG_CHAT_ID, "text": full_message}
    res = requests.post(url, json=payload, timeout=15)

    if res.status_code == 200:
        print("Уведомление успешно улетело в Telegram!")
    else:
        print(f"Ошибка Telegram: {res.text}")
else:
    print("Все модели сейчас заняты, попробуй позже.")
