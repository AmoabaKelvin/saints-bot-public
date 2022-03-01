import os

from celery import Celery
from gtts import gTTS

import messages
from bot import bot
from transactions import Transactor

app = Celery(
    "tasks", broker=os.environ["REDIS_URL"], backend=os.environ["mongodb_srv"]
)

transactor = Transactor("telegrambot", "users")


@app.task
def send_mass_message(message_body):
    """Send a message to all users of the bot

    Args:
        message_body (str): The message to send
    """
    chat_ids = transactor.retrieve_all_users()
    for chatid in chat_ids:
        try:
            bot.send_message(chatid, message_body, parse_mode="Markdown")
        except:
            transactor.delete_user_from_collection(chatid)


@app.task
def convert_search_results_to_audio(results: str):
    """Convert text obtained from get_wikipedia_summary function to speech
    and save to a file audio.mp3

    Args:
        results (str): Search results obtained from get_wikipedia_summary
    """
    to_speech = gTTS(results)
    to_speech.save("audio.mp3")


@app.task
def convert_results_and_send(results: str, chat_id: int, title: str):
    """Convert search results to audio and send

    Args:
        results (str): _description_
    """
    results = convert_search_results_to_audio.delay(results)
    while True:
        if results.ready():
            with open(messages.AUDIO_FILE_NAME, "rb") as audio_file:
                # Only send the chat action after successfully converting
                # the results into audio
                bot.send_chat_action(chat_id, "upload_audio")
                bot.send_audio(
                    chat_id,
                    audio=audio_file,
                    title=title,
                    performer=messages.AUDIO_PERFORMER,
                )
                os.remove(messages.AUDIO_FILE_NAME)
                break


@app.task
def add_a_user_to_the_database(username: str, chat_id: int):
    """Add a user to the database if they are not already part

    Args:
        username (str): The username of the user to add
        chat_id (int): The chat id of the user to add
    """
    users = transactor.retrieve_all_users()
    if chat_id in users:
        pass
    else:
        transactor.add_user_to_database(username, chat_id)
