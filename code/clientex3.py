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
import multiprocessing
from protocol import *
from stego import *
from protocol import *
import select
import msvcrt
import threading
import tkinter.messagebox as messagebox
import rsa


class ContectInfo:
    name = ""
    picther = Image
    public_key = rsa.PublicKey


class OutputType(Enum):
    receive = "receive"
    sending = "sending"
    sending_e = "sending - e"
    receive_e = "receive - e"
    system_info = "system_info"
    server_ans = "server_ans"


msg_input = ""
messages_to_write = []
CONTECT_MENU = dict()
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""
BLACK_LIST_SIMBOLD = "[]{}"
text_output_lock = threading.Lock()
massage_list_lock = threading.Lock()

# window_output = Tk()
def call_send_massage():
    send_massage(OutputType.sending, False)
def call_send_massage_e():
    send_massage(OutputType.sending_e, False)
def call_send_image():
    send_massage(OutputType.sending, True)
def call_send_image_e():
    send_massage(OutputType.sending_e, True)

def send_massage(encode, image):
    to_input = str(text_input_to.get())
    for i in to_input:
        if i in BLACK_LIST_SIMBOLD:
            label_error.configure(text="name contect cant include [,],{,}!")

            return
    label_error.configure(text="")
    if ',' in to_input:
        to_input = {to_input.split(',')}
    else:
        to_input = {to_input}
    msg = ""
    if not image:
        msg = str(text_input_massage.get(1.0, END))
    elif image:
        img = tkinter.filedialog.askopenfilename(title="open image to send", filetypes=(("Image files", "*.png"),))
        msg = Image.open(img, 'r')
    send_to = set()
    if encode is OutputType.sending_e:
        path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
        encoded_image = encode_info(time.localtime(), msg, path_image)
        msg = pickle.dumps(encoded_image)
        msg = base64.b64encode(msg)
        msg = "".join([format(n, '08b') for n in msg])
    for i in to_input:
        if i in CONTECT_MENU.keys():
            send_to.add([CONTECT_MENU[i]])
        send_to.add(i)

    send_msg = (str(send_to), "msg", to_input, msg, encode)
    with massage_list_lock:
        massage_list_lock.acquire(blocking=False)
        messages_to_write.append(send_msg)
        massage_list_lock.release()
    text_input_to.delete(0, END)
    text_input_massage.delete(1.0, END)
    return


def open_group():
    def create_group():
        group_name = str(text_group_name.get())
        for i in group_name:
            if i in BLACK_LIST_SIMBOLD:
                label_error.configure(text="name contect cant include [,],{,}!")
                return
        if group_name in CONTECT_MENU.keys():
            if not messagebox.askquestion("Info", 'This name already exists, do you want to replace it?'):
                return
        peoples = set(str(text_group_people.get(1.0, END)).split(','))
        CONTECT_MENU[group_name] = peoples
        group_window.destroy()

    group_window = Tk()
    label_error = Label(group_window)
    group_window.title("create group")
    text_group_name = Entry(group_window, width=20)
    text_group_people = Text(group_window, width=20, height=30)
    ok_button = Button(group_window, text="OK",
                       command=create_group)
    open_group_massage = Label(group_window, text="please enter group name :", width=25, height=1)
    people = Label(group_window, text="please enter contact people spread by , :", width=39, height=1)
    open_group_massage.pack()
    text_group_name.pack()
    people.pack()
    label_error.pack()
    text_group_people.pack()
    ok_button.pack()
    group_window.mainloop()


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


