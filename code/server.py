import socket
import select
from protocol import *

SERVER_IP = "0.0.0.0"
DICTIONARY_SOCKETS = dict()
MESSAGES_TO_SEND = []


class SocketsInfo:
    client_socket = socket
    client_name = ""

    def __init__(self, client_socket, client_name):
        self.client_socket = client_socket
        self.client_name = client_name


def find_socket(client_socket):
    """
    Finds the specific socket it received in the socket list
    :param client_socket: Search specific socket
    :return: key for socket
    """
    for i in DICTIONARY_SOCKETS.keys():
        if DICTIONARY_SOCKETS[i].client_socket == client_socket:
            return i
    return None


def find_name(name):
    for i in DICTIONARY_SOCKETS.keys():
        if DICTIONARY_SOCKETS[i].client_name == name:
            return i
    return None


def get_names(client_socket):
    """
    return al sockets name
    :param client_socket: Which socket to return the answer to
    """
    MESSAGES_TO_SEND.append((client_socket, create_msg("ans_all " + json.dumps(
        dict(zip(DICTIONARY_SOCKETS.keys(), [i.client_name for i in DICTIONARY_SOCKETS.values()]))))))


def closing_client(client_socket):
    """
    Closing communication with a client
    :param client_socket:What a customer to close
    """
    name = find_socket(client_socket)
    # delete socket from list
    for i in DICTIONARY_SOCKETS.keys():
        MESSAGES_TO_SEND.append(
            (DICTIONARY_SOCKETS[i], create_msg("ans_delete " + DICTIONARY_SOCKETS[name].client_name)))
    DICTIONARY_SOCKETS.pop(name)
    print("Connection " + name + " closed")
    client_socket.close()


def name_setting(client_socket, data):
    """
    enter socket name to dictionary
    :param client_socket: which socket save name
    :param data:what the name
    """
    name = str
    # if he got only NAME send is name
    if len(data) == 0:
        for i in DICTIONARY_SOCKETS.keys():
            if DICTIONARY_SOCKETS[i].client_socket == client_socket:
                MESSAGES_TO_SEND.append((client_socket, create_msg("ans_name_ " + str(i))))
                return
    else:
        name = data
    if name in DICTIONARY_SOCKETS.keys():
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg("ans_error_<name" + name + "> " + " this name already exists")))
    else:
        # if he wants change his name
        for i in DICTIONARY_SOCKETS.values():
            if client_socket == i.client_socket:
                key = find_socket(client_socket)
                DICTIONARY_SOCKETS[key].client_name = name
                MESSAGES_TO_SEND.append((client_socket, create_msg("ans_success_<name:" + name + "> ")))
                return


def message(client_socket, data):
    """
    send message to auther clients

    :param client_socket: source
    :param data: destination and message
    """
    msg_to = ""
    data = data.split('}', 1)
    # gen msg commend without destination
    if len(data) == 1:
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg("ans_error_<msg>" + " who you want tho send message?")))
        return
    data[0] += '}'
    msg_to = eval(data[0])
    data = data[1]
    # get empty message
    if data == "":
        data = '" "'

    # looking for destination
    msg = "msg " + DICTIONARY_SOCKETS[find_socket(client_socket)].cliet_name + " " + data
    for i in msg_to:
        try:
            MESSAGES_TO_SEND.append((DICTIONARY_SOCKETS[i].client_socket, create_msg(msg)))
        except KeyError:
            # destination not found
            MESSAGES_TO_SEND.append(
                (client_socket, create_msg("ans_error_<msg>" + " no client with " + i + "name")))


def get_name(client_socket, name):
    key = find_name(name)
    if key is not None:
        MESSAGES_TO_SEND.append((client_socket, create_msg("return_name_<" + name + "> " + key)))
    else:
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg("ans_error_<name" + name + "> " + " not exists")))


def check_cmd(cmd, data, client_socket):
    cmd = cmd.lower()
    if cmd == "get_names":
        get_names(client_socket)
    if cmd == "get_name":
        get_name(client_socket, data)
    elif cmd == "exit":
        closing_client(client_socket)
    elif cmd == "name":
        name_setting(client_socket, data)
    elif cmd == "msg":
        message(client_socket, data)
    else:
        MESSAGES_TO_SEND.append((client_socket, create_msg("Invalid command, please enter NAME,MSG,GET_NAMES or EXIT")))


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen()
    print("Listening for clients...")

    while True:
        try:
            sockets = list(map(lambda item: item.client_socket, DICTIONARY_SOCKETS.values()))
            rlist, wlist, xlist = select.select(sockets + [server_socket], sockets, [])
            for current_socket in rlist:
                if current_socket is server_socket:
                    connection, client_address = current_socket.accept()
                    print("New client joined!", client_address)
                    # Saves the client if the port number the server brought to it
                    DICTIONARY_SOCKETS[str(client_address[1])] = SocketsInfo(connection, str(client_address[1]))
                else:
                    flag = bool
                    data = str
                    to_msg = ""
                    cmd = ""
                    try:
                        flag, cmd, data = get_msg(current_socket)

                    except ConnectionResetError:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))

                    if flag:
                        check_cmd(cmd, data, current_socket)
                    else:
                        # if client fall by ctrl+c
                        if data == "":
                            closing_client(current_socket)
                        else:
                            print(data)
                            MESSAGES_TO_SEND.append((current_socket, create_msg(data)))

            for message_to_send in MESSAGES_TO_SEND:
                current_socket, data = message_to_send
                if current_socket in wlist:
                    try:
                        current_socket.send(data)
                    except ConnectionResetError:
                        closing_client(current_socket)
                MESSAGES_TO_SEND.remove(message_to_send)
        except IndexError as e:
            print(e)
            pass


if __name__ == "__main__":
    main()
