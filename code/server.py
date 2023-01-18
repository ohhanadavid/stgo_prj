import json
import socket

import select

from protocol import *

SERVER_IP = "0.0.0.0"
DICTIONARY_SOCKETS = dict()
MESSAGES_TO_SEND = []
MESSAGES_ACK = dict()
MESSAGES_TO_SEND_LOCK = threading.Lock()
DICTIONARY_SOCKETS_LOCK = threading.Lock()

hacker_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hacker_server.bind((SERVER_IP, 5))
hacker_server.listen()
hacker_socket = socket
hacker_address = 0
hacker_list = []


class SocketsInfo:
    client_socket = socket
    client_name = ""
    client_image = None

    def __init__(self, client_socket, client_name, image=None):
        self.client_socket = client_socket
        self.client_name = client_name
        self.client_image = image

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
    ack_number = str(random.randint(100000, 999999))
    msg = ack_number + " ans_all " + json.dumps(
        dict(zip(DICTIONARY_SOCKETS.keys(), [i.client_name for i in DICTIONARY_SOCKETS.values()])))

    MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
    MESSAGES_TO_SEND.append(ack_number)


def closing_client(client_socket):
    """
    Closing communication with a client
    :param client_socket:What a customer to close
    """
    name = find_socket(client_socket)
    msg = "ans_delete " + DICTIONARY_SOCKETS[name].client_name

    for i in DICTIONARY_SOCKETS.keys():
        ack_number = str(random.randint(100000, 999999))

        MESSAGES_ACK[ack_number] = [Ack.waiting, (DICTIONARY_SOCKETS[i], msg)]
        MESSAGES_TO_SEND.append(ack_number)

    DICTIONARY_SOCKETS.pop(name)

    print("Connection " + name + " closed")
    try:
        client_socket.close()
    except OSError as e:
        if e.__str__() in "OSError: [WinError 10038] An operation was attempted on something that is not a socket":
            return


def name_setting(client_socket, data):
    """
    enter socket name to dictionary
    :param client_socket: which socket save name
    :param data:what the name
    """

    if len(data) == 0:
        for i in DICTIONARY_SOCKETS.keys():
            if DICTIONARY_SOCKETS[i].client_socket == client_socket:
                msg = "ans_name_ " + str(i)
                ack_number = str(random.randint(100000, 999999))
                MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, ack_number + " " + msg)]
                MESSAGES_TO_SEND.append(ack_number)

                return
    else:
        name = data
    if name in DICTIONARY_SOCKETS.keys():
        ack_number = str(random.randint(100000, 999999))
        msg = ack_number + " ans_error_<name" + name + "> " + " this name already exists"

        MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
        MESSAGES_TO_SEND.append(ack_number)

    else:
        # if he wants change his name
        for i in DICTIONARY_SOCKETS.values():
            if client_socket == i.client_socket:
                key = find_socket(client_socket)
                DICTIONARY_SOCKETS[key].client_name = name
                ack_number = str(random.randint(100000, 999999))
                msg = ack_number + " ans_success_<name:" + name + "> "

                MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
                MESSAGES_TO_SEND.append(ack_number)

                break
    for i in DICTIONARY_SOCKETS.keys():
        print(i + ":" + DICTIONARY_SOCKETS[i].client_name)


def message(client_socket, data, ack):
    """
    send message to auther clients

    :param ack:
    :param client_socket: source
    :param data: destination and message
    """

    data = data.split('}', 1)
    # gen msg commend without destination
    if len(data) == 1:
        msg = "ans_error_<msg>" + " who you want tho send message?"

        ack_number = str(random.randint(100000, 999999))
        MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
        MESSAGES_TO_SEND.append(ack_number)

        return
    data[0] += '}'
    msg_to = eval(data[0])
    data = data[1]
    # get empty message
    if data in EMPTY_DATA:
        data = '" "'
    print("data", len(data))
    # looking for destination
    msg = ack + " msg " + DICTIONARY_SOCKETS[find_socket(client_socket)].client_name + " " + data
    for i in msg_to:
        try:

            ack_number = str(random.randint(100000, 999999))
            MESSAGES_ACK[ack_number] = [Ack.transport, (DICTIONARY_SOCKETS[i].client_socket, msg)]
            MESSAGES_TO_SEND.append(ack_number)

        except KeyError:
            msg_error = "ans_error_<msg> " + " no client with " + i + " name"

            ack_number = str(random.randint(100000, 999999))
            MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg_error)]
            MESSAGES_TO_SEND.append(ack_number)


def get_name(client_socket, name):
    """
    Sends the name saved on the server to the requester
    :param client_socket:
    :param name:
    :return:
    """
    key = find_name(name)

    if key is not None:
        msg = "return_name_<" + name + "> " + key + " "
        ack_number = str(random.randint(100000, 999999))
        MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
        MESSAGES_TO_SEND.append(ack_number)

    else:
        msg = "ans_error_<name" + name + "> " + " not exists"
        ack_number = str(random.randint(100000, 999999))
        MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, msg)]
        MESSAGES_TO_SEND.append(ack_number)


def ack_recv(ack, cmd, data):
    try:
        client_socket = DICTIONARY_SOCKETS[data].client_socket
    except KeyError:
        return
    ack_massege((client_socket, ack + " " + cmd), MESSAGES_ACK, MESSAGES_TO_SEND)


