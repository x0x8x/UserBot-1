import json
import time

import pandas


class Constants:

    def __init__(self):
        self.__appHash = "APP HASH"
        self.__appId = 1234567890
        self.__botLog = -1001234567890
        self.__botCreators = None
        self.__chatAllowed = list()
        self.__phoneNumber = "PHONE NUMBER WITH INTERNATIONAL CODE AND WITHOUT +"

    @property
    def creators(self) -> pandas.DataFrame:
        return self.__botCreators

    @property
    def chats(self) -> list:
        return self.__chatAllowed

    @chats.setter
    def chats(self, chatId: int):
        self.__chatAllowed.append(chatId)

    @property
    def hash(self) -> str:
        return self.__appHash

    @property
    def id(self) -> int:
        return self.__appId

    def loadCreators(self):
        with open("database.json", "r") as users:
            users = json.load(users)
            self.__botCreators = pandas.DataFrame(data=users["creators"], columns=list(["id", "nickname"]))
            self.__chatAllowed = users["chat"]

    @property
    def log(self) -> int:
        return self.__botLog

    @staticmethod
    def now() -> str:
        timer = time.localtime()
        return "{0}:{1}:{2} of {3}-{4}-{5}".format(str(timer.tm_hour), str(timer.tm_min), str(timer.tm_sec),
                                                   str(timer.tm_mday), str(timer.tm_mon), str(timer.tm_year))

    @property
    def phoneNumber(self) -> str:
        return self.__phoneNumber
