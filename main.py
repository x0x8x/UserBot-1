from pyrogram import Client, Filters, Message

from modules import Constants

constants = Constants.Constants()
initialLog = list(["Initializing the Admins ...", "Admins initializated\nSetting the admins list ...",
                   "Admins setted\nSetting the chats list ...", "Chats initializated\nInitializing the Client ..."])
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


@app.on_message(Filters.chat(chatIdList) & Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
    global constants

    title = message.chat.title
    """
        Removing the status message
    """
    message.delete(revoke=True)
    log(client, "I removed a status message from the {0} at {1}.".format(title, constants.now()))


@app.on_message(
    Filters.command("check", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def checkList(client: Client, message: Message):
    global adminsIdList, constants, chatIdList

    """
        Removing the message
    """
    message.delete(revoke=True)
    """
        Sending the output
    """
    print("{0}".format(adminsIdList))
    for j in adminsIdList:
        print("\t{0} - {1}".format(j, type(j)))
    print("\n\n{0}".format(chatIdList))
    for j in chatIdList:
        print("\t{0} - {1}".format(j, type(j)))
    log(client, "I have checked the admin and the chat list at {0}.".format(constants.now()))


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


@app.on_message(Filters.command("retrieve", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator))
def retrieveChatId(client: Client, message: Message):
    global constants, chatIdList

    if message.chat.id not in chatIdList and message.chat.id != constants.creator:
        title = message.chat.title
        id = message.chat.id
        """
            Removing the message
        """
        message.delete(revoke=True)
        """
            Adding the chat to the database
        """
        before = len(chatIdList)
        chatIdList = set(chatIdList)
        chatIdList.add(id)
        chatIdList = list(chatIdList)
        if len(chatIdList) != before:
            constants.chats = dict({"id": id, "name": title})
        log(client, "I added {0} to the list of allowed chat at {1}.".format(title, constants.now()))


log(logging="Setted the markup syntax")
app.set_parse_mode("markdown")
log(logging="Started serving ...")
app.run()
