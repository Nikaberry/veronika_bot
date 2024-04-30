from telebot import types
from my_token import bot
from russia_cities import cities

used_words = []
max_word_score = 0
max_city_score = 0
word_score = 0
city_score = 0
current_game = None


@bot.message_handler(commands=["start"])
def hello(message):
    global used_words
    used_words = []
    markup = types.InlineKeyboardMarkup()
    rules = types.InlineKeyboardButton("Правила", callback_data='edit')
    markup.add(rules)
    start_game = types.InlineKeyboardButton("Начать новую игру", callback_data='start_game')
    markup.add(start_game)
    bot.send_message(message.chat.id, "Привет, {0.first_name}!".format(message.from_user), reply_markup=markup)
    bot.send_message(message.chat.id, 'Я бот помощник в игре в слова и игре в российские города! '
                          'Я проверяю есть ли такой город в России, говорю на какую букву нужно назвать слово '
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
        with open("max_result_words.txt", "w") as f:
            f.write(str(max_word_score))
    if city_score > max_city_score:
        max_city_score = city_score
        with open("max_result_cities.txt", "w") as f:
            f.write(str(max_city_score))

    bot.send_message(call.message.chat.id, f"Максимальный результат в игре в слова: {max_word_score}")
    bot.send_message(call.message.chat.id, f"Максимальный результат в игре в города: {max_city_score}")
    markup = types.InlineKeyboardMarkup(row_width=1)
    rules_button = types.InlineKeyboardButton("Правила ", callback_data='edit')
    start_game_button = types.InlineKeyboardButton("Начать новую игру", callback_data='start_game')
    markup.add(rules_button, start_game_button)
    bot.send_message(call.message.chat.id, "Выберите игру:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'start_game')
def choose_game(call):
    markup = types.InlineKeyboardMarkup(row_width=1)
    cities_game_button = types.InlineKeyboardButton("Игра в города", callback_data='cities_game')
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
    back_to_menu(call)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global current_game, used_words, word_score, city_score
    if current_game == "cities":
        global used_words, max_city_score, city_score
        if len(message.text.split()) != 1:
            bot.send_message(message.chat.id, "Нужно ввести одно слово!")
            return
        word = (message.text.lower()).title()
        markup = types.InlineKeyboardMarkup(row_width=1)
        if len(used_words) == 0:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови город на букву '{word[-1].upper()}'.",
                             reply_markup=markup)
            used_words.append(word)
            city_score += 1
        if word not in cities:
            bot.send_message(message.chat.id, "Такого города нет в России. Пожалуйста введите существующий город.")
            return
        if word in used_words:
            bot.send_message(message.chat.id, "Этот город уже был использован. Пожалуйста, введите другой город.")
            return
        if used_words and (used_words[-1][-1] in 'ъыь') and (word[0] != used_words[-1][-2]):
            bot.send_message(message.chat.id, f"Этот город не начинается на букву '{used_words[-1][-2].upper()}'. "
                                              f"Пожалуйста, напишите город на букву '{used_words[-1][-2].upper()}'.")
            return
        if (used_words[-1][-1] not in 'ъыь') and (word[0] != used_words[-1][-1]) :
            bot.send_message(message.chat.id, f"Этот город не начинается на букву '{used_words[-1][-1].upper()}'. "
                                              f"Пожалуйста, напишите город на букву '{used_words[-1][-1].upper()}'.")
            return
        finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
        markup.add(finish_button)
        if word[-1] in ['ъ', 'ы', 'ь']:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови город на букву '{word[-2].upper()}'.",
                             reply_markup=markup)
            used_words.append(word)
        else:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови город на букву '{word[-1].upper()}'.",
                             reply_markup=markup)
            used_words.append(word)
        city_score += 1
    elif current_game == "words":
        if len(message.text.split()) != 1:
            bot.send_message(message.chat.id, "Нужно ввести одно слово!")
            return
        word = message.text.lower()
        if word in used_words:
            bot.send_message(message.chat.id, "Это слово уже было использовано. Пожалуйста, введи другое слово.")
            return
        if used_words and (used_words[-1][-1] in 'ъыь') and (word[0] != used_words[-1][-2]):
            bot.send_message(message.chat.id, f"Это слово не начинается на букву '{used_words[-1][-2].upper()}'. "
                                              f"Пожалуйста, напиши слово на букву '{used_words[-1][-2].upper()}'.")
            return
        if used_words and (used_words[-1][-1] not in 'ъыь') and (word[0] != used_words[-1][-1]):
            bot.send_message(message.chat.id, f"Это слово не начинается на букву '{used_words[-1][-1].upper()}'. "
                                              f"Пожалуйста, напиши слово на букву '{used_words[-1][-1].upper()}'.")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        finish_button = types.InlineKeyboardButton("Завершить игру", callback_data='finish_game')
        markup.add(finish_button)
        if word[-1] in ['ъ', 'ы', 'ь']:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву '{word[-2].upper()}'.",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id, f"Отлично! Теперь назови слово, начинающееся на букву '{word[-1].upper()}'.",
                             reply_markup=markup)
        used_words.append(word)

        word_score += 1


bot.infinity_polling()
