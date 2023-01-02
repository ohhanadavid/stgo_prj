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
import pickle
import time
import stego

from PIL import Image

LENGTH_FIELD_SIZE = 9
PORT = 8820
LENGTH_FIELD_SIZE_STR_ERROR = "YOU ENTER MORE THEN " + str(10 ** LENGTH_FIELD_SIZE) + " CHARACTERS"
TYPE_LENGTH = 5


def create_msg(data, type_msg):
    """Create a valid protocol message, with length field"""
    if not data.isascii():
        data = "We can only handle what is in the ASCII table "
    if len(data) >= 10 ** LENGTH_FIELD_SIZE:
        return (str.zfill(str(len(LENGTH_FIELD_SIZE_STR_ERROR)),
                          LENGTH_FIELD_SIZE) + LENGTH_FIELD_SIZE_STR_ERROR).encode()
    if data is str:
        return (str.zfill(str(len(data)), LENGTH_FIELD_SIZE) + str.zfill(type_msg.__name__,
                                                                         TYPE_LENGTH) + data).encode()
    else:
        return (str.zfill(str(len(data)), LENGTH_FIELD_SIZE) + str.zfill(type_msg.__name__,
                                                                         TYPE_LENGTH)).encode() + data


def get_msg(my_socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
    data_type = my_socket.recv(TYPE_LENGTH).decode()
    if data_length.isdigit():
        try:
            if data_type == "str":
                return True, data_type, my_socket.recv(int(data_length)).decode()
            else:
                data = my_socket.recv(int(data_length))
                decoded_b64 = base64.b64decode(data)
                data = pickle.loads(decoded_b64)
                return True, data_type, data

        except:
            count = 0
            data = ""
            while count < data_length:
                count += 1048576
                data += my_socket.recv(1048576)


    else:
        # if client fall by ctrl+c
        if data_length == "":
            return False, ""
        return False, None, "ERROR: This message without length field "
