import math
import socket
import threading

import select
from protocol import *

SERVER_IP = "0.0.0.0"
DICTIONARY_SOCKETS = dict()
MESSAGES_TO_SEND = []
MESSAGES_TO_SEND_LOCK = threading.Lock()
DICTIONARY_SOCKETS_LOCK = threading.Lock()


class SocketsInfo:
    client_socket = socket
    client_name = ""

    def __init__(self, client_socket, client_name):
        self.client_socket = client_socket
        self.client_name = client_name

    def __str__(self):
        return self.client_name


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
    list_msg = []
    msg = "ans_all " + json.dumps(
        dict(zip(DICTIONARY_SOCKETS.keys(), [i.client_name for i in DICTIONARY_SOCKETS.values()])))
    transaction_id = time.localtime()
    transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
        transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " "
    count_msg = 1
    for i in range(0, len(msg), 1048576):
        if i + 1048576 > len(msg):
            list_msg.append(transaction_id + str(count_msg) + " " + msg[i:])
        list_msg.append(transaction_id + str(count_msg) + " " + msg[i:i + 1048576])
        count_msg += 1
    for i in list_msg:
        MESSAGES_TO_SEND.append((client_socket, create_msg(i)))


def closing_client(client_socket):
    """
    Closing communication with a client
    :param client_socket:What a customer to close
    """
    name = find_socket(client_socket)
    msg = "ans_delete " + DICTIONARY_SOCKETS[name].client_name
    transaction_id = time.localtime()
    transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
        transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
    # delete socket from list
    for i in DICTIONARY_SOCKETS.keys():
        MESSAGES_TO_SEND.append(
            (DICTIONARY_SOCKETS[i], create_msg(transaction_id + msg)))
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
    transaction_id = time.localtime()
    transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
        transaction_id.tm_sec.real) + "_"
    # if he got only NAME send is name
    if len(data) == 0:
        for i in DICTIONARY_SOCKETS.keys():
            if DICTIONARY_SOCKETS[i].client_socket == client_socket:
                msg = "ans_name_ " + str(i)
                transaction_id += str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
                MESSAGES_TO_SEND.append((client_socket, create_msg(transaction_id + msg)))
                return
    else:
        name = data
    if name in DICTIONARY_SOCKETS.keys():
        msg = "ans_error_<name" + name + "> " + " this name already exists"
        transaction_id += str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg(transaction_id + msg)))
    else:
        # if he wants change his name
        for i in DICTIONARY_SOCKETS.values():
            if client_socket == i.client_socket:
                key = find_socket(client_socket)
                DICTIONARY_SOCKETS[key].client_name = name
                msg = "ans_success_<name:" + name + "> "
                transaction_id += str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
                MESSAGES_TO_SEND.append((client_socket, create_msg(transaction_id + msg)))
                break
    for i in DICTIONARY_SOCKETS.keys():
        print(i + ":" + DICTIONARY_SOCKETS[i].client_name)


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
        msg = "ans_error_<msg>" + " who you want tho send message?"
        transaction_id = time.localtime()
        transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
            transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg(transaction_id + msg)))
        return
    data[0] += '}'
    msg_to = eval(data[0])
    data = data[1]
    # get empty message
    if data in EMPTY_DATA:
        data = '" "'
    print("data", len(data))
    # looking for destination
    msg = "msg " + DICTIONARY_SOCKETS[find_socket(client_socket)].client_name + " " + data
    for i in msg_to:
        try:
            transaction_id = time.localtime()
            transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
                transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " "
            list_msg = []
            print("num tranaction:", str(math.ceil(len(msg) / 1048576)).zfill(3))
            count_msg = 1
            for k in range(0, len(msg), 1048576):
                if k + 1048576 > len(msg):
                    list_msg.append(transaction_id + str(count_msg) + " " + msg[k:])
                else:
                    list_msg.append(transaction_id + str(count_msg) + " " + msg[k:k + 1048576])
                count_msg += 1
            print("len list", len(list_msg))
            for k in list_msg:
                MESSAGES_TO_SEND.append((DICTIONARY_SOCKETS[i].client_socket, create_msg(k)))
        except KeyError:
            msg = "ans_error_<msg> " + " no client with " + i + " name"
            transaction_id = time.localtime()
            transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
                transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
            # destination not found
            MESSAGES_TO_SEND.append(
                (client_socket, create_msg(transaction_id + msg)))


