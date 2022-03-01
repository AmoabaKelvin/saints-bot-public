import os

import pymongo


class Transactor:
    """This class performs all database transactions using the mongodb
    atlas database.
    """

    def __init__(self, database_name: str, cluster: str) -> None:
        """Create a new instance of the Transactor class and then set the
        collection and database instance. The collection will be used for
        transacting database statements.

        Args:
            database_name (str): The name of the database to work with
            cluster (str): The name of the collection to work with
        """
        # Insert mongodb srv connection string in place of mongodb_srv
        self.__client = pymongo.MongoClient(os.environ["mongodb_srv"])
        self.__db = self.__client[database_name]
        self.__collection = self.__db[cluster]

    def add_user_to_database(self, username: str, chat_id: int) -> None:
        """Add a new user to the database

        Args:
            username (str): The username of the person to add
            chat_id (int): The chat id of the user to add
        """
        self.__collection.insert_one(
            {"username": username, "chat_id": chat_id}
        )

    def delete_user_from_collection(self, chat_id: int) -> None:
        """Delete a user from the database

        Args:
            chat_id (int): The chat id of the user to delete.
        """
        self.__collection.delete_one({"chat_id": chat_id})

    def retrieve_all_users(self) -> list:
        """retrive all users stored in the database

        Returns:
            list: A list containing all the user chatids
        """
        results = self.__collection.find()
        chat_ids = [i["chat_id"] for i in results]
        return chat_ids
