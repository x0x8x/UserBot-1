import os
import subprocess

import schedule
from pyrogram import Client, Filters, Message
from pyrogram.api.functions.help import GetConfig

from modules import Constants

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
    element = element.replace(":", ": ")
    element = element.replace(",", ", ")
    print("{}".format(element))
    print("\n{}\n".format(adminsIdList))
    for j in adminsIdList:
        print("\t{} - {}".format(j, type(j)))
    element = constants.chats.to_json(orient="records")
    element = element.replace(":", ": ")
    element = element.replace(",", ", ")
    print("\n{}".format(element))
    print("\n{}\n".format(chatIdList))
    for j in chatIdList:
        print("\t{} - {}".format(j, type(j)))
    print("\n\n")
    log(client, "I have checked the admin and the chat list at {}.".format(constants.now()))


@app.on_message(Filters.command("evaluate", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def evaluation(client: Client, message: Message):
    """
        Extract the command
    """
    command = message.command
    command.pop(0)
    command = " ".join(command)
    result = eval(command)
    """
        Sending the output
    """
    text = "**Expression:**\n\t`{}`\n\n**Result:**\n\t`{}`".format(command, result)
    maxLength = client.send(GetConfig()).message_length_max
    message.edit_text(text[:maxLength])
    if len(text) >= maxLength:
        for k in range(1, len(text), maxLength):
            message.reply_text(text[k:k + maxLength])
    log(client, "I have evaluated the command `{}` at {}.".format(command, constants.now()))


@app.on_message(Filters.command("exec", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def execution(client: Client, message: Message):
    """
        Extract the command
    """
    command = message.command
    command.pop(0)
    command = " ".join(command)
    """
        Execution of the command
    """
    if command == "clear":
        os.system(command)
    result = subprocess.check_output(command, shell=True)
    result = result.decode("utf-8")
    if "\n" in result:
        result = result.replace("\n", "`\n\t`")
    """
        Sending the output
    """
    text = "**Command:**\n\t`{}`\n\n**Result:**\n\t`{}`".format(command, result)
    maxLength = client.send(GetConfig()).message_length_max
    message.edit_text(text[:maxLength])
    if len(text) >= maxLength:
        for k in range(1, len(text), maxLength):
            message.reply_text(text[k:k + maxLength])
    log(client, "I have executed the command `{}` at {}.".format(command, constants.now()))


@app.on_message(
    Filters.command("help", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def help(client: Client, message: Message):
    global constants

    commands = list(["check",
                     "evaluate",
                     "exec",
                     "help",
                     "retrieve"
                    ])
    prefixes = list(["/",
                     "!",
                     "."
                    ])
    """
        Sending the output
    """
    message.edit_text("The commands are:\n\t\t`{}`\nThe prefixes for use this command are:\n\t\t`{}`".format(
        "`\n\t\t`".join(bots), "`\n\t\t`".join(prefixes)))
    log(client, "I sent the help at {}.".format(constants.now()))


def job(client: Client):
    log(client, "I have do my job at {}.".format(constants.now()))


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


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def retrieveChatId(client: Client, message: Message):
    global constants, chatIdList

    title = message.chat.title
    id = message.chat.id
    text = "The chat {} is already present in the list of allowed chat.".format(title)
    """
        Removing the message
    """
    message.delete(revoke=True)
    if id not in chatIdList and id != constants.creator:
        """
            Adding the chat to the database
        """
        before = len(chatIdList)
        chatIdList = set(chatIdList)
        chatIdList.add(id)
        chatIdList = list(chatIdList)
        if len(chatIdList) != before:
            constants.chats = dict({"id": id, "name": title})
            text = "I added {} to the list of allowed chat at {}.".format(title, constants.now())
    log(client, text)


log(logging="Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("markdown")
log(logging="Setted the markup syntax\nSetting the Job Queue ...")
log(logging="Setted the Job Queue\nStarted serving ...")
app.run()
scheduler.every().day.at("13:00").do(job, client=app)
while True:
    scheduler.run_pending()
