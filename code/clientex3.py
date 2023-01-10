"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""
import argparse
import math
import tkinter.messagebox as messagebox
import tkinter.scrolledtext
import tkinter.filedialog
from tkinter import *
from PIL import Image, ImageTk
from enum import Enum
import socket
from stego import *
import threading
import rsa
from protocol import *
import select
import json
import time
import sys

import multiprocessing

import msvcrt


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
    error_msg = "error"


def ip_from_user():
    parser = argparse.ArgumentParser(usage="scurety chat app", description="scurety chat app")
    parser.add_argument("-ip", "--ip", type=str, default='127.0.0.1', help="ip you want to connect")
    args = parser.parse_args()
    return args.ip


msg_input = ""
messages_to_write = []
HISTORY = dict()
INDEX = 0
CONTECT_MENU = dict()
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""
BLACK_LIST_SIMBOLD = "[]{}"
text_output_lock = threading.Lock()
massage_list_lock = threading.Lock()
CONNECT_TRYNIG = 10
SENDIN_DICT = dict()


def find_name(name):
    for i in CONTECT_MENU.keys():
        if CONTECT_MENU[i] == name:
            return i
    return None


def call_send_massage(s):
    if not s.is_alive():
        try:

            s.start()
        except RuntimeError as e:
            try:

                s.run()
            except AttributeError as e:

                s = threading.Thread(target=send_massage, args=(OutputType.sending, False))
                s.run()


def call_send_massage_e(se):
    if not se.is_alive():
        try:
            se.start()
        except RuntimeError as e:
            try:

                se.run()
            except AttributeError as e:

                se = threading.Thread(target=send_massage, args=(OutputType.sending_e, False))
                se.run()


def call_send_image(i):
    if not i.is_alive():
        try:

            i.start()
        except RuntimeError as e:
            try:

                i.run()
            except AttributeError as e:

                i = threading.Thread(target=send_massage, args=(OutputType.sending, True))
                i.run()


def call_send_image_e(ie):
    if not ie.is_alive():
        try:

            ie.start()
        except RuntimeError as e:
            try:

                ie.run()
            except AttributeError as e:

                ie = threading.Thread(target=send_massage, args=(OutputType.sending_e, True))
                ie.run()


def send_massage(encode, image):
    msg_e = ""
    to_input = str(text_input_to.get())
    if to_input in EMPTY_DATA:
        label_error.configure(text="must by address!")
        return
    for i in to_input:
        if i in BLACK_LIST_SIMBOLD:
            label_error.configure(text="name contect cant include [,],{,}!")
            return
    label_error.configure(text="")
    if ',' in to_input:
        to_input = set(to_input.split(','))
    else:
        to_input = [to_input]
    msg = ""
    if not image:
        msg = str(text_input_massage.get(1.0, END))
        count = 0
        for i in msg:
            if i in EMPTY_DATA:
                count += 1
            else:
                break
        msg = msg[count:]
        if msg in EMPTY_DATA:
            return
        type_msg = msg.__class__.__name__
    elif image:
        img = tkinter.filedialog.askopenfilename(title="open image to send", filetypes=(("Image files", "*.png"),))
        if img is None or img == "":
            return
        msg = Image.open(img, 'r')
        type_msg = msg.__class__.__name__
        if encode is OutputType.sending_e:
            msg = msg.resize((50, 50))
        msg = pickle.dumps(msg)
        msg = base64.b64encode(msg)
        msg = "".join([format(n, '08b') for n in msg])
        print("len image:", len(msg))
    send_to = set()
    if encode is OutputType.sending_e:
        msg_e = msg
        path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
        if path_image is None or path_image == "":
            return
        encoded_image = encode_info(time.localtime(), msg, path_image)
        type_msg = encoded_image.__class__.__name__
        msg = pickle.dumps(encoded_image)
        msg = base64.b64encode(msg)
        msg = "".join([format(n, '08b') for n in msg])
        print("msg:", len(msg))

    for i in to_input:
        if i in CONTECT_MENU.keys():
            send_to.add(CONTECT_MENU[i])
        send_to.add(i)
    msg = " " + msg
    transaction_id = time.localtime()
    transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
        transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " "
    print("num transaction:", str(math.ceil(len(msg) / 1048576)).zfill(3))

    list_msg = []
    count_msg = 1
    msg = "msg " + str(send_to) + type_msg + " " + msg
    for i in range(0, len(msg), 1048576):
        if i + 1048576 > len(msg):
            list_msg.append(transaction_id + str(count_msg) + " " + msg[i:])
        else:
            list_msg.append(transaction_id + str(count_msg) + " " + msg[i:i + 1048576])
            count_msg += 1
    print("len list", len(list_msg))
    with massage_list_lock:
        SENDIN_DICT[transaction_id] = [math.ceil(len(msg) / 1048576), ""]
        for i in list_msg:

            send_msg = (to_input, i, encode, msg_e)

            SENDIN_DICT[transaction_id][1] += i.split(" ", 2)[2]
                # massage_list_lock.acquire(blocking=False)
            messages_to_write.append(send_msg)
                # massage_list_lock.release()
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


