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
import tkinter.messagebox as messagebox

msg_input = ""

CONTECT_MENU = dict()
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""

window_input = Tk()
window_output = Tk()

text_input = Text(window_input)
text_output = Text(window_output)


def update_window_input():
    window_input.after(500,update_window_input)

def update_window_output():
    window_output.after(500, update_window_output())

def end_input(my_socket):
    msg_input = str(text_input.get(1.0, END))
    msg = msg_input.split("'\n", 1)
    contact = msg[0][3:]
    massage = msg[1][8:]
    if contact in CONTECT_MENU.keys():
        send_msg = CONTECT_MENU[contact] + massage
    else:
        my_socket.send("get_names")

    text_input.delete("1.0", END)


def open_group():
    open_group_massage = "please enter group name :"
    people = "\nplease enter contact people spread by , :"
    text_input.delete("1.0", END)
    text_input.insert(END, open_group_massage)
    text_input.insert(END, people)
    data = str(text_input.get(1.0, END)).split('\n')
    group_name = data[0][len(open_group_massage):]
    if group_name in CONTECT_MENU.keys():
        if not messagebox.showinfo("Info", '\nThis name already exists, do you want to replace it?'):
            return
    CONTECT_MENU[group_name] = data[1][len(people):].split(',')


def input_function(my_socket, start_input, return_input=""):
    print(start_input)
    window_input.title("MASSAGE")

    text_input.insert(END, 'To: ')
    text_input.insert(END, start_input)
    text_input.insert(END, '\nMassage: ')
    button = Button(text="send", command=lambda: end_input(my_socket), compound='bottom')
    button.pack()
    text_input.pack()
    window_input.after(500, update_window_input)
    window_input.mainloop()


def update_output_massage(text, my_socket):
    rlist, wlist, xlist = select.select([my_socket], [], [])
    if my_socket in rlist:
        include_length_field, data = get_msg(my_socket)
        if include_length_field:
            text.insert(END, '\n' + data)
        else:
            try:
                my_socket.send(create_msg("There is no length field!"))
                my_socket.recv(1024)
            except ConnectionAbortedError:
                return


def output_function(window_output, my_socket):
    window_output.title("MASSAGE")
    text = Text(window_output)
    text.pack()
    window_output.after(500, update_window_output())
    window_output.mainloop()


def main():
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.connect(("127.0.0.1", PORT))
        sel = [my_socket]
        messages_to_write = []
        print("enter commend")
        user_input = ""
        ch = ""

        while True:

            rlist, wlist, xlist = select.select(sel, sel, [])

            if msvcrt.kbhit() and not window_input.winfo_exists():
                while msvcrt.kbhit():
                    ch += msvcrt.getche().decode()
                input_thread = threading.Thread(
                    input_function(my_socket, ch, "commend input", user_input))
                input_thread.start()

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
