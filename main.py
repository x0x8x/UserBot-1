from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import logging as logger
import os
import pymysql
from pyrogram import Client, Emoji, Filters, Message
from pyrogram.api import functions
from pyrogram.errors import FloodWait
import random
import re
from res.configurations import Configurations
import subprocess

def stopFilterCommute(self):
	self.flag = not self.flag


adminsIdList = list()
chatIdList = list()

configurations_map = {
	"commands": "commands",
	"database": "database",
	"logger": "logger"
}

config = Configurations("config/config.json", configurations_map)
await config.parse()
config.set("app_hash", os.environ.pop("app_hash", None))
config.set("app_id", os.environ.pop("app_id", None))
config.set("phoneNumber", os.environ.pop("phoneNumber", None))
config.set("userbot_username", os.environ.pop("userbot_username", None))

connection = pymysql.connect(
	host=config.get("database")["host"],
	user=config.get("database")["username"],
	password=config.get("database")["password"],
	database=config.get("bot_username"),
	port=config.get("database")["port"],
	charset="utf8",
	cursorclass=pymysql.cursors.DictCursor,
	autocommit=False)

flags = {
	"gnome": ""
}

logger.basicConfig(
	filename=config.get("logger")["path"],
	datefmt="%d/%m/%Y %H:%M:%S",
	format=config.get("logger")["format"],
	level=config.get("logger").pop("level", "INFO"))

minute = 60
scheduler = AsyncIOScheduler()
stopFilter = Filters.create(lambda self, _: self.flag, flag=True, commute=stopFilterCommute)

with connection.cursor() as cursor:
	logger.info("Initializing the Admins ...")
	cursor.execute("SELECT `id` FROM `Admins` WHERE `username`=%(user)s", {"user": "username"})
	config.set("creator", cursor.fetchone()["id"])

	logger.info("Admins initializated\nSetting the admins list ...")
	cursor.execute("SELECT `id` FROM `Admins`")
	for i in cursor.fetchall():
		adminsIdList.append(i["id"])

	logger.info("Admins setted\nSetting the chats list ...")
	cursor.execute("SELECT `id` FROM `Chats`")
	for i in cursor.fetchall():
		chatIdList.append(i["id"])
chatIdList.append("me")

logger.info("Chats initializated\nInitializing the Client ...")
app = Client(session_name=config.get("userbot_username"), api_id=config.get("api_id"), api_hash=config.get("api_hash"), phoneNumber=config.get("phoneNumber"))


async def split_edit_text(message: Message, text: str):
	"""
		A coroutine that edits the text of a message; if text is too long sends more messages.
		:param message: Message to edit
		:param text: Text to insert
		:return: None
	"""
	global config

	await message.edit_text(text[:config.get("message_max_length")])
	if len(text) >= config.get("message_max_length"):
		for i in range(1, len(text), config.get("message_max_length")):
			try:
				await message.reply_text(text[i:i + config.get("message_max_length")], quote=False)
			except FloodWait as e:
				await asyncio.sleep(e.x)


async def split_reply_text(message: Message, text: str):
	"""
		A coroutine that reply to a message; if text is too long sends more messages.
		:param message: Message to reply
		:param text: Text to insert
		:return: None
	"""
	global config

	await message.reply_text(text[:config.get("message_max_length")], quote=False)
	if len(text) >= config.get("message_max_length"):
		for i in range(1, len(text), config.get("message_max_length")):
			try:
				await message.reply_text(text[i:i + config.get("message_max_length")], quote=False)
			except FloodWait as e:
				await asyncio.sleep(e.x)


