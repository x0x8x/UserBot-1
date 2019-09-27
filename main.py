from pyrogram import Client, Filters, InlineKeyboardButton, InlineKeyboardMarkup, \
    Message

from modules import Constants

constants = Constants.Constants()
initialLog = list(["Initializing the Admins ...", "Admins initializated\nInitializing the Client ..."])
constants.loadCreators()
adminsIdList = set()
i = constants.admins.to_json(orient="columns")
i = i[len("{\"id\":{"):i.index("}")]
i = i.split(",")
i = list(map(lambda n: n.split(":"), i))
i = list(map(lambda n: dict({n[0]: n[1]}), i))
i = list(map(lambda n: list(n.values()), i))
list(map(lambda n: list(map(lambda m: adminsIdList.add(m), n)), i))
chatIdList = set()
i = constants.admins.to_json(orient="columns")
i = i[len("{\"id\":{"):i.index("}")]
i = i.split(",")
i = list(map(lambda n: n.split(":"), i))
i = list(map(lambda n: dict({n[0]: n[1]}), i))
i = list(map(lambda n: list(n.values()), i))
list(map(lambda n: list(map(lambda m: chatIdList.add(m), n)), i))
app = Client("UserBot", constants.id, constants.hash, phone_number=constants.phoneNumber, first_name="",
             last_name="")


@app.on_message(Filters.chat(chatIdList) & Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
    global constants

    """
        Removing the status message
    """
    message.delete()
    log(client, "I removed a status message from the " + message.chat.title + " at " + constants.now() + ".")


@app.on_message(Filters.chat(chatIdList) & Filters.user(adminsIdList))
def functions(client: Client, message: Message):
    global constants

    message.reply_chat_action("typing")
    pass


def log(client: Client = None, logging: str = ""):
    global constants, initialLog

    if client is not None:
        if initialLog is not None:
            # noinspection PyTypeChecker
            for msg in initialLog:
                client.send_message(constants.log, msg)
            initialLog = None
        client.send_message(constants.log, logging)
    else:
        initialLog.append(logging)


@app.on_message(Filters.chat(chatIdList) & Filters.user(adminsIdList))
def replyInlineKeyboard(client: Client, message: Message):
    """
        Inline button
    """
    global constants

    message.reply_chat_action("typing")
    keyboard = list([list([InlineKeyboardButton("Text", url="Text")]), ...])
    keyboard = InlineKeyboardMarkup(keyboard)
    message.reply_text("Text", disable_web_page_preview=True, reply_markup=keyboard)
    log(client, "I sent an InlineKeyboard to @" + message.from_user.username + " at " + constants.now() + ".")


@app.on_message(Filters.command("retrieve", prefix=list(["/", "!", "."])) & Filters.user(constants.creator))
def retrieveChatId(client: Client, message: Message):
    global constants, chatIdList

    if message.chat.id not in chatIdList:
        constants.chats = dict({"id": message.chat.id, "name": message.chat.title})
        message.delete()
        chatIdList.add(message.chat.id)
        log(client, "I added " + message.chat.title + " to the list of allowed chat at " + constants.now() + ".")


log(logging="Started serving ...")
app.run()
log(logging="Setted the markup syntax")
app.set_parse_mode("markdown")