def check_cmd(ack, cmd, data, client_socket):
    """
    Checking the request sent to the server
    :param ack:
    :param cmd:
    :param data:
    :param client_socket:
    :return:
    """
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
        message(client_socket, data, ack)
    elif cmd == "waiting":
        return
    elif "ack" in cmd:
        ack_recv(ack, cmd, data)
    else:
        ack_number = str(random.randint(100000, 999999))
        MESSAGES_ACK[ack_number] = [Ack.waiting, (client_socket, "Invalid command")]
        MESSAGES_TO_SEND.append(ack_number)


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((SERVER_IP, PORT))

    server_socket.listen()
    print("Listening for clients...")
    recv_thread = threading.Thread(target=recv_socket, args=(server_socket,))
    send_thread = threading.Thread(target=send_method)
    while True:
        try:
            if not recv_thread.is_alive():
                recv_thread.start()
        except RuntimeError:
            try:

                recv_thread.run()
            except AttributeError:

                recv_thread = threading.Thread(target=recv_socket, args=(server_socket,))
                recv_thread.run()
        try:
            if not send_thread.is_alive():
                send_thread.start()
        except RuntimeError:
            try:
                send_thread.run()
            except AttributeError:

                send_thread = threading.Thread(target=send_method)
                send_thread.run()

        except IndexError as e:
            print(e)
            pass


def hacker_methode_recv(data):
    """
    Sending the information to the connected listener
    :param data:
    :return:
    """
    global hacker_list
    try:
        for m in create_msg(data):
            hacker_socket.send(m)
    except ConnectionAbortedError:
        hacker_server.close()
        hacker_list = []
    except ConnectionResetError:
        hacker_server.close()
        hacker_list = []
    except OSError:
        hacker_server.close()
        hacker_list = []


def send_method():
    """
    Sending the information
    """
    global hacker_server
    global hacker_address
    while True:
        with DICTIONARY_SOCKETS_LOCK:
            sockets = list(map(lambda item: item.client_socket, DICTIONARY_SOCKETS.values()))
        if not sockets:
            continue
        rlist, wlist, xlist = select.select([], sockets + hacker_list, [])
        for message_to_send in MESSAGES_TO_SEND:
            if MESSAGES_ACK[message_to_send][0] is Ack.waiting or MESSAGES_ACK[message_to_send][0] is Ack.bad or \
                    MESSAGES_ACK[message_to_send][0] is Ack.ack or MESSAGES_ACK[message_to_send][0] is Ack.transport:
                current_socket, data = MESSAGES_ACK[message_to_send][1]
                print("len data:", len(data))
                if current_socket in wlist:
                    try:
                        for m in create_msg(data):
                            current_socket.sendall(m)

                        if hacker_socket in wlist:
                            hacker_methode_recv(data)
                        if MESSAGES_ACK[message_to_send][0] is Ack.ack or MESSAGES_ACK[message_to_send][0] \
                                is Ack.transport:
                            MESSAGES_ACK.pop(message_to_send)
                        else:
                            MESSAGES_ACK[message_to_send][0] = Ack.send
                    except ConnectionAbortedError:
                        closing_client(current_socket)
                    except ConnectionResetError:
                        try:
                            closing_client(current_socket)
                        except KeyError:
                            pass
                    except OSError as e:
                        if e.__str__() in \
                                "OSError: [WinError 10038] An operation was " \
                                "attempted on something that is not a socket":
                            closing_client(current_socket)
                with MESSAGES_TO_SEND_LOCK:
                    MESSAGES_TO_SEND.remove(message_to_send)


def recv_socket(server_socket):
    global hacker_socket
    global hacker_address
    global hacker_list
    while True:
        with DICTIONARY_SOCKETS_LOCK:
            sockets = list(map(lambda item: item.client_socket, DICTIONARY_SOCKETS.values()))
        rlist, wlist, xlist = select.select(sockets + [server_socket] + [hacker_server], hacker_list, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined!", client_address)
                # Saves the client if the port number the server brought to it
                with DICTIONARY_SOCKETS_LOCK:
                    DICTIONARY_SOCKETS[str(client_address[1])] = SocketsInfo(connection, str(client_address[1]))
            elif current_socket is hacker_server:
                (hacker_socket, hacker_address) = current_socket.accept()
                hacker_list.append(hacker_socket)

            else:
                flag = bool
                data = str
                cmd = ""
                ack = ""
                try:

                    flag, ack, cmd, data = get_msg(current_socket)
                    if hacker_socket in wlist:
                        if data is None:
                            data = ""

                except ConnectionResetError:
                    with DICTIONARY_SOCKETS_LOCK:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))
                except ConnectionAbortedError:
                    with DICTIONARY_SOCKETS_LOCK:
                        DICTIONARY_SOCKETS.pop(find_socket(current_socket))
                except ValueError:
                    print(ack, " ", cmd, " ", data)
                    continue

                if flag:
                    check_cmd(ack, cmd, data, current_socket)
                else:
                    # if client fall by ctrl+page_number
                    if data == "":
                        closing_client(current_socket)
                    else:
                        print(data)
                        with MESSAGES_TO_SEND_LOCK:
                            for m in create_msg(data):
                                MESSAGES_TO_SEND.append((current_socket, m))


if __name__ == "__main__":
    main()
