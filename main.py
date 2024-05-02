from telebot import types
from my_token import bot
from russia_cities import cities

used_words = []
max_word_score = 0
max_city_score = 0
word_score = 0
city_score = 0
current_game = None

with open("max_result_words.txt", "r") as f:
    max_word_score = int(f.read())
with open("max_result_cities.txt", "r") as f:
    max_city_score = int(f.read())


@bot.message_handler(commands=["start"])
def hello(message):
    global used_words
    used_words.clear()
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id, "Привет, {0.first_name}!".format(message.from_user), reply_markup=markup)
    rules = types.InlineKeyboardButton("Правила", callback_data='edit')
    markup.add(rules)
    start_game = types.InlineKeyboardButton("Начать новую игру", callback_data='start_game')
    markup.add(start_game)
    bot.send_message(message.chat.id, 'Я бот помощник в игре в слова и игре в российские города! '
                                      'Я проверяю есть ли такой город в России, '
                                      'говорю на какую букву нужно назвать слово '
                                      'и главное проверяю чтобы слова не повторялись', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'edit')
def show_rules(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    back_button = types.InlineKeyboardButton("Назад", callback_data='back')
    markup.add(back_button)
    rules_text = ("Вот правила игры: "
                  "Этот бот не является <вторым игроком>, в бот нужно подряд вводить слова, "
                  "а бот будет проверять было ли уже сыграно это слово, напоминает на какую букву нужно написать "
                  "следующее слово. Если вы играете в русские города, то бот ещё проверяет есть ли такой город в "
                  "России.")
    bot.send_message(call.message.chat.id, rules_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_to_menu(call):
    global max_word_score, max_city_score, word_score, city_score
    if word_score > max_word_score:
        max_word_score = word_score
        with open("max_result_words.txt", "w") as file:
            file.write(str(max_word_score))
    if city_score > max_city_score:
        max_city_score = city_score
        with open("max_result_cities.txt", "w") as file:
            file.write(str(max_city_score))

    markup = types.InlineKeyboardMarkup(row_width=1)
    bot.send_message(call.message.chat.id, f"Максимальный результат в игре в слова: {max_word_score}",
                     reply_markup=markup)
    bot.send_message(call.message.chat.id, f"Максимальный результат в игре в города: {max_city_score}",
                     reply_markup=markup)
    rules_button = types.InlineKeyboardButton("Правила ", callback_data='edit')
    start_game_button = types.InlineKeyboardButton("Начать новую игру", callback_data='start_game')
    markup.add(rules_button, start_game_button)
    bot.send_message(call.message.chat.id, "Выберите игру:", reply_markup=markup)
    used_words.clear()


@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def choose_game(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    cities_game_button = types.InlineKeyboardButton("Игра в российские города", callback_data='cities_game')
    words_game_button = types.InlineKeyboardButton("Игра в слова", callback_data='words_game')
    markup.add(cities_game_button, words_game_button)
    bot.send_message(call.message.chat.id, "У меня есть две игры: города России и слова, что выберешь?",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'cities_game')
def start_cities_game(call):
    global current_game
    current_game = "cities"
    markup = types.InlineKeyboardMarkup(row_width=1)
    finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
    markup.add(finish_button)
    bot.send_message(call.message.chat.id, "Давай начнем игру в города! Пока в моем инвентаре есть "
                                           "только города России, "
                                           "называй города России, а я буду говорить есть ли такой город в России, "
                                           "не называли ли вы еще его, "
                                           "если да, то игра продолжится! "
                                           "Назови первый город на любую букву алфавита!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'words_game')
def start_words_game(call):
    global current_game
    current_game = "words"
    markup = types.InlineKeyboardMarkup(row_width=1)
    finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
    markup.add(finish_button)
    bot.send_message(call.message.chat.id, "Давайте начнем игру в слова! Назовите слово на любую букву.",
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'finish_game')
def finish_game(call):
    global used_words
    used_words = []
    back_to_menu(call)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_game, used_words, word_score, city_score
    if current_game == "cities":
        global used_words, max_city_score, city_score
        if len(message.text.split()) != 1:
            bot.send_message(message.chat.id, "Нужно ввести одно слово!")
            return
        city = message.text.strip().lower().capitalize()  # Приводим город к единому формату
        markup = types.InlineKeyboardMarkup(row_width=1)
        finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
        markup.add(finish_button)

        if city not in cities:
            bot.send_message(message.chat.id, f"Такого города нет в России. Пожалуйста, введите другой город.",
                             reply_markup=markup)
            return
        if city in used_words:
            bot.send_message(message.chat.id, f"Этот город уже был использован, пожалуйста введи другой город.",
                             reply_markup=markup)
        if len(used_words) == 0:
            if city[-1] in "ьъы":
                bot.send_message(message.chat.id, f"Отлично! Теперь назови город, начинающийся на букву "
                                                  f"'{city[-2].upper()}'.",
                                 reply_markup=markup)
                used_words.append(city[:-1])
                city_score += 1

            if city[-1] not in "ьъы":
                bot.send_message(message.chat.id, f"Отлично! Теперь назови город, начинающийся на букву "
                                                  f"'{city[-1].upper()}'.",
                                 reply_markup=markup)
                used_words.append(city)
                city_score += 1

        if len(used_words) == 0 or (city[0].lower() == used_words[-1][-1].lower() and city[:-1] not in used_words):
            if city[-1] in 'ьъы':
                bot.send_message(message.chat.id, f"Отлично! Теперь назови город, начинающийся на букву "
                                                  f"'{city[-2].upper()}'.",
                                 reply_markup=markup)
                used_words.append(city[:-1])
                city_score += 1
            else:
                bot.send_message(message.chat.id, f"Отлично! Теперь назови город, начинающийся на букву "
                                                  f"'{city[-1].upper()}'.",
                                 reply_markup=markup)
                used_words.append(city)
                city_score += 1
            return
        elif (used_words[-1][-1] in 'ьъы' and city not in used_words and used_words[-1][-2] == city[0] and
              city in cities):
            bot.send_message(message.chat.id, f"Отлично! Теперь назови город, начинающийся на букву "
                                              f"'{city[-1].upper()}'.",
                             reply_markup=markup)
            used_words.append(city)
            city_score += 1
            return
        elif city[-1] != used_words[-1][-1].lower() and city[-2] != used_words[-1][-1].lower():
            bot.send_message(message.chat.id, f"Этот город не начинается на букву '{used_words[-1][-1].upper()}'. "
                                              f"Пожалуйста, напишите город на букву '{used_words[-1][-1].upper()}'.",
                             reply_markup=markup)
            return

    elif current_game == "words":
        if len(message.text.split()) != 1:
            bot.send_message(message.chat.id, "Нужно ввести одно слово!")
            return
        word = message.text.lower()
        markup = types.InlineKeyboardMarkup(row_width=1)
        finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
        markup.add(finish_button)

        if len(used_words) == 0:
            if word[-1] in "ьъы":
                bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву "
                                                  f"'{word[-2].upper()}'.",
                                 reply_markup=markup)

            if word[-1] not in "ьъы":
                bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву "
                                                  f"'{word[-1].upper()}'.",
                                 reply_markup=markup)
            used_words.append(word)
            word_score += 1
            return
        elif word in used_words:
            bot.send_message(message.chat.id, "Это слово уже было использовано. Пожалуйста, введите другое слово.",
                             reply_markup=markup)
        elif word[-1] in "ьъы" and word not in used_words:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву "
                                              f"'{word[-2].upper()}'.",
                             reply_markup=markup)
            used_words.append(word)
            word_score += 1
            return
        elif word[-1] not in "ьъы" and word not in used_words:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву "
                                              f"'{word[-1].upper()}'.",
                             reply_markup=markup)
            used_words.append(word)
            word_score += 1
            return


@bot.message_handler(content_types=["photo"])
def get_photo(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    bot.send_message(message.chat.id, f"Хорошее фото, но я отвечаю только на текст!",
                     reply_markup=markup)


bot.infinity_polling()