def get_contect_info():
    for item in CONTECT_MENU.items():
        if item[1].__class__ is not set:
            output_insert(END, '\n\r' + item[0] + ': ' + item[1] + ',', OutputType.system_info.value)

        else:
            output_insert(END, '\n\r' + item[0] + ': ', OutputType.system_info.value)

            output_insert(END, '\n'.join(item[1]), OutputType.system_info.value)


def get_names():
    with massage_list_lock:
        msg = "get_names"
        # massage_list_lock.acquire(blocking=False)
        transaction_id = time.localtime()
        transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
            transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " "
        SENDIN_DICT[transaction_id] = [math.ceil(len(msg) / 1048576), msg]
        messages_to_write.append(("", transaction_id + str(1) + " " + msg, OutputType.sending, ""))
        # massage_list_lock.release()


def change_name():
    def change_name_action():
        new_name = str(text_new_name.get())
        for i in new_name:
            if i in BLACK_LIST_SIMBOLD:
                label_error.configure(text="name contect cant include [,],{,}!")
                return
        new_name = "name " + new_name
        transaction_id = time.localtime()
        transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
            transaction_id.tm_sec.real) + "_" + str(math.ceil(len(new_name) / 1048576)).zfill(3) + " "
        send_msg = ("", transaction_id + str(1) + " " + new_name, OutputType.sending, "")
        with massage_list_lock:
            # massage_list_lock.acquire(blocking=False)
            SENDIN_DICT[transaction_id] = [math.ceil(len(new_name) / 1048576), new_name]
            messages_to_write.append(send_msg)
            # massage_list_lock.release()
        new_name_win.destroy()

    new_name_win = Tk()
    label_error = Label(new_name_win)
    new_name_win.title("create name")
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


def getting_msg(data):
    data = data.split(" ", 2)
    sender = data[0]
    type_msg = data[1]
    data = data[2]
    try:
        if type_msg == Image.__name__ or type_msg == "PngImageFile":
            print("len", len(data))
            data = b"".join([bytes(chr(int(data[i:i + 8], 2)), "utf-8") for i in range(0, len(data), 8)])
            decoded_b64 = base64.b64decode(data)
            data = pickle.loads(decoded_b64)
        elif type_msg == str.__name__:
            pass
    except ValueError:
        pass
    except EOFError:
        pass
    if data is Image:
        if "date" in data.info.keys():
            data = stego.decode_info(data)
            if data.__class__ is str:
                output_insert(END, '\n\r' + sender + "say:\n" '** ' + data + ' **', OutputType.receive_e.value)
            else:
                data = PhotoImage(data)
                output_insert(END, '\n\r' + sender + " send:\n", OutputType.receive_e.value)
                output_insert(END, data, "")

        else:
            data = PhotoImage(data)
            output_insert(END, '\n\r' + sender + "send:\n" '** ', OutputType.receive_e.value)
            output_insert(END, data, "")
            output_insert(END, '\n\r' + '** ', OutputType.receive_e.value)
    else:
        output_insert(END, '\n\r' + data, OutputType.receive.value)