@app.on_message(Filters.command("add", prefixes=["/", "!", "."]) & (Filters.user(config.get("creator")) | Filters.channel) & stopFilter)
async def add_to_the_database(client: Client, message: Message):
	# /add
	global adminsIdList, chatIdList, config, stopFilter

	await stopFilter.commute()
	# Checking if the message arrive from a channel and, if not, checking if the user that runs the command is allowed
	if message.from_user is not None and message.from_user.id != config.get("creator"):
		await stopFilter.commute()
		return

	lists = chatIdList
	text = "The chat {} is already present in the list of allowed chat.".format(chat.title)

	# Checking if the data are of a chat or of a user
	if message.reply_to_message is not None:
		chat = await client.get_users(message.reply_to_message.from_user.id)
		chat = chat.__dict__
		lists = adminsIdList
		text = "The user @{} is already an admin.".format(chat["username"])
	else:
		chat = await client.get_chat(message.chat.id)
		chat = chat.__dict__

		# Deleting the message
		await message.delete(revoke=True)

	# Checking if the chat/user is in the list
	if chat["id"] in lists:
		await stopFilter.commute()
		logger.info(text)
		return

	# Adding the chat/user to the database
	lists.append(chat["id"])

	# Removing inutil informations
	chat.pop("_client", None)
	chat.pop("_", None)
	chat.pop("photo", None)
	chat.pop("description", None)
	chat.pop("pinned_message", None)
	chat.pop("sticker_set_name", None)
	chat.pop("can_set_sticker_set", None)
	chat.pop("members_count", None)
	chat.pop("restrictions", None)
	chat.pop("permissions", None)
	chat.pop("distance", None)
	chat.pop("status", None)
	chat.pop("last_online_date", None)
	chat.pop("next_offline_date", None)
	chat.pop("dc_id", None)
	chat.pop("is_self", None)
	chat.pop("is_contact", None)
	chat.pop("is_mutual_contact", None)
	chat.pop("is_deleted", None)
	chat.pop("is_verified", None)
	chat.pop("is_restricted", None)
	chat.pop("is_scam", None)
	chat.pop("is_support", None)

	with connection.cursor() as cursor:
		if config.get("creator") in lists:
			cursor.execute("INSERT INTO `Admins` (`id`, `is_bot`, `first_name`, `last_name`, `username`, `language_code`, `phone_number`) VALUES (%(id)s, %(is_bot)s, %(first_name)s, %(last_name)s, %(username)s, %(language_code)s, %(phone_number)s)", chat)
			text = "I added {}{} to the list of allowed user.".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "", "{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
		else:
			cursor.execute("INSERT INTO `Chats` (`id`, `type`, `title`, `username`, `first_name`, `last_name`, `invite_link`) VALUES (%(id)s, %(type)s, %(title)s, %(username)s, %(first_name)s, %(last_name)s, %(invite_link)s)", chat)
			text = "I added {} to the list of allowed chat.".format(chat["title"])
		connection.commit()

	await stopFilter.commute()
	logger.info(text)

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.service)
async def automaticRemovalStatus(client: Client, message: Message):
	await message.delete(revoke=True)
	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("check", prefixes=["/", "!", "."]) & Filters.user(config.get("creator")) & Filters.chat(chatIdList) & stopFilter)
