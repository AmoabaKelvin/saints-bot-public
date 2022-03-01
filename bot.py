import logging
import os

import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.util import split_string

import messages
import tasks
import utils
from transactions import Transactor

logging.basicConfig(level=logging.DEBUG, filename="log.log")


bot = telebot.TeleBot(os.environ["BOT_TOKEN"])  # Paste bot token here
transactor = Transactor("telegrambot", "users")


@bot.message_handler(commands=["start"])
def respond_to_start_command(message):
    """Respond to start command"""
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id, messages.WELCOME_MESSAGE, parse_mode="Markdown"
    )
    tasks.add_a_user_to_the_database.delay(
        message.chat.username, message.chat.id
    )


@bot.message_handler(commands=["help"])
def respond_to_help_command(message):
    """Send help message to requesting user"""
    bot.send_chat_action(message.chat.id, "typing")
    bot.send_message(
        message.chat.id, messages.HELP_MESSAGE, parse_mode="Markdown"
    )


@bot.message_handler(commands=["dic"])
def lookup_word(message):
    """Lookup the meaning of a word"""
    word_to_lookup = message.text.replace("/dic", "")
    bot.send_chat_action(message.chat.id, "typing")
    dictionary_result = utils.lookup(word_to_lookup)
    # Sometimes the characters are more than the maximum 4096, hence, the
    # results is splitted and then sent to the user.
    splitted_text = split_string(dictionary_result, 4000)
    for text in splitted_text:
        bot.send_message(message.chat.id, text, parse_mode="Markdown")


@bot.message_handler(commands=["update"])
def process_update_command(message):
    """Process the update command by sending an update message to the users
    of the bot. The chat id of the sender is checked whether it matches
    that of the bot owner, if it does, it moves on to send the messages
    to the users.
    """
    bot.send_chat_action(message.chat.id, "typing")
    if message.chat.id != int(os.environ["SAINTS_BOT_SUPERUSER"]):
        bot.send_message(
            message.chat.id, messages.NOT_AUTHORIZED, parse_mode="Markdown"
        )
    else:
        update_message = message.text.replace("/update", "")
        # A celery task is used to send the mass message to the users.
        # This is to prevent the bot from not being able to respond to
        # incoming messages until the function has finished.
        tasks.send_mass_message.delay(update_message)


@bot.message_handler(commands=["book"])
def download_ebook(message):
    """Search for books and send the user a keyboard to select their desired
    book from the list of books
    """
    bot.send_chat_action(message.chat.id, "typing")
    names, links = utils.scrape_books_from_b_africa(
        message.text.replace("/download", "")
    )
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for index, value in enumerate(names):
        markup.add(InlineKeyboardButton(value, callback_data=links[index]))
    bot.send_message(message.chat.id, "Select your book", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def download_book_and_send(callback):
    """Send the download link of a book to the user"""
    bot.send_chat_action(callback.message.chat.id, "typing")
    book_url = callback.data
    full_link_to_book = messages.B_OK_LINK + book_url
    bot.send_message(
        callback.message.chat.id,
        messages.BOOK_LINK.format(full_link_to_book),
        disable_web_page_preview=True,
    )
    bot.delete_message(callback.message.chat.id, callback.message.id)


@bot.message_handler(content_types=["text"])
def handle_all_text(message):
    """Respond to all non commands by calling the wikipedia function"""
    bot.send_chat_action(message.chat.id, "typing")
    function_results = utils.get_wikipedia_summary(message.text + ".")
    if isinstance(function_results, tuple):
        # If the results from the function is a tuple, go ahead and unpack
        # the values into the summary and images variable.
        summary, images = function_results
        splitted_summary = split_string(summary, 4000)
        for summary in splitted_summary:
            bot.send_message(message.chat.id, summary)
        bot.send_chat_action(message.chat.id, "upload_photo")
        for i in images[:4]:
            try:
                bot.send_photo(message.chat.id, photo=i)
            except:
                pass
        # A celery task handles the sending of conversion of text to audio
        # and also sending the audio file to the user.
        tasks.convert_results_and_send.delay(
            summary, message.chat.id, message.text
        )
    else:
        bot.send_message(message.chat.id, function_results)


if __name__ == "__main__":
    while True:
        bot.infinity_polling(timeout=100)