def ans(cmd, data):
    if cmd == "msg":
        getting_msg(data)
    elif "ans_all" in cmd:
        data = json.loads(data)
        output = "people in server:" + '\n\r'.join([str(item) for item in data.items()])
        output_insert(END, output, OutputType.server_ans.value)
        for i in data:
            if i not in CONTECT_MENU.values():
                CONTECT_MENU[i] = i
    elif "return_name" in cmd:
        cmd = cmd.split('<', 1)[1].split('>', 1)[0]
        CONTECT_MENU[cmd] = data
        output_insert(END, data, OutputType.server_ans.value)
    elif "ans_error" in cmd:
        output_insert(END, data, OutputType.error_msg.value)
    elif cmd == 'ans_name_':
        output_insert(END, "your name is: " + data, OutputType.server_ans.value)
    elif "ans_success" in cmd:
        output_insert(END, "your name change to: " + data, OutputType.server_ans.value)
    elif "ans_delete" in cmd:
        key = find_name(data)
        if key is not None:
            CONTECT_MENU.pop(key)
            output_insert(END, data + "out from server", OutputType.server_ans.value)
    else:
        return


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
            # massage_list_lock.acquire(blocking=False)
            msg = "get_name " + msg
            transaction_id = time.localtime()
            transaction_id = str(transaction_id.tm_hour.real) + str(transaction_id.tm_min.real) + str(
                transaction_id.tm_sec.real) + "_" + str(math.ceil(len(msg) / 1048576)).zfill(3) + " " + str(1) + " "
            SENDIN_DICT[transaction_id] = [math.ceil(len(msg) / 1048576), msg]
            messages_to_write.append(("", transaction_id + msg, OutputType.sending, ""))
            # massage_list_lock.release()
        get_name_text.destroy()

    get_name_window = Tk()
    label_error = Label(get_name_window)
    get_name_window.title("get name")
    get_name_text = Entry(get_name_window, width=20)
    cmd_send_button = Button(get_name_window, text="send", command=send_name)
    get_name_text.pack()
    cmd_send_button.pack()
    get_name_window.mainloop()


def call_open_group(open_group_thred):
    if not open_group_thred.is_alive():
        try:
            print("a")
            open_group_thred.start()
        except RuntimeError as e:
            try:
                open_group_thred.run()
            except AttributeError as e:

                open_group_thred = threading.Thread(target=open_group)
                open_group_thred.run()


def call_get_contect_info(get_contect_info_thred):
    if not get_contect_info_thred.is_alive():
        try:

            get_contect_info_thred.start()
        except RuntimeError as e:
            try:

                get_contect_info_thred.run()
            except AttributeError as e:

                get_contect_info_thred = threading.Thread(target=get_contect_info())
                get_contect_info_thred.run()


def call_get_names(get_names_thred):
    if not get_names_thred.is_alive():
        try:

            get_names_thred.start()
        except RuntimeError as e:
            try:

                get_names_thred.run()
            except AttributeError as e:

                get_names_thred = threading.Thread(target=get_names())
                get_names_thred.run()


def call_change_name(change_name_thred):
    if not change_name_thred.is_alive():
        try:

            change_name_thred.start()
        except RuntimeError as e:
            try:

                change_name_thred.run()
            except AttributeError as e:

                change_name_thred = threading.Thread(target=change_name())
                change_name_thred.run()


def call_add_people(add_people_thred):
    if not add_people_thred.is_alive():
        try:

            add_people_thred.start()
        except RuntimeError as e:
            try:

                add_people_thred.run()
            except AttributeError as e:

                add_people_thred = threading.Thread(target=add_people())
                add_people_thred.run()


