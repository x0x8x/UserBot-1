import os
import re
import subprocess

import schedule
from pyrogram import Client, Filters, Message
from pyrogram.api.functions.account import UpdateStatus
from pyrogram.api.functions.help import GetConfig
from pyrogram.errors import FloodWait

from modules import Constants

commands = list(["check",
				 "evaluate",
				 "exec",
				 "help",
				 "retrieve",
				 "update"
				])
constants = Constants.Constants()
initialLog = list(["Initializing the Admins ...", "Admins initializated\nSetting the admins list ...",
				   "Admins setted\nSetting the chats list ...", "Chats initializated\nInitializing the Client ..."])
scheduler = schedule.default_scheduler
"""
	Initializing the Admins ...
"""
constants.loadCreators()
"""
	Admins initializated
	Setting the admins list ...
"""
adminsIdList = set()
i = constants.admins.to_json(orient="columns")
i = i[len("{\"id\":{"):i.index("}")]
i = i.split(",")
i = list(map(lambda n: n.split(":"), i))
i = list(map(lambda n: dict({n[0]: n[1]}), i))
i = list(map(lambda n: list(n.values()), i))
list(map(lambda n: list(map(lambda m: adminsIdList.add(int(m)), n)), i))
adminsIdList = list(adminsIdList)
"""
	Admins setted
	Setting the chats list ...
"""
chatIdList = set()
i = constants.chats.to_json(orient="columns")
i = i[len("{\"id\":{"):i.index("}")]
i = i.split(",")
i = list(map(lambda n: n.split(":"), i))
i = list(map(lambda n: dict({n[0]: n[1]}), i))
i = list(map(lambda n: list(n.values()), i))
list(map(lambda n: list(map(lambda m: chatIdList.add(int(m)), n)), i))
chatIdList = list(chatIdList)
chatIdList.append("me")
"""
	Chats initializated
	Initializing the Client ...
"""
app = Client("UserBot", constants.id, constants.hash, phone_number=constants.phoneNumber)


@app.on_message(Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
	"""
		Removing the status message
	"""
	message.delete(revoke=True)
	client.send(UpdateStatus(offline=True))


@app.on_message(
	Filters.command("check", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
		chatIdList))
def checkDatabase(client: Client, message: Message):
	global adminsIdList, constants, chatIdList

	"""
		Removing the message
	"""
	message.delete(revoke=True)
	"""
		Sending the output
	"""
	element = constants.admins.to_json(orient="records")
	element = element.replace("\":", "\": ")
	print("{}".format(element))
	print("\n{}\n".format(adminsIdList))
	for j in adminsIdList:
		print("\t{} - {}".format(j, type(j)))
	element = constants.chats.to_json(orient="records")
	element = element.replace("\":", "\": ")
	element = element.replace(",\"", ", \"")
	print("\n{}".format(element))
	print("\n{}\n".format(chatIdList))
	for j in chatIdList:
		print("\t{} - {}".format(j, type(j)))
	print("\n\n")
	log(client, "I have checked the admin and the chat list at {}.".format(constants.now()))
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
	log(client, "I have evaluated the command <code>{}</code> at {}.".format(command, constants.now()))
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
	log(client, "I have executed the command <code>{}</code> at {}.".format(command, constants.now()))
	client.send(UpdateStatus(offline=True))


@app.on_message(
	Filters.command("help", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
		chatIdList))
def help(client: Client, message: Message):
	global commands, constants

	prefixes = list(["/",
					 "!",
					 "."
					])
	"""
		Sending the output
	"""
	message.edit_text("The commands are:\n\t\t<code>{}</code>\nThe prefixes for use this command are:\n\t\t<code>{}</code>".format(
		"<code>\n\t\t</code>".join(commands), "<code>\n\t\t</code>".join(prefixes)))
	log(client, "I sent the help at {}.".format(constants.now()))
	client.send(UpdateStatus(offline=True))


def job(client: Client):
	global constants, scheduler

	"""
		Sending the output
	"""
	scheduler.every().hour.do(subJob, client=client).tag("Temporary")
	log(client, "I done my job at {}.".format(constants.now()))
	client.send(UpdateStatus(offline=True))


def log(client: Client = None, logging: str = ""):
	global constants, initialLog

	if client is not None:
		if initialLog is not None:
			for msg in initialLog:
				client.send_message(constants.log, msg)
			initialLog = None
		client.send_message(constants.log, logging)
		client.send(UpdateStatus(offline=True))
	else:
		initialLog.append(logging)


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & (Filters.user(constants.creator) | Filters.channel))
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
		before = len(lists)
		lists = set(lists)
		lists.add(chat.id)
		lists = list(lists)
		if len(lists) != before:
			chatDict = chat.__dict__
			try:
				del chatDict["_client"]
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
			if chatType is not None:
				constants.chats = dict(chatDict)
				text = "I added {} to the list of allowed chat at {}.".format(chat.title, constants.now())
			else:
				constants.admins = dict(chatDict)
				text = "I added {}".format("{} ".format(chat.first_name) if chat.first_name is not None else "")
				text += "{}to the list of allowed chat at {}.".format("{} ".format(chat.last_name) if chat.last_name is not None else "", constants.now())
	log(client, text)
	client.send(UpdateStatus(offline=True))


def subJob(client: Client):
	global constants

	log(client, "I done my job at {}.".format(constants.now()))
	client.send(UpdateStatus(offline=True))


@app.on_message(Filters.command("update", prefixes=list(["/", "!", "."])) & Filters.user(adminsIdList))
def updateDatabase(client: Client, message: Message = None):
	global adminsIdList, constants, chatIdList

	"""
		Copy the database
	"""
	copyPath = "~/Desktop"
	if constants.databasePath == "/data/data/com.termux/files/home":
		copyPath = "."
	elif constants.databasePath == "/data/data/com.termux/files/home/downloads":
		copyPath = ".."
	os.system("cp {} {}".format(constants.databasePath, copyPath))
	"""
		Clearing the database
	"""
	del constants.admins
	del constants.chats
	"""
		Updateing the admins database
	"""
	chats = client.get_users(adminsIdList)
	chats.append(client.get_me())
	chats = list(map(lambda n: n.__dict__, chats))
	for i in chats:
		try:
			del i["_client"]
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
	constants.admins = chats
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
	for i in chats:
		try:
			del i["_client"]
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
	constants.chats = chats
	"""
		Removing the message
	"""
	if message is not None and len(message.command) != 0:
		message.delete(revoke=True)
	"""
		Removing the copy of the database
	"""
	os.system("rm -rf {}/database.json".format(copyPath))
	log(client, "I have updated the database at {}.".format(constants.now()))
	client.send(UpdateStatus(offline=True))


def unknownFilter():
	global commands

	def func(flt, message):
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
	global constants

	if message.chat.type == "bot":
		return
	message.edit_text("This command isn\'t supported.")
	log(client, "I managed an unsupported command at {}.".format(constants.now()))
	client.send(UpdateStatus(offline=True))


log(logging="Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
log(logging="Setted the markup syntax\nSetting the Job Queue ...")
log(logging="Setted the Job Queue\nStarted serving ...")
scheduler.every().day.do(job, client=app)
i = scheduler.every().week.do(updateDatabase, client=app)
with app:
	i.run()
	while True:
		scheduler.run_pending()