async def checkDatabase(client: Client, _):
	# /check
	global adminsIdList, connection, chatIdList

	await message.delete(revoke=True)

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

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("clear", prefixes=["/", "!", "."]) & Filters.user(config.get("creator")) & Filters.chat(chatIdList))
async def clearSavedMessage(client: Client, message: Message):
	# /clear
	maxLength = 200
	message.command.pop(0)

	await message.delete(revoke=True)

	to_delete = await client.iter_history("me")
	to_delete = list(to_delete)
	if len(to_delete) == 0 or to_delete is None:
		return
	to_delete = list(map(lambda n: n.message_id, to_delete))

	for i in range(0, len(to_delete), maxLength):
		await client.delete_messages(chat_id, to_delete[i:i + maxLength], revoke=True)

	logger.info("I have cleared the Telegram\'s Saved Messages chat.")

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("evaluate", prefixes=["/", "!", "."]))
async def evaluation(client: Client, message: Message):
	# /evaluate
	message.command.pop(0)

	command = " ".join(message.command)

	result = eval(command)
	text = "<b>Espression:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)

	await split_edit_text(message, text)

	logger.info("I have evaluated the command <code>{}</code>.".format(command))

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("exec", prefixes=["/", "!", "."]))
async def execution(client: Client, message: Message):
	# /exec
	message.command.pop(0)

	command = " ".join(message.command)

	if command == "clear":
		os.system(command)

	result = subprocess.check_output(command, shell=True)
	result = result.decode("utf-8")
	result = result.replace("\n", "</code>\n\t<code>")
	text = "<b>Command:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)

	await split_edit_text(message, text)

	logger.info("I have executed the command <code>{}</code>.".format(command))

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("groups", prefixes=["/", "!", "."]) & Filters.user(config.get("creator")) & Filters.chat(chatIdList) & stopFilter)
async def groups(client: Client, message: Message):
	# /groups
	global connection

	groups = list()

	with connection.cursor() as cursor:
		cursor.execute("SELECT `title`, `username`, `invite_link` FROM `Chats`")
		i = list(filter(lambda n: n["username"] is not None, cursor.fetchall()))

		groups = list(map(lambda n: "<a href=\"https://t.me/{}\">{}</a>".format(n["username"], n["title"]), i))

		i = list(filter(lambda n: n["invite_link"] is not None and n["username"] is None, cursor.fetchall()))

		groups.extend(list(map(lambda n: "<a href=\"{}\">{}</a>".format(n["invite_link"], n["title"]), i)))

	groups = sorted(groups, key=lambda n: n[n.index(">") + 1:])
	text = "Your groups are:\n\t{}".format("\n\t".join(groups))

	await split_edit_text(message, text)

	logger.info("I sent the groups list.")

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("help", prefixes=["/", "!", "."]) & Filters.chat(chatIdList))
async def help(_, message: Message):
	# /help
	global config

	prefixes = [
		"/",
		"!",
		"."
	]
	commands = config.get("commands")

	# Filter the commands list in base at their domain
	if message.from_user.id not in adminsIdList:
		commands = list(filter(lambda n: n["domain"] != "admin", commands))
	if message.from_user.id != config.get("creator"):
		commands = list(filter(lambda n: n["domain"] != "creator", commands))

	await split_reply_text(message, "In this section you will find the list of the command of the UserBot.\n\t{}\nThe prefixes for use this command are:\n\t\t<code>{}</code>".format("\n\t".join(list(map(lambda n: "<code>/{} {}</code> - {}".format(n["name"], n["parameters"], n["description"])), commands)), prefixes))

	logger.info("I sent the help.")

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("init", prefixes="/") & Filters.user(adminsIdList) & Filters.private)
async def initializing(client: Client, _):
	# /init
	global config

	max_length = await client.send(functions.help.GetConfig())
	config.set("message_max_length", max_length.message_length_max)

	await client.send(functions.account.UpdateStatus(offline=True))


@app.on_message(Filters.command("remove", prefixes="/") & (Filters.user(config.get("creator")) | Filters.channel) & stopFilter)
async def remove_from_the_database(_, message: Message):
	# /remove
	global adminsIdList, chatIdList, config, stopFilter

	await stopFilter.commute()

	# Checking if the message arrive from a channel and, if not, checking if the user that runs the command is allowed
	if message.from_user is not None and message.from_user.id != config.get("creator"):
		await stopFilter.commute()
		return

	lists = chatIdList
	title = message.chat.title
	text = "The chat {} hasn\'t been removed from the list of allowed chat.".format(title)

	# Checking if the data are of a chat or of a user
	if message.reply_to_message is not None:
		ids = message.reply_to_message.from_user.id
		lists = adminsIdList
		text = "The user @{} hasn\'t been removed from the admins list.".format(message.reply_to_message.from_user.username)
	else:
		ids = message.chat.id

		# Deleting the message
		await message.delete(revoke=True)

	# Checking if the chat/user is in the list
	if ids not in lists:
		await stopFilter.commute()
		logger.info(text)
		return

	# Removing the chat/user from the database
	lists.remove(ids)

	with connection.cursor() as cursor:
		if config.get("creator") in lists:
			cursor.execute("DELETE FROM `Admins` WHERE `id`=%(id)s", {"id": ids})
			text = "The user @{} has been removed from the admins list.".format(message.reply_to_message.from_user.username)
		else:
			cursor.execute("DELETE FROM `Chats` WHERE `id`=%(id)s", {"id": ids})
			text = "The chat {} has been removed from the list of allowed chat.".format(title)
		connection.commit()

	await stopFilter.commute()
	logger.info(text)


