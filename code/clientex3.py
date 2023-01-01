"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""

import socket
import sys
from tkinter import *
from protocol import *
import select
import msvcrt
import threading


def end_input(text_box, end_input):
    end_input = str(text_box.get(1.0, END))
    print(end_input)
    text_box.clipboard_clear()


def input_function(f, start_input, titel, return_input=""):
    print(start_input)
    f = "False"
    window_input = Tk()
    window_input.title(titel)
    text = Text(window_input)
    text.insert(END, start_input)
    button = Button(text="cmd", command=lambda: end_input(text, return_input))
    button.pack()
    text.pack()
    window_input.mainloop()
    f = "True"


def main():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect(("127.0.0.1", PORT))
        sel = [my_socket]
        messages_to_write = []
        print("enter commend")
        user_input = ""
        ch = ""
        input_window = "True"
        while True:

            rlist, wlist, xlist = select.select(sel, sel, [])

            if msvcrt.kbhit() and input_window == "True":
                while msvcrt.kbhit():
                    ch += msvcrt.getche().decode()
                input_thred=threading.Thread(input_function(input_window,ch,"commend input",user_input))
                input_thred.start()

            if my_socket in rlist:
                include_length_field, data = get_msg(my_socket)
                if include_length_field:
                    print("server sent:\n" + data)
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