def call_get_name(get_name_thred):
    if not get_name_thred.is_alive():
        try:

            get_name_thred.start()
        except RuntimeError as e:
            try:

                get_name_thred.run()
            except AttributeError as e:

                get_name_thred = threading.Thread(target=get_name())
                get_name_thred.run()


def main():
    global window
    global text_input_to
    global text_input_massage
    global text_output
    global my_socket

    global text_output_lock
    global massage_list_lock
    global label_error

    ip = ip_from_user()
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    my_socket.connect((ip, PORT))

    if text_output_lock.locked():
        text_output_lock.release()
    if massage_list_lock.locked():
        massage_list_lock.release()
    window = Tk()

    window.title("Chat APP")
    text_input_to = Entry(window, width=100)
    text_input_massage = Text(window, width=100, height=3)
    text_output = tkinter.scrolledtext.ScrolledText(window, width=100, height=20)

    text_output.config(state=DISABLED)
    text_output.tag_config(OutputType.receive.value, foreground="#ff6800")
    text_output.tag_config(OutputType.sending.value, foreground="green")
    text_output.tag_config(OutputType.sending_e.value, foreground="blue")
    text_output.tag_config(OutputType.receive_e.value, foreground="#f45d07")
    text_output.tag_config(OutputType.system_info.value, foreground="black")
    text_output.tag_config(OutputType.server_ans.value, foreground="#585858")
    text_output.tag_config(OutputType.error_msg.value, foreground="red")
    label_error = Label(window, foreground="red")
    label_to = Label(window, text="To:", height=1, width=3, compound="left")
    label_msg = Label(window, text="Massage:", height=1, width=8, compound="left")

    client_loop = threading.Thread(target=main1)

    open_group_thred = threading.Thread(target=open_group)
    get_contect_info_thred = threading.Thread(target=get_contect_info)
    get_names_thred = threading.Thread(target=get_names)
    change_name_thred = threading.Thread(target=change_name)
    add_people_thred = threading.Thread(target=add_people)

    send_massage_thred_s = threading.Thread(target=send_massage, args=(OutputType.sending, False))
    send_massage_thred_se = threading.Thread(target=send_massage, args=(OutputType.sending_e, False))
    send_massage_thred_i = threading.Thread(target=send_massage, args=(OutputType.sending, True))
    send_massage_thred_ie = threading.Thread(target=send_massage, args=(OutputType.sending_e, True))

    get_name_thred = threading.Thread(target=get_name)

    create_group_button = Button(window, text="crate group", command=lambda: call_open_group(open_group_thred))
    my_contest_info_button = Button(window, text="phon book",
                                    command=lambda: call_get_contect_info(get_contect_info_thred))
    get_all_names_button = Button(window, text="names by server", command=lambda: call_get_names(get_names_thred))
    my_name_button = Button(window, text="change my name", command=lambda: call_change_name(change_name_thred))
    add_people_button = Button(window, text="add people", command=lambda: call_add_people(add_people_thred))

    send_msg_button = Button(window, text="send", command=lambda: call_send_massage(send_massage_thred_s))

    send_encrypt_msg_button = Button(window, text="send encrypt",
                                     command=lambda: call_send_massage_e(send_massage_thred_se))
    send_image_button = Button(window, text="send Image", command=lambda: call_send_image(send_massage_thred_i))
    send_encrypt_image_button = Button(window, text="send encrypted Image",
                                       command=lambda: call_send_image_e(send_massage_thred_ie))
    get_name_button = Button(window, text="get name", command=lambda: call_get_name(get_name_thred))

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

    open_group_thred.daemon = True
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


