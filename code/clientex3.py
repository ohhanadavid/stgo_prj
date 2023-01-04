"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""
from enum import Enum
import json
import socket
import sys
import time
import tkinter.filedialog
from tkinter import *

from protocol import *
from stego import *
from protocol import *
import select
import msvcrt
import threading
import tkinter.messagebox as messagebox


class OutputType(Enum):
    receive = "receive"
    sending = "sending"
    sending_e = "sending - e"
    receive_e = "receive - e"
    system_info = "system_info"


msg_input = ""
messages_to_write = []
CONTECT_MENU = dict()
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""


# window_output = Tk()


def send_massage(encode):
    to_input = str(text_input_to.get(1.0, END))
    to_input = [to_input.split(',')]
    msg = str(text_input_massage.get(1.0, END))
    send_to = []
    if encode is OutputType.sending_e:
        path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
        encoded_image = encode_info(time.localtime(), msg, path_image)
        msg = pickle.dumps(encoded_image)
        msg = base64.b64encode(msg)
        msg = "".join([format(n, '08b') for n in msg])
    for i in to_input:
        if i in CONTECT_MENU.keys():
            send_to.append(CONTECT_MENU[i])
        send_to.append(i)

    send_msg = (json.dumps(send_to), "msg", to_input, msg, encode)
    messages_to_write.append(send_msg)
    text_input_to.delete("1.0", END)


def create_group(text_group_name, text_group_people, group_window):
    group_name = str(text_group_name.get(1.0, END))
    if group_name in CONTECT_MENU.keys():
        if not messagebox.askquestion("Info", 'This name already exists, do you want to replace it?'):
            return
    people = str(text_group_people.get(1.0, END)).split(',')
    CONTECT_MENU[group_name] = people
    group_window.destroy()


def open_group():
    group_window = Tk()
    group_window.title("create group")
    text_group_name = Text(group_window, width=20, height=1)
    text_group_people = Text(group_window, width=20, height=30)
    ok_button = Button(group_window, text="OK",
                       command=lambda: create_group(text_group_name, text_group_people, group_window))
    open_group_massage = Label(group_window, text="please enter group name :", width=25, height=1)
    people = Label(group_window, text="please enter contact people spread by , :", width=39, height=1)
    open_group_massage.pack()
    text_group_name.pack()
    people.pack()
    text_group_people.pack()
    ok_button.pack()
    group_window.mainloop()


def input_function(my_socket, start_input):
    print(start_input)
    window.title("MASSAGE")

    text_input_to.insert(END, 'To: ')
    text_input_to.insert(END, start_input)
    text_input_to.insert(END, '\nMassage: ')
    button = Button(text="send", command=lambda: send_massage(my_socket), compound='bottom')
    button.pack()
    text_input_to.pack()


"""
def update_window_output():
    window_output.after(500, update_window_output())
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

"""


def main1(my_socket):
    while True:
        try:

            rlist, wlist, xlist = select.select([my_socket], [my_socket], [])

            if my_socket in rlist:
                text_output.config(state=NORMAL)
                include_length_field, from_how, data = get_msg(my_socket)
                if include_length_field:
                    text_output.insert(END, '\n\r' + from_how + '\n\r', "receive")
                    if data is Image:
                        if "date" in data.info.keys():
                            stego.decode_info(data)
                            text_output.insert(END, '\n\r' + '** ' + data + ' **', "receive - e")
                        text_output.image_create(END, data)
                    else:
                        text_output.insert(END, '\n\r' + data, "receive")
                    text_output.config(state=DISABLED)
                else:
                    try:
                        my_socket.send(create_msg("There is no length field!"))
                        my_socket.recv(1024)
                    except ConnectionAbortedError:
                        return
            for message in messages_to_write:
                send_to, cmd, to_input, data, encrypt = message
                if my_socket in wlist:
                    my_socket.send(create_msg(cmd + send_to + data))
                    if encrypt is OutputType.sending:
                        text_output.insert(END, '\n\r' + to_input + '\n\r' + data, OutputType.sending.value)
                    elif encrypt is OutputType.sending_e:
                        text_output.insert(END, '\n\r' + to_input + '\n\r' + "** " + data + " **",
                                           OutputType.sending_e.value)
                    messages_to_write.remove(message)
                if not window.winfo_exists():
                    print("Closing\n")
                    my_socket.close()
                    return
        except KeyboardInterrupt:
            print("Closing\n")
            my_socket.close()
            return


def get_contect_info():
    pass


def get_names():
    pass


def change_name():
    pass


def add_people():
    pass


def send_image(param):
    pass


def main():
    global window
    global text_input_to
    global text_input_massage
    global text_output
    window = Tk()
    window.title("Chat APP")
    text_input_to = Text(window, width=100, height=1)
    text_input_massage = Text(window, width=100, height=3)
    text_output = Text(window, width=100, height=20)
    # window.geometry("400x400")
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # my_socket.connect(("127.0.0.1", PORT))
    text_output.config(state=DISABLED)
    text_output.tag_config(OutputType.receive.value, foreground="red")
    text_output.tag_config(OutputType.sending.value, foreground="green")
    text_output.tag_config(OutputType.sending_e.value, foreground="blue")
    text_output.tag_config(OutputType.receive_e.value, foreground="#f45d07")
    text_output.tag_config(OutputType.system_info.value, foreground="black")

    label_to = Label(window, text="To:", height=1, width=3, compound="left")
    label_msg = Label(window, text="Massage:", height=1, width=8, compound="left")

    create_group_button = Button(window, text="crate group", command=lambda: open_group(), compound="left")
    my_contest_info_button = Button(window, text="phon book", command=lambda: get_contect_info(), compound="left")
    get_all_names_button = Button(window, text="names by server", command=lambda: get_names(), compound="left")
    my_name_button = Button(window, text="change my name", command=lambda: change_name(), compound="left")
    add_people_button = Button(window, text="add people", command=lambda: add_people(), compound="left")
    send_msg_button = Button(window, text="send", command=lambda: send_massage(False))
    send_encrypt_msg_button = Button(window, text="send encrypt", command=lambda: send_massage(True))
    send_image_button = Button(window, text="send Image", command=lambda: send_image(False))
    send_encrypt_image_button = Button(window, text="send encrypted Image", command=lambda: send_image(True))

    """
        text_output.grid(row=1)
        text_output.grid_size()
        text_input_to.grid(column=1, row=7)
        text_input_massage.grid(column=1, row=8)
        label_to.grid(column=0, row=7)
        label_msg.grid(column=0, row=8)
        create_group_button.grid(column=0, row=0)
        add_people_button.grid(row=0, column=1)
        my_contest_info_button.grid(row=0, column=2)
        get_all_names_button.grid(row=0, column=3)
        my_name_button.grid(row=0, column=4)
        send_msg_button.grid(column=4, row=7)
        send_encrypt_msg_button.grid(column=4, row=8)
        send_image_button.grid(column=4, row=9)
        send_encrypt_image_button.grid(column=4, row=10)
    """
    create_group_button.pack()
    add_people_button.pack()
    my_contest_info_button.pack()
    get_all_names_button.pack()
    my_name_button.pack()
    text_output.pack()
    label_to.pack()
    text_input_to.pack()
    label_msg.pack()
    text_input_massage.pack()
    send_msg_button.pack()
    send_encrypt_msg_button.pack()
    send_image_button.pack()
    send_encrypt_image_button.pack()
    t = threading.Thread(target=main1, args=(my_socket,))
    t.daemon = True
    t.start()
    window.mainloop()


r"""
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

"""
if __name__ == "__main__":
    main()
