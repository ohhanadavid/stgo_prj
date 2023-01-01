"""EX 2.6 protocol implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands:
   NUMBER - server should reply with a random number, 0-99
   HELLO - server should reply with the server's name, anything you want
   TIME - server should reply with time and date
   EXIT - server should send acknowledge and quit
"""

LENGTH_FIELD_SIZE = 9
PORT = 8820
LENGTH_FIELD_SIZE_STR_ERROR = "YOU ENTER MORE THEN " + str(10 ** LENGTH_FIELD_SIZE) + " CHARACTERS"


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
    if data_length.isdigit():
        return True, my_socket.recv(int(data_length)).decode()
    else:
        # if client fall by ctrl+c
        if data_length == "":
            return False, ""
        return False, "ERROR: This message without length field "