def main1():
    text_output.configure(state=NORMAL)
    co = 0
    while True:
        for i in range(5):
            text_output.insert(END, str(co) + "\n")
        text_output.delete(1.0, END)
        co += 1

    while True:
        try:

            rlist, wlist, xlist = select.select([my_socket], [my_socket], [])

            if my_socket in rlist:

                text_output.config(state=NORMAL)
                include_length_field, from_how, data = get_msg(my_socket)
                if include_length_field:
                    if from_how == "server":
                        data = data.split
                    with text_output_lock:
                        text_output_lock.acquire(blocking=False)
                        text_output.config(state=NORMAL)
                        text_output.insert(END, '\n\r' + from_how + '\n\r', OutputType.receive.value)
                        text_output.config(state=DISABLED)
                        text_output_lock.release()
                    if data is Image:
                        if "date" in data.info.keys():
                            stego.decode_info(data)
                            with text_output_lock:
                                text_output_lock.acquire(blocking=False)
                                text_output.config(state=NORMAL)
                                text_output.insert(END, '\n\r' + '** ' + data + ' **', OutputType.receive_e.value)
                                text_output.config(state=DISABLED)
                                text_output_lock.release()
                        else:
                            data = PhotoImage(data)
                            with text_output_lock:
                                text_output_lock.acquire(blocking=False)
                                text_output.config(state=NORMAL)
                                text_output.image_create(END, data)
                                text_output.config(state=DISABLED)
                                text_output_lock.release()
                    else:
                        with text_output_lock:
                            text_output_lock.acquire(blocking=False)
                            text_output.config(state=NORMAL)
                            text_output.insert(END, '\n\r' + data, OutputType.receive.value)
                            text_output.config(state=DISABLED)
                            text_output_lock.release()


                else:
                    try:
                        my_socket.send(create_msg("There is no length field!"))
                        my_socket.recv(1024)
                    except ConnectionAbortedError:
                        if text_output_lock.locked():
                            text_output.config(state=DISABLED)
                            text_output_lock.release()
                        return

            for message in messages_to_write:
                send_to, cmd, to_input, data, encrypt = message
                if my_socket in wlist:
                    my_socket.send(create_msg(cmd + send_to + data))
                    with text_output_lock:
                        text_output_lock.acquire(blocking=False)
                        text_output.config(state=NORMAL)
                        if encrypt is OutputType.sending:
                            text_output.insert(END, '\n\r' + to_input + '\n\r' + data, OutputType.sending.value)
                        elif encrypt is OutputType.sending_e:
                            text_output.insert(END, '\n\r' + to_input + '\n\r' + "** " + data + " **",
                                               OutputType.sending_e.value)
                        text_output.config(state=DISABLED)
                        text_output_lock.release()
                    with massage_list_lock:
                        massage_list_lock.acquire(blocking=False)
                        messages_to_write.remove(message)
                        massage_list_lock.release()
                if not window.winfo_exists():
                    print("Closing\n")
                    my_socket.close()
                    return
        except KeyboardInterrupt:
            print("Closing\n")
            my_socket.close()
            return


def get_contect_info():
    for item in CONTECT_MENU.items():
        if item[1] is not list:
            with text_output_lock:
                text_output_lock.acquire(blocking=False)
                text_output.config(state=NORMAL)
                text_output.insert(END, '\n\r' + item[0] + ': ' + item[1] + ',', OutputType.system_info.value)
                text_output.config(state=DISABLED)
                text_output_lock.release()
        else:
            with text_output_lock:
                text_output_lock.acquire(blocking=False)
                text_output.config(state=NORMAL)
                text_output.insert(END, '\n\r' + item[0] + ': ', OutputType.system_info.value)
                text_output.config(state=DISABLED)
                text_output_lock.release()
            c = ""
            for k in range(len(item[0] + 2)):
                c += " "
            with text_output_lock:
                text_output_lock.acquire(blocking=False)
                text_output.config(state=NORMAL)
                text_output.insert(END, (',\n' + c).join(item[1]), OutputType.system_info.value)
                text_output.config(state=DISABLED)
                text_output_lock.release()


def get_names():
    with massage_list_lock:
        massage_list_lock.acquire(blocking=False)
        messages_to_write.append(("", "get_names", "", "", OutputType.sending))
        massage_list_lock.release()


def change_name():
    def change_name_action():
        new_name = str(text_new_name.get())
        for i in new_name:
            if i in BLACK_LIST_SIMBOLD:
                label_error.configure(text="name contect cant include [,],{,}!")
                return
        send_msg = ("", "name ", "", new_name, OutputType.sending)
        with massage_list_lock:
            massage_list_lock.acquire(blocking=False)
            messages_to_write.append(send_msg)
            massage_list_lock.release()
        new_name_win.destroy()

    new_name_win = Tk()
    label_error = Label(new_name_win)
    new_name_win.title("create group")
    text_new_name = Entry(new_name_win, width=20)
    ok_button = Button(new_name_win, text="OK", command=change_name_action)
    new_name_massage = Label(new_name_win, text="please enter new  name :", width=25, height=1)
    new_name_massage.pack()
    text_new_name.pack()
    label_error.pack()

    ok_button.pack()
    new_name_win.mainloop()


def add_people():
    def create_people():
        name = str(text__name.get())
        for i in name:
            if i in BLACK_LIST_SIMBOLD:
                label_error.configure(text="name contect cant include [,],{,}!")
                return
        if name in CONTECT_MENU.keys():
            if not messagebox.askquestion("Info", 'This name already exists, do you want to replace it?'):
                return
        person = str(text__people.get())
        CONTECT_MENU[name] = person
        add_window.destroy()

    add_window = Tk()
    label_error = Label(add_window)
    add_window.title("create new phone")
    text__name = Entry(add_window, width=20)
    text__people = Entry(add_window, width=20)
    ok_button = Button(add_window, text="OK", command=create_people)
    open_group_massage = Label(add_window, text="please enter  name :", width=25, height=1)
    people = Label(add_window, text="please enter contact know by server:", width=39, height=1)
    open_group_massage.pack()
    text__name.pack()
    people.pack()
    text__people.pack()
    ok_button.pack()
    add_window.mainloop()


