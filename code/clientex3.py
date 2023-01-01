"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""

import socket
import sys

from protocol import *
import select
import msvcrt


def main():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect(("127.0.0.1", PORT))
        sel = [my_socket]
        messages_to_write = []
        print("enter commend")
        user_input = ""
        while True:

            rlist, wlist, xlist = select.select(sel, sel, [])
            if msvcrt.kbhit():
                ch = msvcrt.getche().decode()
                if ch == "\b":
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
                if ch == '\r':
                    messages_to_write.append((my_socket, user_input))
                    user_input = ""
                    print('\n', flush=True, end="")
                else:
                    user_input += ch
            if my_socket in rlist:
                include_length_field, data = get_msg(my_socket)
                if include_length_field:
                    print("server sent:\n"+data)
                else:
                    try:
                        my_socket.send(create_msg("There is no length field!"))
                        my_socket.recv(1024)
                    except ConnectionAbortedError:
                        return
            for message in messages_to_write:
                current_socket, data = message
                if current_socket in wlist:
                    current_socket.send(create_msg(data))
                    messages_to_write.remove(message)
                if data in ['EXIT', 'exit']:
                    print("Closing\n")
                    my_socket.close()
                    return
    except KeyboardInterrupt:
        print("Closing\n")
        my_socket.close()
        return


if __name__ == "__main__":
    main()