def get_name(client_socket, name):
    key = find_name(name)

    if key is not None:
        msg = "return_name_<" + name + "> " + key
        transaction_id = time.localtime()
        transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
            transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
        MESSAGES_TO_SEND.append((client_socket, create_msg(transaction_id + msg)))
    else:
        msg = "ans_error_<name" + name + "> " + " not exists"
        transaction_id = time.localtime()
        transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
            transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
        MESSAGES_TO_SEND.append(
            (client_socket, create_msg(transaction_id + msg)))


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
    elif cmd == "waiting":
        return
    else:
        MESSAGES_TO_SEND.append((client_socket, create_msg("Invalid command, please enter NAME,MSG,GET_NAMES or EXIT")))


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, PORT))
    server_socket.listen()
    print("Listening for clients...")
    recv_thread = threading.Thread(target=recev_socket, args=(server_socket,))
    send_thread = threading.Thread(target=send_method)
    while True:
        try:
            if not recv_thread.is_alive():
                recv_thread.start()
        except RuntimeError as e:
            try:

                recv_thread.run()
            except AttributeError as e:

                recv_thread = threading.Thread(target=recev_socket, args=(server_socket,))
                recv_thread.run()
        try:
            if not send_thread.is_alive():
                send_thread.start()
        except RuntimeError as e:
            try:
                send_thread.run()
            except AttributeError as e:

                send_thread = threading.Thread(target=send_method)
                send_thread.run()

        except IndexError as e:
            print(e)
            pass


def send_method():
    while True:
        with DICTIONARY_SOCKETS_LOCK:
            sockets = list(map(lambda item: item.client_socket, DICTIONARY_SOCKETS.values()))
        if not sockets:
            continue
        rlist, wlist, xlist = select.select([], sockets, [])
        for message_to_send in MESSAGES_TO_SEND:
            current_socket, data = message_to_send
            if current_socket in wlist:
                try:
                    current_socket.send(data)
                except ConnectionAbortedError:
                    closing_client(current_socket)
                except ConnectionResetError:
                    try:
                        closing_client(current_socket)
                    except KeyError:
                        pass
            with MESSAGES_TO_SEND_LOCK:
                MESSAGES_TO_SEND.remove(message_to_send)


def recev_socket(server_socket):
    while True:
        with DICTIONARY_SOCKETS_LOCK:
            sockets = list(map(lambda item: item.client_socket, DICTIONARY_SOCKETS.values()))
        rlist, wlist, xlist = select.select(sockets + [server_socket], [], [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                # Saves the client if the port number the server brought to it
                with DICTIONARY_SOCKETS_LOCK:
                    DICTIONARY_SOCKETS[str(client_address[1])] = SocketsInfo(connection, str(client_address[1]))
            else:
                flag = bool
                data = str
                to_msg = ""
                cmd = ""
                try:
                    flag, cmd, data = get_msg(current_socket)

                except ConnectionResetError:
                    with DICTIONARY_SOCKETS_LOCK:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))
                except ConnectionAbortedError:
                    with DICTIONARY_SOCKETS_LOCK:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))

                if flag:
                    check_cmd(cmd, data, current_socket)
                else:
                    # if client fall by ctrl+c
                    if data == "":
                        closing_client(current_socket)
                    else:
                        print(data)
                        with MESSAGES_TO_SEND_LOCK:
                            MESSAGES_TO_SEND.append((current_socket, create_msg(data)))


if __name__ == "__main__":
    main()
