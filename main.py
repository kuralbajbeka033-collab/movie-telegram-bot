import telebot
from telebot import types

TOKEN = "8790815338:AAFCHS97KCnHpIjbzN4D5VwpOGXsVprPt8I"

bot = telebot.TeleBot(TOKEN)

# 🎭 жанры → фильмы
movies = {
    "комедия": ["один дома", "маска", "мистер бин"],
    "ужасы": ["оно", "заклятие", "астрал"],
    "фантастика": ["интерстеллар", "матрица", "аватар"],
    "драма": ["зеленая миля", "форрест гамп", "титаник"]
}

# 🎥 фильмы → видео
movie_videos = {
    "оно": r"C:\Users\1\OneDrive\Рабочий стол\оно.mp4",
    "форрест гамп": r"C:\Users\1\OneDrive\Рабочий стол\форрест гамп.mp4",
    "один дома": r"C:\Users\1\OneDrive\Рабочий стол\один дома.mp4",
    "матрица": r"C:\Users\1\OneDrive\Рабочий стол\матрица.mp4"
}

# 🧠 память пользователя
user_state = {}

# ▶️ старт
@bot.message_handler(commands=['start'])
def start(message):

    # клавиатура жанров
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    # кнопки жанров
    for genre in movies.keys():
        btn = types.KeyboardButton(genre)
        markup.add(btn)

    bot.send_message(
        message.chat.id,
        "🎬 Выбери жанр:",
        reply_markup=markup
    )

    user_state[message.chat.id] = {
        "step": "genre"
    }


# 💬 обработка сообщений
@bot.message_handler(func=lambda message: True)
def handle(message):

    chat_id = message.chat.id
    text = message.text.lower().strip()

    # если пользователь новый
    if chat_id not in user_state:
        user_state[chat_id] = {
            "step": "genre"
        }

    step = user_state[chat_id]["step"]

    # 🎭 выбор жанра
    if step == "genre":

        if text in movies:

            user_state[chat_id]["genre"] = text
            user_state[chat_id]["step"] = "movie"

            # клавиатура фильмов
            markup = types.ReplyKeyboardMarkup(
                resize_keyboard=True
            )

            # кнопки фильмов
            for movie in movies[text]:
                btn = types.KeyboardButton(movie)
                markup.add(btn)

            # кнопка назад
            markup.add(types.KeyboardButton("назад"))

            bot.send_message(
                chat_id,
                f"🎥 Выбери фильм из жанра '{text}':",
                reply_markup=markup
            )

        else:
            bot.send_message(
                chat_id,
                "❌ Такого жанра нет. Нажми /start"
            )

    # 🎬 выбор фильма
    elif step == "movie":

        # кнопка назад
        if text == "назад":
            start(message)
            return

        genre = user_state[chat_id]["genre"]

        if text in movies[genre]:

            # если видео есть
            if text in movie_videos:

                try:
                    with open(movie_videos[text], "rb") as video:
                        bot.send_video(chat_id, video)

                except:
                    bot.send_message(
                        chat_id,
                        "⚠️ Ошибка загрузки видео"
                    )

            else:
                bot.send_message(
                    chat_id,
                    "🎬 Фильм есть, но видео пока не добавлено 😅"
                )

            # после фильма снова выбор жанра
            start(message)

        else:
            bot.send_message(
                chat_id,
                "❌ Фильм не найден"
            )


# 🚀 запуск бота
bot.polling()