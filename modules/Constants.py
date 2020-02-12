import json
import time
import subprocess

import pandas


class Constants:

	def __init__(self):
		self.__appHash = "HASH"
		self.__appId = 0
		self.__botAdmins = None
		self.__botLog = -0
		self.__botUsername = "UserBot"
		self.__chat = None
		self.__creator = 0
		pwd = str(subprocess.check_output("pwd", shell=True))
		pwd = pwd.replace("b\'", "")
		pwd = pwd.replace("\\n\'", "")
		if pwd == "/":
			self.__path = "home/USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home":
			self.__path = "USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER":
			self.__path = "Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER/Documents":
			self.__path = "gitHub/{}/".format(self.__botUsername)
		elif pwd == "/home/USER/Documents/gitHub":
			self.__path = "{}/".format(self.__botUsername)
		elif pwd == "/root":
			self.__path = "/home/USER/Documents/gitHub/{}/".format(self.__botUsername)
		elif pwd == "/data/data/com.termux/files/home":
			self.__path = "downloads/{}/".format(self.__botUsername)
		elif pwd == "/data/data/com.termux/files/home/downloads":
			self.__path = "{}/".format(self.__botUsername)
		else:
			self.__path = "./"
		self.__phoneNumber = "PHONE NUMBER WITH PREFIX AND WITHOUT +"

	@property
	def admins(self) -> pandas.DataFrame:
		return self.__botAdmins

	@admins.setter
	def admins(self, newAdmin: list):
		self.__botAdmins = self.__botAdmins.append(newAdmin, ignore_index=True)
		element = "{\"admins\":" + self.__botAdmins.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + ",\"chat\":" + \
				  self.__chat.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + "}"
		"""
			Saving the database
		"""
		with open("{}database.json".format(self.__path), "w") as users:
			users.write(element)

	@admins.deleter
	def admins(self):
		self.__botAdmins = pandas.DataFrame(data=dict(), columns=list(["id", "is_self", "is_contact",
																	   "is_mutual_contact", "is_deleted",
																	   "is_bot", "is_verified", "is_restricted",
																	   "is_scam", "is_support", "first_name",
																	   "last_name", "username", "language_code",
																	   "phone_number"]))
		element = "{\"admins\": [],\"chat\":" + self.__chat.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + "}"
		"""
			Saving the database
		"""
		with open("{}database.json".format(self.__path), "w") as users:
			users.write(element)

	@property
	def creator(self) -> int:
		return self.__creator

	@property
	def chats(self) -> pandas.DataFrame:
		return self.__chat

	@chats.setter
	def chats(self, newChat: list):
		self.__chat = self.__chat.append(newChat, ignore_index=True)
		element = "{\"admins\":" + self.__botAdmins.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + ",\"chat\":" + \
				  self.__chat.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + "}"
		"""
			Saving the database
		"""
		with open("{}database.json".format(self.__path), "w") as users:
			users.write(element)

	@chats.deleter
	def chats(self):
		self.__chat = pandas.DataFrame(data=dict(), columns=list(["id", "type", "is_verified", "is_restricted",
																  "is_scam", "is_support", "title", "username",
																  "first_name", "last_name", "invite_link"]))
		element = "{\"admins\":" + self.__botAdmins.to_json(orient="records").replace("\":", "\": ").replace(",\"", ", \"") + ",\"chat\": []}"
		"""
			Saving the database
		"""
		with open("{}database.json".format(self.__path), "w") as users:
			users.write(element)

	@property
	def databasePath(self) -> str:
		return self.__path

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
		with open("{}database.json".format(self.__path), "r") as users:
			files = json.load(users)
			"""
		Setting the database
		"""
			self.__botAdmins = pandas.DataFrame(data=files["admins"], columns=list(["id", "is_self", "is_contact",
																					"is_mutual_contact", "is_deleted",
																					"is_bot", "is_verified", "is_restricted",
																					"is_scam", "is_support", "first_name",
																					"last_name", "username", "language_code",
																					"phone_number"]))
			self.__chat = pandas.DataFrame(data=files["chat"], columns=list(["id", "type", "is_verified", "is_restricted",
																			 "is_scam", "is_support", "title", "username",
																			 "first_name", "last_name", "invite_link"]))
		"""
			Setting the parameters
		"""
		rows = self.__botAdmins.shape[0]
		rows = range(rows)
		for i in rows:
			if self.__botAdmins.at[i, "username"] == "CREATOR USERNAME":
				self.__creator = int(self.__botAdmins.at[i, "id"])

	@property
	def log(self) -> int:
		return self.__botLog

	@property
	def lootBot(self) -> int:
		return self.__lootBot

	@property
	def lootBotPlus(self) -> int:
		return self.__lootBotPlus

	@property
	def mom(self) -> int:
		return self.__mom

	@staticmethod
	def now() -> str:
		timer = time.localtime()
		return "{}:{}:{} of {}-{}-{}".format(timer.tm_hour, timer.tm_min, timer.tm_sec,
											 timer.tm_mday, timer.tm_mon, timer.tm_year)

	@property
	def phoneNumber(self) -> str:
		return self.__phoneNumber

	@property
	def username(self) -> str:
		return self.__botUsername
