import asyncio
import logging as logger
from modules import Constants
import os
import pymysql
from pyrogram import Client, Emoji, Filters, Message
from pyrogram.api.functions.account import UpdateStatus
from pyrogram.api.functions.help import GetConfig
from pyrogram.errors import FloodWait
import re
import schedule
import subprocess
import time

def stopFilterCommute(self):
	self.flag = not self.flag


adminsIdList = list()
chatIdList = list()
commands = list(["check", "clear", "evaluate", "exec", "help", "retrieve", "scheduling", "update"])
connection = pymysql.connect(host="localhost", user="myUser", password="myPassword", database=constants.username, port=3306, charset="utf8", cursorclass=pymysql.cursors.DictCursor, autocommit=False)
constants = Constants.Constants()
logger.basicConfig(filename="{}{}.log".format(constants.databasePath, constants.username), datefmt="%d/%m/%Y %H:%M:%S", format="At %(asctime)s was logged the event:\t%(levelname)s - %(message)s", level=logger.INFO)
messageMaxLength = 0
minute = 60
scheduler = schedule.default_scheduler
stopFilter = Filters.create(lambda self, _: self.flag, flag=True, commute=stopFilterCommute)
with connection.cursor() as cursor:
	logger.info("Initializing the Admins ...")
	cursor.execute("SELECT `id` FROM `Admins` WHERE `username`=%(user)s", dict({"user": "myUser"}))
	constants.creator = cursor.fetchone()["id"]
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
app = Client(session_name=constants.username, api_id=constants.id, api_hash=constants.hash, phone_number=constants.phoneNumber)


@app.on_message(Filters.service)
async def automaticRemovalStatus(client: Client, message: Message):
	await message.delete(revoke=True)
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("check", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(chatIdList) & stopFilter)
async def checkDatabase(client: Client, _):
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
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("clear", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(chatIdList))
async def clearSavedMessage(client: Client, message: Message):
	global constants

	maxLength = 200
	message.command.pop(0)
	await message.delete(revoke=True)
	parameters = " ".join(message.command)
	to_delete = await client.iter_history("me")
	to_delete = list(to_delete)
	if len(to_delete) == 0 or to_delete is None:
		return
	to_delete = list(map(lambda n: n.message_id, to_delete))
	for i in range(0, len(to_delete), maxLength):
		await client.delete_messages(chat_id, to_delete[i:i + maxLength], revoke=True)
	logger.info("I have cleared the Telegram\'s Saved Messages chat.")
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("evaluate", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
async def evaluation(client: Client, message: Message):
	global messageMaxLength

	message.command.pop(0)
	command = " ".join(message.command)
	result = eval(command)
	text = "<b>Espression:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	await message.edit_text(text[:messageMaxLength])
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I have evaluated the command <code>{}</code>.".format(command))
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("exec", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
async def execution(client: Client, message: Message):
	global messageMaxLength

	message.command.pop(0)
	command = " ".join(message.command)
	if command == "clear":
		os.system(command)
	result = subprocess.check_output(command, shell=True)
	result = result.decode("utf-8")
	result = result.replace("\n", "</code>\n\t<code>")
	text = "<b>Command:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
	await message.edit_text(text[:messageMaxLength])
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I have executed the command <code>{}</code>.".format(command))
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("help", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(chatIdList))
async def help(client: Client, message: Message):
	global commands

	prefixes = list(["/", "!", "."])
	text = "The commands are:\n\t\t<code>{}</code>\nThe prefixes for use this command are:\n\t\t<code>{}</code>".format("<code>\n\t\t</code>".join(commands), "<code>, </code>".join(prefixes))
	await message.edit_text(text[:messageMaxLength], disable_web_page_preview=True)
	if len(text) >= messageMaxLength:
		for i in range(1, len(text), messageMaxLength):
			try:
				await message.reply_text(text[i:i + messageMaxLength], quote=False, disable_web_page_preview=True)
			except FloodWait as e:
				time.sleep(e.x)
	logger.info("I sent the help.")
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & (Filters.user(constants.creator) | Filters.channel) & stopFilter)
async def retrieveChatId(client: Client, message: Message):
	global adminsIdList, chatIdList, connection, stopFilter

	await stopFilter.commute()
	if message.from_user is not None and message.from_user.id != constants.creator:
		await stopFilter.commute()
		return
	lists = chatIdList
	text = "The chat {} is already present in the list of allowed chat.".format(chat.title)
	if message.chat.type == "private" or message.chat.type == "bot":
		chat = await client.get_users(message.chat.id)
		chat = chat.__dict__
		lists = adminsIdList
		text = "The user {}".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "")
		text += "{} is already present in the list of allowed user.".format("{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
	else:
		chat = await client.get_chat(message.chat.id)
		chat = chat.__dict__
	await message.delete(revoke=True)
	if chat["id"] == constants.creator or chat["id"] in lists:
		await stopFilter.commute()
		return
	lists.append(chat["id"])
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
	with connection.cursor() as cursor:
		if message.chat.type == "private" or message.chat.type == "bot":
			cursor.execute("INSERT INTO `Admins` (`id`, `is_self` ,`is_contact`, `is_mutual_contact`, `is_deleted`, `is_bot`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `first_name`, `last_name`, `username`, `language_code`, `phone_number`, `role`) VALUES (%(id)s, %(is_self)s, %(is_contact)s, %(is_mutual_contact)s, %(is_deleted)s, %(is_bot)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(first_name)s, %(last_name)s, %(username)s, %(language_code)s, %(phone_number)s)", chat)
			text = "I added {}".format("{} ".format(chat["first_name"]) if chat["first_name"] is not None else "")
			text += "{} to the list of allowed user.".format("{} ".format(chat["last_name"]) if chat["last_name"] is not None else "")
		else:
			cursor.execute("INSERT INTO `Chats` (`id`, `type`, `is_verified`, `is_restricted`, `is_scam`, `is_support`, `title`, `username`, `first_name`, `last_name`, `invite_link`) VALUES (%(id)s, %(type)s, %(is_verified)s, %(is_restricted)s, %(is_scam)s, %(is_support)s, %(title)s, %(username)s, %(first_name)s, %(last_name)s, %(invite_link)s)", chat)
			text = "I added {} to the list of allowed chat.".format(chat["title"])
		connection.commit()
	await stopFilter.commute()
	logger.info(text)
	await client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("scheduling", prefixes=list(["/", "!", "."])) & Filters.user(adminsIdList))
