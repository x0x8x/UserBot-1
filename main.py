import os
import logging as logger
import random
import re
import subprocess
import time
from datetime import date

import schedule
import pymysql
from pyrogram import Client, Filters, Message
from pyrogram.api.functions.account import UpdateStatus
from pyrogram.api.functions.help import GetConfig
from pyrogram.errors import FloodWait

from modules import Constants

def stopFilterCommute(self):
	self.flag = not self.flag


adminsIdList = list()
chatIdList = list()
commands = list(["check",
				 "evaluate",
				 "exec",
				 "help",
				 "retrieve",
				 "update"
				])
constants = Constants.Constants()
connection = pymysql.connect(host="localhost",
                             user="USER",
                             password="PASSWORD",
                             database=constants.username,
							 port=3306,
                             charset="utf8",
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=False)
logger.basicConfig(filename="{}{}.log".format(constants.databasePath, constants.username), datefmt="%d/%m/%Y %H:%M:%S", format="At %(asctime)s was logged the event:\t%(levelname)s - %(message)s", level=logger.INFO)
scheduler = schedule.default_scheduler
stopFilter = Filters.create(lambda self, _: self.flag, flag=True, commute=stopFilterCommute)
with connection.cursor() as cursor:
	"""
		Initializing the Admins ...
	"""
	logger.info("Initializing the Admins ...")
	cursor.execute("SELECT `id` FROM `Admins` WHERE `username`=%(user)s", dict({"user": "USER"}))
	constants.creator = cursor.fetchone()["id"]
	"""
		Admins initializated
		Setting the admins list ...
	"""
	logger.info("Admins initializated\nSetting the admins list ...")
	cursor.execute("SELECT `id` FROM `Admins`")
	for i in cursor.fetchall():
		adminsIdList.append(i["id"])
	"""
		Admins setted
		Setting the chats list ...
	"""
	logger.info("Admins setted\nSetting the chats list ...")
	cursor.execute("SELECT `id` FROM `Chats`")
	for i in cursor.fetchall():
		chatIdList.append(i["id"])
chatIdList.append("me")
"""
	Chats initializated
	Initializing the Client ...
"""
logger.info("Chats initializated\nInitializing the Client ...")
app = Client(session_name=constants.username, api_id=constants.id, api_hash=constants.hash, phone_number=constants.phoneNumber)


