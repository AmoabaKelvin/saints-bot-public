import os

import wikipedia
from bs4 import BeautifulSoup
from PyMultiDictionary import DICT_WORDNET, MultiDictionary
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from wordhoard import Antonyms, Synonyms

import messages


def get_wikipedia_summary(query: str):
    """
    Get the summary of a query from wikipedia and return the results.
    """
    try:
        page = wikipedia.page(query)
    except wikipedia.PageError:
        return "Search did not produce any results"
    except wikipedia.DisambiguationError as error:
        return f"Please specify your search query \n{error}"
    summary = page.summary
    images = page.images
    return summary, images


def lookup(word: str) -> str:
    """Get the meaning of a word

    Args:
        word (str): The word to lookup

    Returns:
        str: Formatted Dictionary Meaning
    """
    dictionary = MultiDictionary()
    try:
        meanings = dictionary.meaning("en", word, dictionary=DICT_WORDNET)
    except IndexError:
        # If an error is raised while getting the meaning of a word, it
        # raises an INDEXERROR
        return messages.DICTIONARY_ERROR.format(word)
    antonyms = Antonyms(word).find_antonyms()
    synonyms = Synonyms(word).find_synonyms()
    if isinstance(antonyms, list):
        antonyms = "; ".join(antonyms)
    if isinstance(synonyms, list):
        synonyms = "; ".join(synonyms)
    for part_of_speech in meanings:
        meaning = (
            f"{part_of_speech}: {'; '.join(meanings.get(part_of_speech))})"
        )
    return messages.DICTIONARY_RESULTS.format(
        word, meaning, synonyms, antonyms
    )


def scrape_books_from_b_africa(book_title: str):
    """Scrape books from https://b-ok.africa

    Args:
        book_title (str): The title of the book to scrape
    """
    formatted_search_query = book_title.replace(" ", "+")
    # setup chromedriver options
    chrome_options = ChromeOptions()
    chrome_options.binary_location = os.environ["GOOGLE_CHROME_BIN"]
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(
        executable_path=os.environ["CHROMEDRIVER_PATH"], options=chrome_options
    )
    driver.get(f"https://b-ok.africa/s/?q={formatted_search_query}")
    # Extract the data using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
    book = soup.find_all("h3", {"itemprop": "name"})
    book_names = [i.text for i in book]
    book_links = [i.a.get("href") for i in book]
    return book_names, book_links