def scheduling(client: Client, _):
	global messageMaxLength, scheduler

	logger.info("Setted the Job Queue")
	messageMaxLength = await client.send(GetConfig()).message_length_max
	scheduler.every().day.do(updateDatabase, client=client).run()
	await client.send(UpdateStatus(offline=True))
	while True:
		scheduler.run_pending()
		time.sleep(minute * 60 * 23)


@app.on_message(Filters.command("update", prefixes=list(["/", "!", "."])) & Filters.user(adminsIdList) & stopFilter)
async def updateDatabase(client: Client, message: Message = None):
	global adminsIdList, chatIdList, connection, constants, stopFilter

	await stopFilter.commute()
	if message is not None:
		await message.delete(revoke=True)
	adminsIdList.remove(constants.creator)
	chats = await client.get_users(adminsIdList)
	adminsIdList.append(constants.creator)
	await chats.append(client.get_me())
	chats = list(map(lambda n: n.__dict__, chats))
	with connection.cursor() as cursor:
		for i in chats:
			i.pop("_client", None)
			i.pop("_", None)
			i.pop("photo", None)
			i.pop("restrictions", None)
			i.pop("status", None)
			i.pop("last_online_date", None)
			i.pop("next_offline_date", None)
			i.pop("dc_id", None)
			cursor.execute("UPDATE `Admins` SET `is_self`=%(is_self)s, `is_contact`=%(is_contact)s, `is_mutual_contact`=%(is_mutual_contact)s, `is_deleted`=%(is_deleted)s, `is_bot`=%(is_bot)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `username`=%(username)s, `language_code`=%(language_code)s, `phone_number`=%(phone_number)s WHERE `id`=%(id)s", i)
		connection.commit()
	chats = list()
	chatIdList.remove("me")
	for i in chatIdList:
		try:
			await chats.append(client.get_chat(i).__dict__)
		except FloodWait as e:
			time.sleep(e.x)
	chatIdList.append("me")
	with connection.cursor() as cursor:
		for i in chats:
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
			cursor.execute("UPDATE `Chats` SET `type`=%(type)s, `is_verified`=%(is_verified)s, `is_restricted`=%(is_restricted)s, `is_scam`=%(is_scam)s, `is_support`=%(is_support)s, `title`=%(title)s, `username`=%(username)s, `first_name`=%(first_name)s, `last_name`=%(last_name)s, `invite_link`=%(invite_link)s WHERE `id`=%(id)s", i)
		connection.commit()
	await stopFilter.commute()
	logger.info("I have updated the database.")
	await client.send(UpdateStatus(offline=True))


def unknownFilter():
	global commands

	def func(flt, message: Message):
		text = message.text or message.caption
		if text:
			message.matches = list(flt.p.finditer(text)) or None
			if bool(message.matches) is False and (text.startswith(".") is True or text.startswith("!") is True or text.startswith("/") is True) and len(text) > 1 and text != "...":
				return True
		return False
	return Filters.create(func, "UnknownFilter", p=re.compile("[/!\.]{}".format("|[/!\.]".join(commands)), 0))


@app.on_message(unknownFilter() & Filters.user(adminsIdList) & Filters.chat(chatIdList))
async def unknown(client: Client, message: Message):
	if message.chat.type == "bot":
		return
	await message.edit_text("This command isn\'t supported.")
	logger.info("I managed an unsupported command.")
	await client.send(UpdateStatus(offline=True))


logger.info("Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
logger.info("Setted the markup syntax\nStarted serving ...")
app.run()
connection.close()