@app.on_message(Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
	"""
		Removing the status message
	"""
	message.delete(revoke=True)
	client.send(UpdateStatus(offline=True))


@app.on_message(
	Filters.command("check", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
		chatIdList) & stopFilter)
def checkDatabase(client: Client, message: Message):
	global adminsIdList, connection, chatIdList

	"""
		Removing the message
	"""
	message.delete(revoke=True)
	"""
		Sending the output
	"""
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Admins`")
		print("{}".format(cursor.fetchall()))
	print("\n{}\n".format(adminsIdList))
	print("{}\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), adminsIdList))))
	with connection.cursor() as cursor:
		cursor.execute("SELECT * FROM `Chats`")
		print("{}".format(cursor.fetchall()))
	print("\n{}\n".format(chatIdList))
	print("{}\n".format(list(map(lambda n: "\t{} - {}\n".format(n, type(n)), chatIdList))))
	print("\n\n")
	logger.info("I have checked the admin and the chat list.")
	client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("evaluate", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def evaluation(client: Client, message: Message):
	"""
		Extract the command
	"""
	command = message.command
	command.pop(0)
	if len(command) == 1:
		command = command.pop(0)
	else:
		command = " ".join(command)
	result = eval(command)
	"""
		Sending the output
	"""
	text = "<b>Espression:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	maxLength = client.send(GetConfig()).message_length_max
	message.edit_text(text[:maxLength])
	if len(text) >= maxLength:
		for k in range(1, len(text), maxLength):
			time.sleep(random.randint(minute / 6, minute / 2))
			message.reply_text(text[k:k + maxLength], quote=False)
	logger.info("I have evaluated the command <code>{}</code>.".format(command))
	client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("exec", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def execution(client: Client, message: Message):
	"""
		Extract the command
	"""
	command = message.command
	command.pop(0)
	if len(command) == 1:
		command = command.pop(0)
	else:
		command = " ".join(command)
	"""
		Execution of the command
	"""
	if command == "clear":
		os.system(command)
	result = subprocess.check_output(command, shell=True)
	result = result.decode("utf-8")
	if "\n" in result:
		result = result.replace("\n", "</code>\n\t<code>")
	"""
		Sending the output
	"""
	text = "<b>Command:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	maxLength = client.send(GetConfig()).message_length_max
	message.edit_text(text[:maxLength])
	if len(text) >= maxLength:
		for k in range(1, len(text), maxLength):
			time.sleep(random.randint(minute / 6, minute / 2))
			message.reply_text(text[k:k + maxLength], quote=False)
	logger.info("I have executed the command <code>{}</code>.".format(command))
	client.send(UpdateStatus(offline=True))


@app.on_message(
	Filters.command("help", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
		chatIdList))
def help(client: Client, message: Message):
	global commands

	prefixes = list(["/",
					 "!",
					 "."
					])
	"""
		Sending the output
	"""
	message.edit_text("The commands are:\n\t\t<code>{}</code>\nThe prefixes for use this command are:\n\t\t<code>{}</code>".format(
		"<code>\n\t\t</code>".join(commands), "<code>\n\t\t</code>".join(prefixes)))
	logger.info("I sent the help.")
	client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & (Filters.user(constants.creator) | Filters.channel) & stopFilter)
def retrieveChatId(client: Client, message: Message):
	global adminsIdList, constants, chatIdList

	if message.from_user is not None and message.from_user.id != constants.creator:
		return
	chat = message.chat
	lists = chatIdList
	text = "The chat {} is already present in the list of allowed chat.".format(chat.title)
	chatType = chat.type
	if chatType == "private" or chatType == "bot":
		chatType = None
		chat = client.get_users(chat.id)
		lists = adminsIdList
		text = "The user {}".format("{} ".format(chat.first_name) if chat.first_name is not None else "")
		text += "{}is already present in the list of allowed chat.".format("{} ".format(chat.last_name) if chat.last_name is not None else "")
	else:
		chat = client.get_chat(chat.id)
	"""
		Removing the message
	"""
	message.delete(revoke=True)
	if chat.id not in lists:
		if chatType is not None and chat.id == constants.creator:
			return
		"""
			Adding the chat to the database
		"""
		chatDict = chat.__dict__
		try:
			del chatDict["_client"]
		except KeyError:
			pass
		try:
			del chatDict["_"]
		except KeyError:
			pass
		try:
			del chatDict["photo"]
		except KeyError:
			pass
		try:
			del chatDict["description"]
		except KeyError:
			pass
		try:
			del chatDict["pinned_message"]
		except KeyError:
			pass
		try:
			del chatDict["sticker_set_name"]
		except KeyError:
			pass
		try:
			del chatDict["can_set_sticker_set"]
		except KeyError:
			pass
		try:
			del chatDict["members_count"]
		except KeyError:
			pass
		try:
			del chatDict["restrictions"]
		except KeyError:
			pass
		try:
			del chatDict["permissions"]
		except KeyError:
			pass
		try:
			del chatDict["distance"]
		except KeyError:
			pass
		try:
			del chatDict["status"]
		except KeyError:
			pass
		try:
			del chatDict["last_online_date"]
		except KeyError:
			pass
		try:
			del chatDict["next_offline_date"]
		except KeyError:
			pass
		try:
			del chatDict["dc_id"]
		except KeyError:
			pass
		with connection.cursor() as cursor:
			if chatType is not None:
				cursor.execute("INSERT INTO `Chats` (`id`, `type`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `title`, `username`, `first_name`, `last_name`, `invite_link`) VALUES (%(id)s, %(type)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(title)s, %(username)s, %(first_name)s, %(last_name)s, %(invite_link)s)", chatDict)
				text = "I added {} to the list of allowed chat.".format(chat.title)
			else:
				cursor.execute("INSERT INTO `Admins` (`id`, `is_self` ,`is_contact`, `is_mutual_contact`, `is_deleted`, `is_bot`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `first_name`, `last_name`, `username`, `language_code`, `phone_number`, `role`) VALUES (%(id)s, %(is_self)s, %(is_contact)s, %(is_mutual_contact)s, %(is_deleted)s, %(is_bot)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(first_name)s, %(last_name)s, %(username)s, %(language_code)s, %(phone_number)s)", chatDict)
				text = "I added {}".format("{} ".format(chat.first_name) if chat.first_name is not None else "")
				text += "{}to the list of allowed chat.".format("{} ".format(chat.last_name) if chat.last_name is not None else "")
			connection.commit()
	logger.info(text)
	client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("scheduling", prefixes=list(["/", "!", "."])) & Filters.user(adminsIdList))
def scheduling(client: Client, message: Message):
	global scheduler

	logger.info("Setted the Job Queue")
	scheduler.every().day.do(updateDatabase, client=client).run()
	while True:
		scheduler.run_pending()


@app.on_message(Filters.command("update", prefixes=list(["/", "!", "."])) & Filters.user(adminsIdList) & stopFilter)
def updateDatabase(client: Client, message: Message = None):
	global adminsIdList, connection, chatIdList, stopFilter

	stopFilter.commute()
	"""
		Updateing the admins database
	"""
	chats = client.get_users(adminsIdList)
	chats.append(client.get_me())
	chats = list(map(lambda n: n.__dict__, chats))
	with connection.cursor() as cursor:
		for i in chats:
			try:
				del i["_client"]
			except KeyError:
				pass
			try:
				del i["_"]
			except KeyError:
				pass
			try:
				del i["photo"]
			except KeyError:
				pass
			try:
				del i["description"]
			except KeyError:
				pass
			try:
				del i["pinned_message"]
			except KeyError:
				pass
			try:
				del i["sticker_set_name"]
			except KeyError:
				pass
			try:
				del i["can_set_sticker_set"]
			except KeyError:
				pass
			try:
				del i["members_count"]
			except KeyError:
				pass
			try:
				del i["restrictions"]
			except KeyError:
				pass
			try:
				del i["permissions"]
			except KeyError:
				pass
			try:
				del i["distance"]
			except KeyError:
				pass
			try:
				del i["status"]
			except KeyError:
				pass
			try:
				del i["last_online_date"]
			except KeyError:
				pass
			try:
				del i["next_offline_date"]
			except KeyError:
				pass
			try:
				del i["dc_id"]
			except KeyError:
				pass
			cursor.execute("UPDATE `Admins` SET `is_self`=%(is_self)s, `is_contact`=%(is_contact)s, `is_mutual_contact`=%(is_mutual_contact)s, `is_deleted`=%(is_deleted)s, `is_bot`=%(is_bot)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `username`=%(username)s, `language_code`=%(language_code)s, `phone_number`=%(phone_number)s WHERE `id`=%(id)s", i)
		connection.commit()
	"""
		Updateing the chats database
	"""
	chats = list()
	chatIdList.remove("me")
	for i in chatIdList:
		try:
			chats.append(client.get_chat(i).__dict__)
		except FloodWait as e:
			time.sleep(e.x)
	chatIdList.append("me")
	with connection.cursor() as cursor:
		for i in chats:
			try:
				del i["_client"]
			except KeyError:
				pass
			try:
				del i["_"]
			except KeyError:
				pass
			try:
				del i["photo"]
			except KeyError:
				pass
			try:
				del i["description"]
			except KeyError:
				pass
			try:
				del i["pinned_message"]
			except KeyError:
				pass
			try:
				del i["sticker_set_name"]
			except KeyError:
				pass
			try:
				del i["can_set_sticker_set"]
			except KeyError:
				pass
			try:
				del i["members_count"]
			except KeyError:
				pass
			try:
				del i["restrictions"]
			except KeyError:
				pass
			try:
				del i["permissions"]
			except KeyError:
				pass
			try:
				del i["distance"]
			except KeyError:
				pass
			try:
				del i["status"]
			except KeyError:
				pass
			try:
				del i["last_online_date"]
			except KeyError:
				pass
			try:
				del i["next_offline_date"]
			except KeyError:
				pass
			try:
				del i["dc_id"]
			except KeyError:
				pass
			cursor.execute("UPDATE `Chats` SET `type`=%(type)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `title`=%(title)s, `username`=%(username)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `invite_link`=%(invite_link)s WHERE `id`=%(id)s", i)
		connection.commit()
	stopFilter.commute()
	"""
		Removing the message
	"""
	if message is not None and len(message.command) != 0:
		message.delete(revoke=True)
	logger.info("I have updated the database.")
	client.send(UpdateStatus(offline=True))


def unknownFilter():
	global commands

	def func(flt, message: Message):
		text = message.text or message.caption
		if text:
			message.matches = list(flt.p.finditer(text)) or None
			if bool(message.matches) is False and (text.startswith(".") is True or text.startswith("!") is True or text.startswith("/") is True) and \
					len(text) > 1 and text != "...":
				return True
		return False
	return Filters.create(func, "UnknownFilter", p=re.compile("[/!\.]{}".format("|[/!\.]".join(commands)), 0))


@app.on_message(unknownFilter() & Filters.user(adminsIdList) & Filters.chat(chatIdList))
def unknown(client: Client, message: Message):
	if message.chat.type == "bot":
		return
	message.edit_text("This command isn\'t supported.")
	logger.info("I managed an unsupported command.")
	client.send(UpdateStatus(offline=True))


logger.info("Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
logger.info("Setted the markup syntax\nStarted serving ...")
app.run()
connection.close()
