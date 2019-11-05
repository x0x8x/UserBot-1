import os
import random
import subprocess
import time
from datetime import date

import schedule
from pyrogram import Client, Filters, Message
from pyrogram.api.functions.help import GetConfig
from pyrogram.api.functions.account import UpdateStatus

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
app = Client("GiuliosUserBot", constants.id, constants.hash, phone_number=constants.phoneNumber)


@app.on_message(
        Filters.command("generator", prefixes=list(["/", "!", "."]))& Filters.user(constants.creator) & Filters.chat(
            chatIdList))
def activateDustGenerator(client: Client, message: Message = None):
    global constants, scheduler

    """
        Removing the message
    """
    message.delete(revoke=True)
    """
        Sending the output
    """
    client.send_message(constants.lootBot, "⏲ Generatore di Polvere (Evento) 🔥", disable_notification=True)
    time.sleep(random.randint(0, 120))
    client.send_message(constants.lootBot, "Aziona Generatore", disable_notification=True)
    time.sleep(random.randint(0, 120))
    client.send_message(constants.lootBot, "Mnu", disable_notification=True)
    scheduler.every().hour.do(collectDust, client=client).tag("Temporary")
    log(client, "I activated the dust generator at {}.".format(constants.now()))


@app.on_message(Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
    """
        Removing the status message
    """
    message.delete(revoke=True)
    client.send(UpdateStatus(offline=True))


@app.on_message(
    Filters.command("bots", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def bots(client: Client, message: Message):
    global constants

    bots = list(["CasaTorinoBot",
                 "CiceroneGuideLootianeBot",
                 "DragonEducatorBot",
                 "FontanelleBot",
                 "PesceMuccaBot",
                 "SavedMessageHelpBot"
                ])
    bots = list(map(lambda n: "<a href=\"https://t.me/{}\">{}</a>".format(n, n), bots))
    """
        Sending the output
    """
    message.edit_text("Your bots are:\n\t{}".format("\n\t".join(bots)), disable_web_page_preview=True)
    log(client, "I sent the bots list at {}.".format(constants.now()))


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


@app.on_message(Filters.command(list(["clear", "clearAll"]), prefixes=list(["/", "!", "."])) & Filters.user(
    constants.creator) & Filters.chat(chatIdList))
def clearChats(client: Client, message: Message):
    global constants

    maxLength = 200
    chat_id = "me"
    parameters = message.command
    command = parameters.pop(0)
    parameters = " ".join(parameters)
    if parameters == "log":
        chat_id = constants.log
    to_delete = client.iter_history(chat_id)
    if chat_id == "me" and command == "clear":
        to_delete = list(filter(lambda n: "#dono" not in n.text and "#restituisco" not in n.text, to_delete))
    to_delete = list(map(lambda n: n.message_id, to_delete))
    """
        Removing the messages
    """
    message.delete(revoke=True)
    for j in range(0, len(to_delete), maxLength):
        client.delete_messages(chat_id, to_delete[j:j + maxLength], revoke=True)
    log(client, "I have cleared the {} chat at {}.".format("Telegram\'s Saved Messages" if chat_id == "me" \
                    else "GiuliosUserBotLog", constants.now()))


def collectDust(client: Client):
    global constants

    """
        Sending the output
    """
    client.send_message(constants.lootBot, "⏲ Generatore di Polvere (Evento) 🔥", disable_notification=True)
    time.sleep(random.randint(0, 120))
    client.send_message(constants.lootBot, "Ritira", disable_notification=True)
    time.sleep(random.randint(0, 120))
    client.send_message(constants.lootBot, "Mnu", disable_notification=True)
    log(client, "I collected dust at {}.".format(constants.now()))


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
    text = "<b>Espression:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
    maxLength = client.send(GetConfig()).message_length_max
    message.edit_text(text[:maxLength])
    if len(text) >= maxLength:
        for k in range(1, len(text), maxLength):
            message.reply_text(text[k:k + maxLength])
    log(client, "I have evaluated the command <code>{}<code> at {}.".format(command, constants.now()))


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
        result = result.replace("\n", "</code>\n\t<code>")
    """
        Sending the output
    """
    text = "<b>Command:</b>\n\t<code>{}</code>\n\n<b>Result:</b>\n\t<code>{}</code>".format(command, result)
    maxLength = client.send(GetConfig()).message_length_max
    message.edit_text(text[:maxLength])
    if len(text) >= maxLength:
        for k in range(1, len(text), maxLength):
            message.reply_text(text[k:k + maxLength])
    log(client, "I have executed the command <code>{}</code> at {}.".format(command, constants.now()))


@app.on_message(Filters.mentioned)
def forwardTags(client: Client, message: Message):
    global constants

    if message.text is not None and message.from_user.id != constants.lootBotPlus:
        text = message.text.lower()
        if "@giuliocoaincamelcase" in text:
            """
                Sending the output
            """
            message.forward("me", disable_notification=True)
    client.send(UpdateStatus(offline=True))


@app.on_message(
    Filters.command("groups", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def groups(client: Client, message: Message):
    global constants

    """
        Sending the output
    """
    message.edit_text("Your groups are:\n" +
                      "\t<a href=\"https://t.me/joinchat/FbxqIBLmmKUHN0kTkfMj7g\">Aula Studio</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/FbxqIBC6c3T7v7KmsgRzgg\">AulaStudioUnCazzo</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAE2Do1DHTDBhindZ_A\">CasaTorinoLog</a>\n" +
                      "\t<a href=\"https://t.me/CHANGELOGDragonEducatorBot\">[CHANGELOG] Educatore dei Draghi</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAEqDSDf4uB9wgjygmQ\">DragonEducatorLog</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAEc1Q4i44WINUiPbnQ\">FontanelleLog</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAEdW-iFCiMxFqtpK3Q\">GiulioUserBotLog</a>\n" +
                      "\t<a href=\"https://t.me/GuideLootiane\">Guide Lootiane</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/C8pTXUc-3nBq3vnO1-tYSA\">Ombrelli alcolizzati</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAEZakE38vKzIPsA5nA\">PesceMuccaLog</a>\n" +
                      "\t<a href=\"https://t.me/pythonlootbot\">python-loot-bot</a>\n" +
                      "\t<a href=\"https://t.me/pythonlootbotgroup\">python-loot-bot</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAEaBjOyzebZU_ctEFw\">python-loot-bot Log</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/G5bsZxTpUmNkfdzYCfWFzw\">python-loot-bot Staff Group</a>\n" +
                      "\t<a href=\"https://t.me/joinchat/AAAAAE1Tj2KE7MU24s-XBg\">SavedMessageHelpLog</a>",
                      disable_web_page_preview=True)
    log(client, "I sent the groups list at {}.".format(constants.now()))


@app.on_message(
    Filters.command("help", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def help(client: Client, message: Message):
    global constants

    commands = list(["bots",
                     "check",
                     "clear",
                     "clearAll",
                     "evaluate",
                     "exec",
                     "groups",
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
    message.edit_text("The commands are:\n\t\t<code>{}</code>\nThe prefixes for use this command are:\n\t\t<code>{}</code>".format(
        "<code>\n\t\t</code>".join(bots), "<code>\n\t\t</code>".join(prefixes)))
    log(client, "I sent the help at {}.".format(constants.now()))


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


@app.on_message(Filters.user(constants.lootBot))
def lootBot(client: Client, message: Message):
    global constants, scheduler

    flag = True
    text = ""
    if "Hai completato l\'esplorazione della cava" in message.text:
        """
            Sending the output
        """
        message.reply_text("Esplorazioni 🗺", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Viaggia a Cava Vesak (2 ore e 40 min)", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Si", disable_notification=True)
        text = "I set a quarries at {}.".format(constants.now())
    elif "📜 Report battaglia del turno" in message.text:
        if "> 55 🦋" not in message.text:
            if "> 15 🦋" in message.text:
                time.sleep(random.randint(0, 180))
            text = message.text
            text = text.splitlines()
            text = list(filter(lambda n: "📜 Report battaglia del turno" in n, text))
            text = text.pop(0)
            text = text[len("📜 Report battaglia del turno "):text.index(")")]
            rounds = text[:text.index(" ")]
            rounds = int(rounds)
            text = text[text.index("(") + 1:]
            """
                Sending the output
            """
            message.reply_text("Inc", disable_notification=True)
            text = "I increased for round {} of the {} at {}.".format(rounds, text, constants.now())
    elif "Il tuo gnomo non è riuscito a raggiungere il rifugio nemico, dannazione!" == message.text or \
            "La tua combinazione di rune (" in message.text:
        """
            Sending the output
        """
        message.reply_text("Mm", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Invia Piedelesto", disable_notification=True)
        text = "I sent Piedelesto to inspect somebody at {}.".format(constants.now())
    elif "Missione completata!" in message.text:
        """
            Sending the output
        """
        message.reply_text("⚔ Missione ⚔", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Si", disable_notification=True)
        text = "I started a Mission at {}.".format(constants.now())
    elif "Durante l\'estrazione di Mana trovi una vena più ricca del solito!" in message.text:
        """
            Sending the output
        """
        message.reply_text("Scava!", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Si", disable_notification=True)
        text = "I collected the Mana bonus at {}.".format(constants.now())
    elif "Durante la produzione del generatore arriva una folata di vento trascinando un po\' di " + \
            "polvere!" in message.text:
        """
            Sending the output
        """
        message.reply_text("Spolvera!", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Si", disable_notification=True)
        text = "I collected the dust bonus at {}.".format(constants.now())
    elif "Il tuo gnomo è arrivato al rifugio nemico, il guardiano del cancello ti propone uno strano gioco " + \
            "con le Rune" in message.text:
        """
            Sending the output
        """
        message.reply_text("Rifugio 🔦", disable_notification=True)
        time.sleep(random.randint(0, 120))
        message.reply_text("Contatta lo Gnomo 💭", disable_notification=True)
        text = "I sent the gnome to retrieve the runes at {}.".format(constants.now())
    elif "I Generatori di Polvere sono stati spenti!" == message.text:
        scheduler.clear("Temporary")
        text = "I stopped the collection of dust at {}.".format(constants.now())
    elif "Hai generato fin ora" in message.text:
        """
            Sending the output
        """
        message.reply_text("Ritira", disable_notification=True)
        text = "I collected the dust at {}.".format(constants.now())
    elif "Gestione Generatore" in message.text:
        """
            Sending the output
        """
        message.reply_text("Aziona Generatore", disable_notification=True)
        text = "I activated the dust generator at {}.".format(constants.now())
    else:
        flag = False
    if flag is True:
        time.sleep(random.randint(0, 120))
        message.reply_text("Mnu", disable_notification=True)
        log(client, text)


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def retrieveChatId(client: Client, message: Message):
    global constants, chatIdList

    title = message.chat.title
    identifier = message.chat.id
    text = "The chat {} is already present in the list of allowed chat.".format(title)
    """
        Removing the message
    """
    message.delete(revoke=True)
    if identifier not in chatIdList and identifier != constants.creator:
        """
            Adding the chat to the database
        """
        before = len(chatIdList)
        chatIdList = set(chatIdList)
        chatIdList.add(identifier)
        chatIdList = list(chatIdList)
        if len(chatIdList) != before:
            constants.chats = dict({"id": identifier, "name": title})
            text = "I added {} to the list of allowed chat at {}.".format(title, constants.now())
    log(client, text)


log(logging="Client initializated\nSetting the markup syntax ...")
app.set_parse_mode("html")
log(logging="Setted the markup syntax\nSetting the Job Queue ...")
log(logging="Setted the Job Queue\nStarted serving ...")
scheduler.every().monday.at("00:15").do(activateDustGenerator, client=app)
with app:
	while True:
		scheduler.run_pending()