def get_name():
    def send_name():
        msg = get_name_text.get()
        for i in msg:
            if i in BLACK_LIST_SIMBOLD:
                label_error.configure(text="name contect cant include [,],{,}!")
                return
        if msg in CONTECT_MENU.keys():
            msg = CONTECT_MENU[msg]
        with massage_list_lock:
            massage_list_lock.acquire(blocking=False)
            messages_to_write.append(("", "get_name", "", msg, OutputType.sending))
            massage_list_lock.release()
        get_name_text.destroy()

    get_name_window = Tk()
    label_error = Label(get_name_window)
    get_name_window.title("get name")
    get_name_text = Entry(get_name_window, width=10)
    cmd_send_button = Button(get_name_window, text="send", command=send_name)
    get_name_text.pack()
    cmd_send_button.pack()
    get_name_window.mainloop()


def main():
    global window
    global text_input_to
    global text_input_massage
    global text_output
    global my_socket
    global open_group_thred
    global get_contect_info_thred
    global get_names_thred
    global change_name_thred
    global add_people_thred
    global send_massage_thred_s
    global send_massage_thred_se
    global send_massage_thred_i
    global send_massage_thred_ie
    global get_name_thred
    global text_output_lock
    global massage_list_lock
    global label_error

    if text_output_lock.locked():
        text_output_lock.release()
    if massage_list_lock.locked():
        massage_list_lock.release()
    window = Tk()
    window.title("Chat APP")
    text_input_to = Entry(window, width=100)
    text_input_massage = Text(window, width=100, height=3)
    text_output = Text(window, width=100, height=20)
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # my_socket.connect(("127.0.0.1", PORT))
    text_output.config(state=DISABLED)
    text_output.tag_config(OutputType.receive.value, foreground="red")
    text_output.tag_config(OutputType.sending.value, foreground="green")
    text_output.tag_config(OutputType.sending_e.value, foreground="blue")
    text_output.tag_config(OutputType.receive_e.value, foreground="#f45d07")
    text_output.tag_config(OutputType.system_info.value, foreground="black")
    text_output.tag_config(OutputType.server_ans.value, foreground="#585858")
    label_error = Label(window)

    label_to = Label(window, text="To:", height=1, width=3, compound="left")
    label_msg = Label(window, text="Massage:", height=1, width=8, compound="left")

    client_loop = threading.Thread(target=main1)
    open_group_thred = threading.Thread(target=open_group)
    get_contect_info_thred = threading.Thread(target=get_contect_info)
    get_names_thred = threading.Thread(target=get_names)
    change_name_thred = threading.Thread(target=change_name)
    add_people_thred = threading.Thread(target=add_people)

    send_massage_thred_s = threading.Thread(target=call_send_massage)
    send_massage_thred_se = threading.Thread(target=call_send_massage_e)
    send_massage_thred_i = threading.Thread(target=call_send_image)
    send_massage_thred_ie = threading.Thread(target=call_send_image_e)

    get_name_thred = threading.Thread(target=get_name)



    create_group_button = Button(window, text="crate group", command=lambda: open_group_thred.run())
    my_contest_info_button = Button(window, text="phon book", command=lambda: get_contect_info_thred.run(),
                                    compound="left")
    get_all_names_button = Button(window, text="names by server", command=lambda: get_names_thred.run(),
                                  compound="left")
    my_name_button = Button(window, text="change my name", command=lambda: change_name_thred.run())
    add_people_button = Button(window, text="add people", command=lambda: add_people_thred.run())

    send_msg_button = Button(window, text="send", command=lambda: send_massage_thred_s.run())

    send_encrypt_msg_button = Button(window, text="send encrypt", command=lambda: send_massage_thred_se.run())
    send_image_button = Button(window, text="send Image", command=lambda: send_massage_thred_i.run())
    send_encrypt_image_button = Button(window, text="send encrypted Image",
                                       command=lambda: send_massage_thred_ie.run())
    get_name_button = Button(window, text="get name", command=lambda: get_name_thred.run())

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
    get_name_button.pack()
    my_name_button.pack()
    text_output.pack()
    label_to.pack()
    text_input_to.pack()
    label_error.pack()
    label_msg.pack()
    text_input_massage.pack()
    send_msg_button.pack()
    send_encrypt_msg_button.pack()
    send_image_button.pack()
    send_encrypt_image_button.pack()

    # open_group_thred.daemon = True
    get_contect_info_thred.daemon = True
    get_names_thred.daemon = True
    change_name_thred.daemon = True
    add_people_thred.daemon = True
    send_massage_thred_s.daemon = True
    send_massage_thred_se.daemon = True
    send_massage_thred_i.daemon = True
    send_massage_thred_ie.daemon = True
    get_name_thred.daemon = True
    client_loop.daemon = True

    client_loop.start()
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

"""
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
