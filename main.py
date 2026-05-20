import os
import django
import telebot
from telebot import types



# =========================
# Django setup
# =========================

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'cinemas.settings'
)

django.setup()

# =========================
# Models
# =========================

from movies.models import (
    TelegramUser,
    Genre,
    Movie,

)

# =========================
# TOKEN
# =========================

TOKEN = "8790815338:AAFCHS97KCnHpIjbzN4D5VwpOGXsVprPt8I"

bot = telebot.TeleBot(TOKEN)

# =========================
# Память пользователей
# =========================

user_state = {}

# =========================
# FAQ ответы
# =========================

faq_answers = {

    "привет": "👋 Привет! Я бот с фильмами.",

    "как дела": "😊 Отлично! Готов подобрать фильм.",

    "что ты умеешь":
        "🎬 Я умею показывать фильмы по жанрам.",

    "помощь":
        "ℹ️ Напиши /help для подробной информации.",

    "спасибо":
        "❤️ Пожалуйста!",

    "пока":
        "👋 Пока! Возвращайся за фильмами.",

    "кто ты":
        "🤖 Я Telegram-бот для просмотра фильмов.",

    "топ фильм":
        "🔥 Попробуй выбрать жанр Боевик или Комедия.",

    "лучший фильм":
        "⭐ У каждого свой вкус 😄",

    "что посмотреть":
        "🍿 Выбери жанр и я помогу.",

    "hello":
        "👋 Hello!"
}

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):

    # сохраняем пользователя
    TelegramUser.objects.get_or_create(
        chat_id=message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    # получаем жанры
    genres = Genre.objects.all()

    # клавиатура
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    # добавляем жанры
    for genre in genres:

        btn = types.KeyboardButton(
            genre.name
        )

        markup.add(btn)

    # сообщение
    bot.send_message(
        message.chat.id,
        "🎬 Выбери жанр:",
        reply_markup=markup
    )

    # состояние пользователя
    user_state[message.chat.id] = {
        "step": "genre"
    }

# =========================
# HELP
# =========================

@bot.message_handler(commands=['help'])
def help_command(message):

    help_text = """
🤖 ПОМОЩЬ ПО БОТУ

Этот бот создан для просмотра фильмов.

📌 Как работает бот:

1️⃣ Пользователь нажимает /start

2️⃣ Бот получает жанры из базы данных Django

3️⃣ На экране появляются кнопки жанров

4️⃣ После выбора жанра бот показывает фильмы

5️⃣ Пользователь выбирает фильм

6️⃣ Бот отправляет видео и описание фильма

━━━━━━━━━━━━━━━

📚 Что использует проект:

• Python
• Django
• pyTelegramBotAPI
• Telegram Bot API
• SQLite

━━━━━━━━━━━━━━━

🧠 Алгоритмы обработки текста:

✔ перевод текста в нижний регистр
✔ удаление пробелов
✔ поиск жанров
✔ поиск фильмов
✔ обработка команд
✔ поддержка диалога
✔ ответы на неизвестные сообщения

━━━━━━━━━━━━━━━

💬 Команды:

/start — запуск бота
/help — помощь

━━━━━━━━━━━━━━━

🎬 Возможности бота:

• выбор жанров
• просмотр фильмов
• отправка видео
• описание фильма
• кнопки Telegram
• поддержка диалога


⚡ Если бот не отвечает:

1. Проверь TOKEN
2. Проверь интернет
3. Запусти:
py manage.py runserver
py main.py
"""

    bot.send_message(
        message.chat.id,
        help_text
    )

# =========================
# ОБРАБОТКА СООБЩЕНИЙ
# =========================

@bot.message_handler(func=lambda message: True)
def handle(message):

    chat_id = message.chat.id
    text = message.text.lower().strip()

    # новый пользователь
    if chat_id not in user_state:

        user_state[chat_id] = {
            "step": "genre"
        }

    # =========================
    # FAQ / диалог
    # =========================

    if text in faq_answers:

        bot.send_message(
            chat_id,
            faq_answers[text]
        )

        return

    # текущее состояние
    step = user_state[chat_id]["step"]

    # =========================
    # ВЫБОР ЖАНРА
    # =========================

    if step == "genre":

        # поиск жанра
        genre = Genre.objects.filter(
            name__iexact=text
        ).first()

        # если жанр найден
        if genre:

            user_state[chat_id]["genre"] = genre.id
            user_state[chat_id]["step"] = "movie"

            # фильмы
            movies_list = Movie.objects.filter(
                genre=genre
            )

            # клавиатура
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True
            )

            # кнопки фильмов
            for movie in movies_list:

                btn = types.KeyboardButton(
                    movie.title
                )

                markup.add(btn)

            # кнопка назад
            markup.add(
                types.KeyboardButton("назад")
            )

            bot.send_message(
                chat_id,
                f"🎥 Выбери фильм из жанра '{genre.name}':",
                reply_markup=markup
            )

        else:

            bot.send_message(
                chat_id,
                "❌ Такого жанра нет.\nПроверь правильность ввода.\nВыбери жанр кнопками."
            )

    # =========================
    # ВЫБОР ФИЛЬМА
    # =========================

    elif step == "movie":

        # назад
        if text == "назад":

            start(message)
            return

        # поиск фильма
        movie = Movie.objects.filter(
            title__iexact=text
        ).first()

        # если найден
        if movie:

            # =========================
            # ОТПРАВКА ВИДЕО
            # =========================

            if movie.video:

                try:

                    with open(
                        movie.video.path,
                        "rb"
                    ) as video:

                        bot.send_video(
                            chat_id,
                            video,
                            caption=f"🎬 {movie.title}",
                            timeout=300
                        )

                except Exception as e:

                    bot.send_message(
                        chat_id,
                        f"⚠️ Ошибка загрузки видео:\n{e}"
                    )

            else:

                bot.send_message(
                    chat_id,
                    "🎬 Видео пока не добавлено"
                )

            # =========================
            # ОПИСАНИЕ
            # =========================

            bot.send_message(
                chat_id,
                f"""
🎥 Название: {movie.title}

📖 Описание:
{movie.description}
"""
            )

            # возврат в меню
            start(message)

        else:

            bot.send_message(
                chat_id,
                "❌ Фильм отсутствует в базе данных.\nВыбери фильм кнопками."
            )

# =========================
# ЗАПУСК БОТА
# =========================

print("Бот запущен...")

bot.infinity_polling()