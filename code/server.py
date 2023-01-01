import socket
import select
from protocol import *

SERVER_IP = "0.0.0.0"
DICTIONARY_SOCKETS = dict()
MESSAGES_TO_SEND = []


def find_socket(client_socket):
    """
    Finds the specific socket it received in the socket list
    :param client_socket: Search specific socket
    :return: key for socket
    """
    for i in DICTIONARY_SOCKETS.keys():
        if DICTIONARY_SOCKETS[i] == client_socket:
            return i


def get_names(client_socket):
    """
    return al sockets name
    :param client_socket: Which socket to return the answer to
    """
    MESSAGES_TO_SEND.append((client_socket, create_msg('\n'.join(list(DICTIONARY_SOCKETS.keys())))))


def closing_client(client_socket):
    """
    Closing communication with a client
    :param client_socket:What a customer to close
    """
    name = find_socket(client_socket)
    # delete socket from list
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
    if len(data) == 1:
        for i in DICTIONARY_SOCKETS.keys():
            if DICTIONARY_SOCKETS[i] == client_socket:
                MESSAGES_TO_SEND.append((client_socket, create_msg("your name is: " + str(i))))
                return
    else:
        name = data[1]
    if name in DICTIONARY_SOCKETS.keys():
        MESSAGES_TO_SEND.append((client_socket, create_msg("this name already exists")))
    else:
        # if he wants change his name
        if client_socket in DICTIONARY_SOCKETS.values():
            old_name = find_socket(client_socket)
            MESSAGES_TO_SEND.append((client_socket, create_msg("hello " + name)))
            DICTIONARY_SOCKETS[name] = client_socket
            DICTIONARY_SOCKETS.pop(old_name)
            return
        DICTIONARY_SOCKETS[name] = client_socket
        MESSAGES_TO_SEND.append((client_socket, create_msg("hello " + name)))


def message(client_socket, data):
    """
    send message to auther clients
    :param client_socket: source
    :param data: destination and message
    """
    # gen msg commend without destination
    if len(data) == 1:
        MESSAGES_TO_SEND.append((client_socket, create_msg("who you want tho send message?")))
        return
    dst = data[1].split(" ", 1)
    # get empty message
    if len(dst) == 1:
        msg = '" "'
    else:
        msg = dst[1]
    try:
        # looking for destination
        msg = find_socket(client_socket) + " say " + msg
        MESSAGES_TO_SEND.append((DICTIONARY_SOCKETS[dst[0]], create_msg(msg)))
    except KeyError:
        # destination not found
        MESSAGES_TO_SEND.append((client_socket, create_msg("no client with this name")))


def check_cmd(data, client_socket):
    """
    Checking that the commands are recognized
    :param data:
    :param client_socket:
    """
    # get the cmd
    cmd = data.split(" ", 1)
    cmd[0] = cmd[0].lower()
    if cmd[0] == "get_names":
        get_names(client_socket)
    elif cmd[0] == "exit":
        closing_client(client_socket)
    elif cmd[0] == "name":
        name_setting(client_socket, cmd)
    elif cmd[0] == "msg":
        message(client_socket, cmd)
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
            rlist, wlist, xlist = select.select(list(DICTIONARY_SOCKETS.values()) + [server_socket],
                                                list(DICTIONARY_SOCKETS.values()), [])
            for current_socket in rlist:
                if current_socket is server_socket:
                    connection, client_address = current_socket.accept()
                    print("New client joined!", client_address)
                    # Saves the client if the port number the server brought to it
                    DICTIONARY_SOCKETS[str(client_address[1])] = connection
                else:
                    flag = bool
                    data = str
                    try:
                        flag, data = get_msg(current_socket)

                    except ConnectionResetError:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))

                    if flag:
                        check_cmd(data, current_socket)
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
                    current_socket.send(data)
                MESSAGES_TO_SEND.remove(message_to_send)
        except IndexError as e:
            print(e)
            pass


if __name__ == "__main__":
    main()
