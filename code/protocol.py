"""EX 2.6 protocol implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands:
   NUMBER - server should reply with a random number, 0-99
   HELLO - server should reply with the server's name, anything you want
   TIME - server should reply with time and date
   EXIT - server should send acknowledge and quit
"""
import base64
import json
import pickle
import threading
import time
import stego

from PIL import Image

LENGTH_FIELD_SIZE = 9
PORT = 8820
LENGTH_FIELD_SIZE_STR_ERROR = "YOU ENTER MORE THEN " + str(10 ** LENGTH_FIELD_SIZE) + " CHARACTERS"
TYPE_LENGTH = 5
ANS_SERVER = "{'server'}"
EMPTY_DATA = ['\n', '\r', '\b', '\a', '', ' \n', ' \r', ' \b', ' \a']
DATA_DICT = dict()
DATA_DICT_LOCK = threading.Lock()


def create_msg(data):
    """Create a valid protocol message, with length field"""
    if not data.isascii():
        data = "We can only handle what is in the ASCII table "
    if len(data) >= 10 ** LENGTH_FIELD_SIZE:
        return (str.zfill(str(len(LENGTH_FIELD_SIZE_STR_ERROR)),
                          LENGTH_FIELD_SIZE) + LENGTH_FIELD_SIZE_STR_ERROR).encode()
    return (str.zfill(str(len(data)), LENGTH_FIELD_SIZE) + data).encode()


def get_msg(my_socket):
    try:
        my_socket.setblocking(False)
        """Extract message from protocol, without the length field
           If length field does not include a number, returns False, "Error" """
        data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
        data = ""
        if data_length.isdigit():
            data_length = int(data_length)
            try:
                while True:
                    r = my_socket.recv(data_length)
                    data += r.decode()
            except BlockingIOError:
                pass
            except:
                count = 0
                data = ""
                while count < data_length:
                    count += 1048576
                    data += my_socket.recv(1048576).decode()
            finally:
                tansaction = tuple(data.split(" ", 2))
                transaction, count, data = tansaction
                count = int(count)
                with DATA_DICT_LOCK:
                    if transaction in DATA_DICT.keys():

                        DATA_DICT[transaction][1][count] = data
                    else:
                        limit = int(transaction[-3:])

                        DATA_DICT[transaction] = [limit, dict()]
                        DATA_DICT[transaction][1][count] = data

                if len(DATA_DICT[transaction][1]) == DATA_DICT[transaction][0]:
                    print("len(DATA_DICT[transaction][1]):", len(DATA_DICT[transaction][1]))
                    print("DATA_DICT[transaction][0]:", DATA_DICT[transaction][0])
                    data = ""
                    with DATA_DICT_LOCK:
                        for i in range(DATA_DICT[transaction][0]):
                            data += DATA_DICT[transaction][1][i + 1]
                        DATA_DICT.pop(transaction)
                else:
                    return True, "waiting", ""

                cmd_get = data.split(" ", 1)
                if len(cmd_get) == 1:
                    return True, cmd_get[0], ""
                else:
                    return True, cmd_get[0], cmd_get[1]


        else:
            # if client fall by ctrl+c
            if data_length == "":
                return False, None, "ERROR: This message without length field "
            return False, None, "ERROR: This message without length field "
    except ConnectionAbortedError:
        return False, None, "ERROR: This message without length field "
