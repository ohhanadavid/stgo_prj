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
import time
import stego

from PIL import Image

LENGTH_FIELD_SIZE = 9
PORT = 8820
LENGTH_FIELD_SIZE_STR_ERROR = "YOU ENTER MORE THEN " + str(10 ** LENGTH_FIELD_SIZE) + " CHARACTERS"
TYPE_LENGTH = 5
ANS_SERVER = "{'server'}"


def create_msg(data):
    """Create a valid protocol message, with length field"""
    if not data.isascii():
        data = "We can only handle what is in the ASCII table "
    if len(data) >= 10 ** LENGTH_FIELD_SIZE:
        return (str.zfill(str(len(LENGTH_FIELD_SIZE_STR_ERROR)),
                          LENGTH_FIELD_SIZE) + LENGTH_FIELD_SIZE_STR_ERROR).encode()
    return (str.zfill(str(len(data)), LENGTH_FIELD_SIZE) + data).encode()


def get_msg(my_socket):
    """Extract message from protocol, without the length field
       If length field does not include a number, returns False, "Error" """
    data_length = my_socket.recv(LENGTH_FIELD_SIZE).decode()
    data = ""
    if data_length.isdigit():
        try:
            data = my_socket.recv(int(data_length)).decode()
        except:
            count = 0
            data = ""
            while count < data_length:
                count += 1048576
                data += my_socket.recv(1048576).decode()
        finally:
            cmd_get = data.split(" ", 1)
            if len(cmd_get) == 1:
                return True, cmd_get[0], ""
            else:
                return True, cmd_get[0], cmd_get[1]
            """cmd = cmd_get[0]
            data = cmd_get[1].split('}', 1)
            if len(data) > 1:
                to_msg = data[0] + '}'
                msg = data[1]
                to_msg = eval(to_msg)
            else:
                data = data[0]
                if data == ANS_SERVER:
                    to_msg = ANS_SERVER
                    data = ""
                else:
                    to_msg = ""
                msg = ""
            
            return True, cmd, to_msg, msg"""

    else:
        # if client fall by ctrl+c
        if data_length == "":
            return False, None, "", "ERROR: This message without length field "
        return False, None, None, "ERROR: This message without length field "