def output_insert(start, data, color):
    global INDEX
    with text_output_lock:
        text_output.config(state=NORMAL)
        if data.__class__ is str:
            HISTORY[INDEX] = data
            type_msg = data.split(" ", 1)
            if color == OutputType.sending.value or color == OutputType.sending_e.value:
                address = type_msg[0].split("[", 1)
                if len(address) == 2:
                    address = address[1].split("]", 1)[0]
                    text_output.insert(start, address + '\n', color)
            if len(type_msg) == 1:
                type_msg = ""
            else:
                data = type_msg[1]
                type_msg = type_msg[0]

            # text_output_lock.acquire(blocking=False)
            if "Image" in type_msg:
                try:

                    insert_image(data, start)
                except ValueError:
                    text_output.insert(start, "we cant uplode this file" + '\n', color)
            else:
                HISTORY[INDEX] = data + '\n'
                text_output.insert(start, HISTORY[INDEX], color)

            # text_output_lock.release()
        elif data.__class__ is PhotoImage:

            insert_image(data, start)
        INDEX += 1
        text_output.config(state=DISABLED)


def insert_image(data, start):
    new_size = 100
    data = data.split(" ", 1)[1]
    data = b"".join([bytes(chr(int(data[i:i + 8], 2)), "utf-8") for i in range(0, len(data), 8)])
    decoded_b64 = base64.b64decode(data)
    data = pickle.loads(decoded_b64)
    data = data.resize((int(new_size * (data.size[0] / data.size[1])), int(new_size / (data.size[0] / data.size[1]))))
    HISTORY[INDEX] = ImageTk.PhotoImage(data)
    text_output.image_create(start, image=HISTORY[INDEX])
    text_output.insert(END, '\n')


def main1():
    """co = 0
    while True:
        for i in range(6):
            output_insert(END, str(co) + '\n', "block")
            co += 1
        time.sleep(2)
        text_output.config(state=NORMAL)
        text_output.delete(1.0, END)"""
    while True:
        try:
            rlist, wlist, xlist = select.select([my_socket], [my_socket], [])

            if my_socket in rlist:
                include_length_field, cmd, data = get_msg(my_socket)
                if include_length_field:
                    ans(cmd, data)

                else:
                    try:

                        my_socket.send(create_msg("There is no length field!"))
                        my_socket.recv(1024)
                    except ConnectionAbortedError:
                        for i in range(CONNECT_TRYNIG):
                            try:
                                my_socket.connect(("127.0.0.1", PORT))
                                break
                            except ConnectionResetError:
                                continue
                        output_insert(END, "Closing", OutputType.system_info.value)
                        my_socket.close()
                        return

            for message in messages_to_write:
                to_input, data, encrypt, msg_e = message
                if my_socket in wlist:
                    my_socket.send(create_msg(data))
                    if encrypt is OutputType.sending:
                        out = data.split(" ", 2)
                        if int(out[1]) == SENDIN_DICT[out[0]][0]:
                            output_insert(END, '\n\r' + str(to_input) + '\n\r' + SENDIN_DICT[out[0]][1],
                                          OutputType.sending.value)
                    elif encrypt is OutputType.sending_e:
                        out = data.split(" ", 2)
                        if int(out[1]) == SENDIN_DICT[out[0]][0]:
                            output_insert(END, '\n\r' + str(to_input) + '\n\r' + "** " + SENDIN_DICT[out[0]][0] + " **",
                                          OutputType.sending_e.value)

                    with massage_list_lock:
                        messages_to_write.remove(message)

                        # massage_list_lock.release()
                if not window.winfo_exists():
                    output_insert(END, "Closing", OutputType.system_info.value)
                    print("Closing\n")
                    my_socket.close()
                    return
        except KeyboardInterrupt:
            output_insert(END, "Closing", OutputType.system_info.value)
            print("Closing\n")
            my_socket.close()
            return
        except ConnectionResetError:
            for i in range(CONNECT_TRYNIG):
                try:
                    my_socket.connect(("127.0.0.1", PORT))
                    break
                except ConnectionResetError:
                    continue
                except OSError as er:
                    if er == "OSError: [WinError 10056] A connect request was made on an already connected socket":
                        pass
            output_insert(END, "Closing", OutputType.system_info.value)
            my_socket.close()


if __name__ == "__main__":
    main()
