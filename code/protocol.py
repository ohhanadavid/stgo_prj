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
import random
import threading
import time
import stego
import hashlib
from PIL import Image

LENGTH_FIELD_SIZE = 9
PORT = 8820
LENGTH_FIELD_SIZE_STR_ERROR = "YOU ENTER MORE THEN " + str(10 ** LENGTH_FIELD_SIZE) + " CHARACTERS"
TYPE_LENGTH = 5
ANS_SERVER = "{'server'}"
EMPTY_DATA = ['\n', '\r', '\b', '\a', '', ' \n', ' \r', ' \b', ' \a']
DATA_DICT = dict()
DATA_DICT_LOCK = threading.Lock()
RECVE_LOCK = threading.Lock()
INTEGRITY_DICT = dict()
INTEGRITY_LOCK = threading.Lock()
MAX_HASH = 64
integrity_ = hashlib.sha3_512
RANDOM_ID = 999999


def create_msg(data):
    """Create a valid protocol message, with length field"""
    if not data.isascii():
        data = "We can only handle what is in the ASCII table "
    if len(data) >= 10 ** LENGTH_FIELD_SIZE:
        return (str.zfill(str(len(LENGTH_FIELD_SIZE_STR_ERROR)),
                          LENGTH_FIELD_SIZE) + LENGTH_FIELD_SIZE_STR_ERROR).encode()
    data = data.encode()
    with INTEGRITY_LOCK:

        integrity_data = integrity_(data).hexdigest().encode()

        id = str.zfill(random.randint(1, RANDOM_ID).__str__(), len(RANDOM_ID.__str__())).encode()
        print(id)
        data = id + b"_msg " + data
        integrity_data = id + b"_hash " + integrity_data
        data = (str.zfill(str(len(data)), LENGTH_FIELD_SIZE)).encode() + data
        integrity_data = (str.zfill(str(len(integrity_data)), LENGTH_FIELD_SIZE)).encode() + integrity_data
    return data, integrity_data


def get_msg(my_socket):
    try:
        count = 0
        """Extract message from protocol, without the length field
           If length field does not include a number, returns False, "Error" """
        with RECVE_LOCK:
            data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
            data = ""
            if data_length.isdigit():
                data_length = int(data_length)
                print("data_length", data_length)
                try:
                    my_socket.setblocking(False)
                    while count < data_length:
                        try:
                            r = ""
                            r = my_socket.recv(data_length)
                            print("r", len(r))
                            data += r.decode()
                            count += len(r)
                        except BlockingIOError as e:
                            print(e)
                            print(len(data))
                    my_socket.setblocking(True)
                except:
                    count = 0
                    data = ""
                    while count < data_length:
                        count += 1048576
                        data += my_socket.recv(1048576).decode()
                finally:
                    integrity = data.split(" ", 1)
                    data = integrity[1]
                    integrity = integrity[0]
                    integrity = integrity.split("_", 1)
                    integrity_type = integrity[1]
                    integrity = integrity[0]
                    with INTEGRITY_LOCK:
                        if integrity in INTEGRITY_DICT.keys():
                            if INTEGRITY_DICT[integrity][0] == "msg":
                                data_save = INTEGRITY_DICT[integrity][1].encode()
                                integrity_data = integrity_(data_save).hexdigest()

                                if integrity_data != data:
                                    return False, None, "ERROR: samone change your msg "
                                data = data_save.decode()
                                INTEGRITY_DICT.pop(integrity)

                            elif INTEGRITY_DICT[integrity][0] == "hash":
                                data_save = INTEGRITY_DICT[integrity][1]
                                integrity_data = integrity_(data).hexdigest()

                                if data_save != integrity_data:
                                    return False, None, "ERROR: samone change your msg "
                                INTEGRITY_DICT.pop(integrity)
                        else:
                            INTEGRITY_DICT[integrity] = (integrity_type, data)
                            return True, "waiting", None

                    """tansaction = tuple(data.split(" ", 2))
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
                    """
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
