from pyrogram import Client, Filters, Message

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
list(map(lambda n: list(map(lambda m: adminsIdList.add(int(m)), n)), i))
adminsIdList = list(adminsIdList)
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
app = Client("UserBot", constants.id, constants.hash, phone_number=constants.phoneNumber)


@app.on_message(Filters.chat(chatIdList) & Filters.service)
def automaticRemovalStatus(client: Client, message: Message):
    global constants

    log(client, "I removed a status message from the {0} at {1}.".format(message.chat.title, constants.now()))
    """
        Removing the status message
    """
    message.delete()


@app.on_message(
    Filters.command("check", prefixes=list(["/", "!", "."])) & Filters.user(constants.creator) & Filters.chat(
        chatIdList))
def checkList(client: Client, message: Message):
    global adminsIdList, constants, chatIdList

    """
        Removing the message
    """
    message.delete()
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
        """
            Adding the chat to the database
        """
        constants.chats = dict({"id": message.chat.id, "name": message.chat.title})
        chatIdList = set(chatIdList)
        chatIdList.add(message.chat.id)
        chatIdList = list(chatIdList)
        log(client, "I added {0} to the list of allowed chat at {1}.".format(message.chat.title, constants.now()))
        """
            Removing the message
        """
        message.delete()


log(logging="Setted the markup syntax")
app.set_parse_mode("markdown")
log(logging="Started serving ...")
app.run()