@app.on_message(Filters.command("update", prefixes="/") & Filters.user(config.get("creator")) & Filters.private & stopFilter)
async def updateDatabase(client: Client, message: Message = None):
	# /update
	global adminsIdList, chatIdList, connection, config, stopFilter

	await stopFilter.commute()

	# Checking if the updating was programmed or not
	if message is not None:
		await message.delete(revoke=True)

	# Updating the admin's database
	adminsIdList.remove(config.get("creator"))
	chats = await client.get_users(adminsIdList)
	adminsIdList.append(config.get("creator"))
	await chats.append(client.get_me())
	chats = list(map(lambda n: n.__dict__, chats))

	with connection.cursor() as cursor:
		for i in chats:
			# Removing inutil informations
			i.pop("_client", None)
			i.pop("_", None)
			i.pop("photo", None)
			i.pop("restrictions", None)
			i.pop("status", None)
			i.pop("last_online_date", None)
			i.pop("next_offline_date", None)
			i.pop("dc_id", None)
			i.pop("is_self", None)
			i.pop("is_contact", None)
			i.pop("is_mutual_contact", None)
			i.pop("is_deleted", None)
			i.pop("is_verified", None)
			i.pop("is_restricted", None)
			i.pop("is_scam", None)
			i.pop("is_support", None)
			# Updating the admins' database
			cursor.execute("UPDATE `Admins` SET `is_bot`=%(is_bot)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `username`=%(username)s, `language_code`=%(language_code)s, `phone_number`=%(phone_number)s WHERE `id`=%(id)s", i)
		connection.commit()

	# Updating the chats' database
	chats = list()
	for i in chatIdList:
		try:
			await chats.append(client.get_chat(i).__dict__)
		except FloodWait as e:
			await asyncio.sleep(e.x)

	with connection.cursor() as cursor:
		for i in chats:
			# Removing inutil informations
			i.pop("_client", None)
			i.pop("_", None)
			i.pop("photo", None)
			i.pop("description", None)
			i.pop("pinned_message", None)
			i.pop("sticker_set_name", None)
			i.pop("can_set_sticker_set", None)
			i.pop("members_count", None)
			i.pop("restrictions", None)
			i.pop("permissions", None)
			i.pop("distance", None)
			i.pop("is_verified", None)
			i.pop("is_restricted", None)
			i.pop("is_scam", None)
			i.pop("is_support", None)
			# Updating the chats' database
			cursor.execute("UPDATE `Chats` SET `type`=%(type)s, `title`=%(title)s, `username`=%(username)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `invite_link`=%(invite_link)s WHERE `id`=%(id)s", i)
		connection.commit()

	await stopFilter.commute()
	logger.info("I have updated the database.")

	await client.send(functions.account.UpdateStatus(offline=True))


def unknownFilter():
	global config

	def func(flt, message: Message):
		text = message.text
		if text:
			message.matches = list(flt.p.finditer(text)) or None
			if bool(message.matches) is False and (text.startswith(".") is True or text.startswith("!") is True or text.startswith("/") is True) and len(text) > 1 and text != "...":
				return True
		return False

	commands = list(map(lambda n: n["name"], config.get("commands")))

	return Filters.create(func, "UnknownFilter", p=re.compile("/{}".format("|/".join(commands)), 0))


@app.on_message(unknownFilter() & Filters.private)
async def unknown(_, message: Message):
	await message.reply_text("This command isn\'t supported.")
	logger.info("I managed an unsupported command.")


logger.info("Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")

logger.info("Set the markup syntax\nSetting the Job Queue ...")
scheduler.add_job(updateDatabase, IntervalTrigger(days=1, timezone="Europe/Rome"), kwargs={"client": app})

logger.info("Set the Job Queue\nStarted serving ...")
scheduler.start()
app.run()
connection.close()
