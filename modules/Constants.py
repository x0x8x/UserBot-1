import json
import time

import pandas


class Constants:

    def __init__(self):
        self.__appHash = "HASH FORM https://my.telegram.org/apps"
        self.__appId = 1234567890
        self.__botLog = -1001234567890
        self.__botAdmins = None
        self.__chat = None
        self.__creator = 0
        self.__phoneNumber = "PHONE NUMBER WITH INTERNATIONAL PREFIX AND WITHOUT THE + SIGN"

    @property
    def admins(self) -> pandas.DataFrame:
        return self.__botAdmins

    @property
    def creator(self) -> int:
        return self.__creator

    @property
    def chats(self) -> pandas.DataFrame:
        return self.__chat

    @chats.setter
    def chats(self, newChat: dict):
        self.__chat = self.__chat.append(newChat, ignore_index=True)
        element = "{\"admins\":" + self.__botAdmins.to_json(orient="records") + ",\"chat\":" + \
                  self.__chat.to_json(orient="records") + "}"
        """
            Saving the database
        """
        with open("database.json", "w") as users:
            users.write(element)

    @property
    def hash(self) -> str:
        return self.__appHash

    @property
    def id(self) -> int:
        return self.__appId

    def loadCreators(self):
        """
            Reading the database
        """
        with open("database.json", "r") as users:
            files = json.load(users)
		"""
			Setting the database
		"""
		self.__botAdmins = pandas.DataFrame(data=files["admins"], columns=list(["id", "name"]))
		self.__chat = pandas.DataFrame(data=files["chat"], columns=list(["id", "name"]))
        """
            Setting the parameters
        """
        rows = self.__botAdmins.shape[0]
        rows = range(rows)
        for i in rows:
            if self.__botAdmins.at[i, "name"] == "":
                self.__creator = int(self.__botAdmins.at[i, "id"])

    @property
    def log(self) -> int:
        return self.__botLog

    @staticmethod
    def now() -> str:
        timer = time.localtime()
        return "{}:{}:{} of {}-{}-{}".format(timer.tm_hour, timer.tm_min, timer.tm_sec,
                                             timer.tm_mday, timer.tm_mon, timer.tm_year)

    @property
    def phoneNumber(self) -> str:
        return self.__phoneNumber
