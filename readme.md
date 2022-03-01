# [Saints Bot](https://t.me/saints_bot) Public Repo

THIS BOT WAS BUILT USING:
- Python and pyTelegramBotAPI wrapper
- [Celery](https://docs.celeryproject.org/)
- [MongoDB](https://cloud.mongodb.com/)


### BOT FUNCTIONALITIES:
- Retrieving information from wikipedia (together with the images) and converting
results to audio.
- Getting meaning of words with a dictionary.
- Downloading books.

> This bot is on telgram and is available from [here](https://t.me/saints_bot)
---
### COMMANDS YOU CAN USE WITH THIS BOT
- To start the bot, you use the command `/start`.
- To get help for using the bot, you use the command `/help`.
- To search for the meaning of a word, you use the command `/dic <word here>`. This returns information about
  the word you've searched for, including its:

    - Part of speech 
    - Definition
    - Antonyms
    - Synonyms
    
- To search for a book, the command `/book <book name>` is used. This returns an inline keyboard containing a list of books from which you can select your desired book.  
When you select the desired book, a link to download the book will be sent and the inline keyboard deleted.