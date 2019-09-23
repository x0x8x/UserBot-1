import json
import time

import pandas


class Constants:

    def __init__(self):
        self.__appHash = "c814ef521255e382f68aef72612c7427"
        self.__appId = 1019898
        self.__botLog = -1001234567890
        self.__botCreators = None
        self.__phoneNumber = "393476039644"

    def creators(self) -> pandas.DataFrame:
        return self.__botCreators

    def hash(self) -> str:
        return self.__appHash

    def id(self) -> int:
        return self.__appId

    def loadCreators(self):
        with open("creators.json", "r") as users:
            self.__botCreators = pandas.DataFrame(data=json.load(users), columns=["id", "nickname"])

    def log(self) -> int:
        return self.__botLog

    @staticmethod
    def now() -> str:
        timer = time.localtime()
        return str(timer.tm_hour) + ":" + str(timer.tm_min) + ":" + str(timer.tm_sec) + " of " + str(timer.tm_mday) + \
               "-" + str(timer.tm_mon) + "-" + str(timer.tm_year)

    def phoneNumber(self) -> str:
        return self.__phoneNumber
