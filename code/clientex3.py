"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""
import argparse
import json
import os.path
import socket
import tkinter.filedialog
import tkinter.messagebox as messagebox
import tkinter.scrolledtext
from tkinter import *

import select
from PIL import ImageTk
from PIL.BmpImagePlugin import BmpImageFile
from PIL.IcoImagePlugin import IcoImageFile
from PIL.JpegImagePlugin import JpegImageFile
from PIL.PngImagePlugin import PngImageFile
from PIL.TiffImagePlugin import TiffImageFile

import stego
from protocol import *
from stego import *


class ContactInfo:
    name = ""

    def __init__(self, name=""):
        self.name = name

    def __str__(self):
        return self.name


class OutputType(Enum):
    receive = "receive"
    sending = "sending"
    sending_e = "sending - e"
    receive_e = "receive - e"
    system_info = "system_info"
    server_ans = "server_ans"
    error_msg = "error"


def ip_from_user():
    parser = argparse.ArgumentParser(usage="Security chat app", description="Security chat app")
    parser.add_argument("-ip", "--ip", type=str, default='127.0.0.1', help="ip you want to connect")
    args = parser.parse_args()
    return args.ip


ip = ip_from_user()
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg_input = ""
messages_to_write = []
messages_ack = dict()
HISTORY = dict()
INDEX = 0
CONTACT_MENU = dict()
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""
BLACK_LIST_SYMBOLS = "[]{}"
text_output_lock = threading.Lock()
massage_list_lock = threading.Lock()
CONNECT_TRYING = 10
SENDING_DICT = dict()
EMPTY_DATA = ['\n', '\r', '\b', '\a', '', ' \n', ' \r', ' \b', ' \a', " "]
IMAGE_TYPE = [JpegImageFile.__name__, PngImageFile.__name__, GifImageFile.__name__, BmpImageFile.__name__,
              TiffImageFile.__name__, IcoImageFile.__name__, PhotoImage.__class__.__name__]


def find_name(name):
    for i in CONTACT_MENU.keys():
        if CONTACT_MENU[i].name == name:
            return i
    return None


def get_name():
    def send_name():
        msg = get_name_text.get()
        for i in msg:
            if i in BLACK_LIST_SYMBOLS:
                label_error.configure(text="name contact cant include [,],{,}!")
                return
        if msg in CONTACT_MENU.keys():
            msg = CONTACT_MENU[msg]
        with massage_list_lock:
            ack_number = str(random.randint(100000, 999999))
            # massage_list_lock.acquire(blocking=False)
            msg = " get_name " + msg
            messages_ack[ack_number] = [Ack.waiting, ("", msg, OutputType.sending, "")]
            messages_to_write.append(ack_number)
            # massage_list_lock.release()
        get_name_window.destroy()

    get_name_window = Tk()
    label_error = Label(get_name_window)
    get_name_window.title("get name")
    get_name_text = Entry(get_name_window, width=20)
    cmd_send_button = Button(get_name_window, text="send", command=send_name)
    get_name_text.pack()
    cmd_send_button.pack()
    get_name_window.mainloop()


def send_massage(encode, image, ather_file=False):
    msg_e = ""
    to_input = str(text_input_to.get())
    if to_input in EMPTY_DATA:
        label_error.configure(text="must by address!")
        return
    for i in to_input:
        if i in BLACK_LIST_SYMBOLS:
            label_error.configure(text="name contact cant include [,],{,}!")
            return
    label_error.configure(text="")
    if ',' in to_input:
        to_input = set(to_input.split(','))
    else:
        to_input = [to_input]
    msg = ""
    if not image and not ather_file:
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
        img = tkinter.filedialog.askopenfilename(title="open image to send", filetypes=(
            ("Image files", "*.png"), ("Image files", "*.jpg"), ("Image files", "*.jpeg"), ("Gif", '*.gif')))
        if img is None or img == "":
            return
        msg = Image.open(img, 'r')
        type_msg = msg.__class__.__name__
        if encode is OutputType.sending_e:
            msg = msg.resize((50, 50))
        if msg.__class__ is GifImageFile:
            msg = not_encoded_gif(msg)
            buffer = io.BytesIO()
            msg.save(buffer, save_all=True, format="gif")
            msg = buffer.getvalue()
        else:
            msg = pickle.dumps(msg)
            msg = base64.b64encode(msg)
            msg = "".join([format(n, '08b') for n in msg])
        print("len image:", len(msg))
    elif ather_file:
        file_path = tkinter.filedialog.askopenfilename(title="open image to send", filetypes=(("files", "*.*"),))
        if os.path.isfile(file_path):

            file_ = open(file_path, 'rb').read().decode('latin-1')
            if file_ == '' or file_ == " ":
                file_ = open(file_path, 'r').read()

            type_msg = file_path.split('.')[-1]
            msg = "<" + type_msg + '>' + file_
            msg_e = file_path.split(r'//')[-1] + " send"
    send_to = set()
    if encode is OutputType.sending_e:
        if ather_file:
            msg_e = "msg " + str(send_to) + type_msg + " " + file_path.split(r'\\')[-1]
            msg = '<' + type_msg + '>' + msg
        elif image:
            msg_e = "msg " + str(send_to) + type_msg + " " + msg
        else:
            msg_e = "msg " + str(send_to) + "str" + " " + msg
            msg = "<str>" + msg
        path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(
            ("Image files", "*.png"), ("Image files", "*.jpg"), ("Image files", "*.jpeg"), ("Gif", '*.gif')))
        if path_image is None or path_image == "":
            return
        encoded_image = encode_info(time.localtime(), msg, path_image)
        if encoded_image.__class__ is GifImageFile:
            type_msg = GifImageFile.__name__
            buffer = io.BytesIO()
            encoded_image.save(buffer, format="gif", save_all=True)
            msg = buffer.getvalue().decode('latin-1')
        else:
            type_msg = encoded_image.__class__.__name__
            msg = pickle.dumps(encoded_image)
            msg = base64.b64encode(msg)
            msg = "".join([format(n, '08b') for n in msg])
        print("msg-e:", len(msg))

    for i in to_input:
        if i in CONTACT_MENU.keys():
            contact = CONTACT_MENU[i]
            if contact.__class__ is set:
                for k in contact:
                    send_to.add(k)
            else:
                send_to.add(contact)
        else:
            send_to.add(i)
    if msg.__class__ is bytes:
        msg = msg.decode('latin-1')

    msg = " " + msg
    ack_number = str(random.randint(100000, 999999))
    msg = ack_number + " msg " + str(send_to) + type_msg + " " + msg
    send_msg = (to_input, msg, encode, msg_e)

    with massage_list_lock:
        messages_to_write.append(ack_number)
        messages_ack[ack_number] = [Ack.waiting, send_msg]
    # massage_list_lock.release()
    text_input_to.delete(0, END)
    text_input_massage.delete(1.0, END)
    return


def get_names():
    with massage_list_lock:
        ack_number = str(random.randint(100000, 999999))
        msg = " get_names"
        messages_ack[ack_number] = [Ack.waiting, ("", msg, OutputType.sending, "")]
        messages_to_write.append(ack_number)


def change_name():
    def change_name_action():
        new_name = str(text_new_name.get())
        for i in new_name:
            if i in BLACK_LIST_SYMBOLS:
                label_error.configure(text="name contact cant include [,],{,}!")
                return
        new_name = " name " + new_name

        with massage_list_lock:

            ack_number = str(random.randint(100000, 999999))

            send_msg = ("", new_name, OutputType.sending, "")
            messages_ack[ack_number] = [Ack.waiting, send_msg]
            messages_to_write.append(ack_number)

        new_name_win.destroy()

    new_name_win = Tk()
    label_error = Label(new_name_win)
    new_name_win.title("create name")
    text_new_name = Entry(new_name_win, width=20)

    ok_button = Button(new_name_win, text="OK", command=lambda: change_name_action())
    new_name_massage = Label(new_name_win, text="please enter new  name :", width=25, height=1)
    new_name_massage.pack()
    text_new_name.pack()
    label_error.pack()

    ok_button.pack()
    new_name_win.mainloop()


def open_group():
    def create_group():
        group_name = str(text_group_name.get())
        for i in group_name:
            if i in BLACK_LIST_SYMBOLS:
                label_error.configure(text="name contact cant include [,],{,}!")
                return
        if group_name in CONTACT_MENU.keys():
            if not messagebox.askquestion("Info", 'This name already exists, do you want to replace it?'):
                return
        peoples = set()
        for i in text_group_people.curselection():
            peoples.add(text_group_people.get(i))
        CONTACT_MENU[group_name] = peoples
        group_window.destroy()

    group_window = Tk()
    label_error = Label(group_window)
    group_window.title("create group")
    frame_group = Frame(group_window, width=20, height=30)

    text_group_name = Entry(group_window, width=20)
    text_group_people = Listbox(frame_group, selectmode=MULTIPLE)

    scrollbar = Scrollbar(frame_group, orient="vertical")
    scrollbar.config(command=text_group_people.yview)
    text_group_people.config(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    text_group_people.pack()

    for i in CONTACT_MENU.keys():
        text_group_people.insert(END, i)

    ok_button = Button(group_window, text="OK", command=create_group)
    open_group_massage = Label(group_window, text="please enter group name :", width=25, height=1)
    people = Label(group_window, text="please enter contact people spread by , :", width=39, height=1)
    open_group_massage.pack()
    text_group_name.pack()
    people.pack()
    label_error.pack()
    frame_group.pack()
    # text_group_people.pack()
    ok_button.pack()
    group_window.mainloop()


def get_contact_info():
    output_insert_system(END, '\n\rPhon BOOK:', OutputType.system_info.value)
    for item in CONTACT_MENU.items():
        if item[1].__class__ is not set:
            output_insert_system(END, '\n\r' + item[0] + ': ' + item[1] + ',', OutputType.system_info.value)

        else:
            output_insert_system(END, '\n\rgroup-' + item[0] + ': \n', OutputType.system_info.value)

            output_insert_system(END, '\n'.join(item[1]), OutputType.system_info.value)


def add_people():
    def create_people():
        name = str(text__name.get())
        for i in name:
            if i in BLACK_LIST_SYMBOLS:
                label_error.configure(text="name contact cant include [,],{,}!")
                return
        if name in CONTACT_MENU.keys():
            if not messagebox.askquestion("Info", 'This name already exists, do you want to replace it?'):
                return
        person = str(text__people_by_server.get())
        if person in CONTACT_MENU.values():
            key = find_name(person)
            CONTACT_MENU.pop(key)
        CONTACT_MENU[name] = person

        add_window.destroy()

    add_window = Tk()
    label_error = Label(add_window)
    add_window.title("create new phone")
    text__name = Entry(add_window, width=20)
    text__people_by_server = Entry(add_window, width=20)
    ok_button = Button(add_window, text="OK", command=create_people)
    open_group_massage = Label(add_window, text="please enter  name :", width=25, height=1)
    people = Label(add_window, text="please enter contact know by server:", width=39, height=1)
    open_group_massage.pack()
    text__name.pack()
    people.pack()
    text__people_by_server.pack()
    ok_button.pack()
    add_window.mainloop()


def getting_msg(ack, data=""):
    data = data.split(" ", 2)
    sender = data[0]
    for i in CONTACT_MENU.items():
        if i[1] == sender:
            sender = i[0]

    type_msg = data[1]
    data = data[2]
    encrypt = False
    count = 0
    if True:

        for i in range(len(data)):
            if data[i] in EMPTY_DATA:
                count += 1
                continue
            else:
                break
        data = data[count:]
        try:
            if type_msg == Image.__name__ or type_msg in IMAGE_TYPE:
                if type_msg == GifImageFile.__name__:
                    if data.__class__ is not bytes:
                        data = data.encode('latin-1')
                    data = Image.open(io.BytesIO(data))
                else:
                    print("len", len(data))
                    data_ = b"".join([bytes(chr(int(data[i:i + 8], 2)), "utf-8") for i in range(0, len(data), 8)])
                    decoded_b64 = base64.b64decode(data_)
                    data_ = pickle.loads(decoded_b64)
                    data = data_

        except pickle.PickleError as e:
            print(e)
            if data.__class__ is not bytes:
                data = data.encode('latin-1')
            data = Image.open(io.BytesIO(data))
        except ValueError as e:
            print(e)
            if data.__class__ is not bytes:
                data = data.encode('latin-1')
            data = Image.open(io.BytesIO(data))
        except EOFError as e:
            print(e)

        if data.__class__ is Image or data.__class__.__name__ in IMAGE_TYPE:
            encode_flag = False
            if data.__class__ is GifImageFile:
                encode = decode_info(data)
                if encode is not None:
                    data = encode
                    encrypt = True
                    encode_flag = True
            if hasattr(data, "info") or encode_flag:
                if hasattr(data, "info") and "date" in data.info.keys():
                    data = stego.decode_info(data)
                    encrypt = True
        elif data.__class__ is str:
            data = data.split('>', 1)
            if len(data) == 2:
                data[0] = data[0][1:]
                try:
                    if data[0] != 'str':
                        data_ = data[1].encode('latin-1')
                        path = tkinter.filedialog.asksaveasfilename(title="save as",
                                                                    filetypes=((data[0], "*." + data[0]),))
                        if path == "":
                            path = PATH + r'\\' + str(random.randint(0, 1000000)) + '.' + data[0]
                        file = open(path, 'wb')
                        file.write(data_)
                        file.close()
                        data = path.split(r"\\")[-1] + " save"
                    else:
                        data = data[1]
                except:
                    print("send function error 430")
                    pass
            else:
                data = data[0]

        if encrypt:
            if data.__class__ is str:
                output_insert(END, "msg str " + '\n\r' + sender + " say:\n" '**\n ' + data + ' **',
                              OutputType.receive_e.value, sender + " say:\n")
            else:
                output_insert(END, "msg str " + '\n\r' + sender + " send:\n**\n", OutputType.receive_e.value)
                output_insert(END, data, "")
        else:
            if data.__class__ is str:
                output_insert(END, "msg str " + '\n\r' + sender + '\n\r' + data, OutputType.receive.value)

            else:
                output_insert(END, "msg str " + '\n\r' + sender + " send:\n", OutputType.receive_e.value)
                output_insert(END, data, "")

        with massage_list_lock:

            messages_to_write.append("ACk" + ack)
            messages_ack["ACk" + ack] = [Ack.ack,
                                         [sender, ack + " " + "ack" + " " + sender, OutputType.sending.value, ""]]
    # except:
    #    with massage_list_lock:
    #        messages_to_write.append("ACk" + ack)
    #        messages_ack["ACk" + ack] = [Ack.ack, ack + " " + "ack_bad" + " " + sender]


def ack_methode(ack, cmd):
    if cmd == "ack":
        try:
            messages_ack.pop(ack)
            messages_to_write.remove(ack)
        except KeyError:
            return
        except ValueError as e:
            print(e)
            return
    elif "ack_bad" in cmd:
        try:
            messages_to_write.append(ack)
            messages_ack[ack][0] = Ack.bad
        except KeyError:
            return


def ans(ack, cmd, data):
    if cmd == "msg":
        getting_msg(ack, data)
    elif "ans_all" in cmd:
        data = json.loads(data)
        output = "people in server:" + '\n\r'.join([str(item) for item in data.items()])
        output_insert(END, output, OutputType.server_ans.value)
        for i in data:
            if i not in CONTACT_MENU.values():
                CONTACT_MENU[i] = i
    elif "return_name" in ack:
        c = ack
        ack = cmd
        cmd = c
        cmd = cmd.split('<', 1)[1].split('>', 1)[0]
        CONTACT_MENU[cmd] = data
        output_insert(END, "return_name " + ack, OutputType.server_ans.value, True, True)
    elif "ans_error" in cmd:
        output_insert(END, data, OutputType.error_msg.value)
    elif cmd == 'ans_name_':
        output_insert(END, "your name is: " + data, OutputType.server_ans.value, True, True)
    elif "ans_success" in cmd:
        output_insert(END, "your name change" + data, OutputType.server_ans.value, True, True)

    elif "ack" in cmd:
        ack_methode(ack, cmd)
    elif "ans_delete" in cmd:
        key = find_name(data)
        if key is not None:
            CONTACT_MENU.pop(key)
            output_insert(END, data + "out from server", OutputType.server_ans.value)
    else:
        return


def output_insert_system(start, data, color):
    global INDEX

    with text_output_lock:
        text_output.config(state=NORMAL)
        HISTORY[INDEX] = data

        text_output.insert(start, HISTORY[INDEX], color)

        INDEX += 1
        text_output.config(state=DISABLED)


def output_insert(start, data, color, receive=True, full_data=False, sender=""):
    global INDEX
    with text_output_lock:
        text_output.config(state=NORMAL)
        if not receive:
            data = data.split(" ", 1)
            msg_commend = data[0]
            data = data[1]

        if full_data:
            HISTORY[INDEX] = data + '\n'
            text_output.insert(start, HISTORY[INDEX], color)
            return
        if data.__class__ is str:
            HISTORY[INDEX] = data
            type_msg = data.split(" ", 2)
            if color == OutputType.sending.value or color == OutputType.sending_e.value:
                address = type_msg[0].split("[", 1)
                if 'msg' in address:
                    address = msg_commend.split("[", 1)
                if len(address) == 2:
                    address = address[1].split("]", 1)[0]
                    text_output.insert(start, address + '\n', color)
            if len(type_msg) == 1:
                type_msg = ""
            else:
                if len(type_msg) == 3:
                    data = type_msg[2]
                    type_msg = type_msg[1]
                    type_msg = type_msg.split('}', 1)
                    if len(type_msg) == 2:
                        type_msg = type_msg[1]
                else:
                    if type_msg[1] in EMPTY_DATA:
                        data = type_msg[0]
                    else:
                        data = type_msg[1]
                    type_msg = type_msg[0]

            if type_msg in IMAGE_TYPE:
                try:
                    insert_image(data, start)
                except ValueError:
                    text_output.insert(start, "we cant up-lode this file" + '\n', color)
            else:
                output = data.split("str", 1)
                if len(output) == 2:
                    output = output[0][:-1]+output[1][1:]
                else:
                    output = output[0]
                if sender != "":
                    output = sender + output
                HISTORY[INDEX] = output + '\n'
                text_output.insert(start, HISTORY[INDEX], color)

        elif data.__class__.__name__ in IMAGE_TYPE or data.__class__ is ImageTk.PhotoImage:

            insert_image(data, start)
        INDEX += 1
        text_output.config(state=DISABLED)


def insert_image(data, start):
    new_size = 100
    if data.__class__ is str:
        i = 0
        for i in range(len(data)):
            if data[i] in EMPTY_DATA:
                continue
            else:
                break
        data = data[i:]
        try:
            byte_data = b"".join([bytes(chr(int(data[i:i + 8], 2)), "utf-8") for i in range(0, len(data), 8)])
            decoded_b64 = base64.b64decode(byte_data)
            byte_data = pickle.loads(decoded_b64)
            data = byte_data
        except ValueError:
            if data.__class__ is not bytes:
                data = data.encode('latin-1')
            data = Image.open(io.BytesIO(data))
        except pickle.UnpicklingError:
            if data.__class__ is not bytes:
                data.encode('latin-1')
            data = Image.open(io.BytesIO(data))
    if hasattr(data, "resize"):
        size = (int(new_size * (data.size[0] / data.size[1])), int(new_size / (data.size[0] / data.size[1])))
        data = data.resize(size)
        HISTORY[INDEX] = ImageTk.PhotoImage(data)
    elif hasattr(data, 'config'):
        if hasattr(data.config, 'width') and hasattr(data.config, 'height'):
            data.config(width=int(new_size * (data.size[0] / data.size[1])),
                        height=int(new_size / (data.size[0] / data.size[1])))
            HISTORY[INDEX] = ImageTk.PhotoImage(data)
    elif data.__class__ is not ImageTk.PhotoImage.__class__:
        HISTORY[INDEX] = ImageTk.PhotoImage(data)
    else:
        HISTORY[INDEX] = data

    text_output.image_create(start, image=HISTORY[INDEX])
    text_output.insert(END, '\n')


def main1():
    while True:
        try:

            rlist, wlist, xlist = select.select([my_socket], [my_socket], [])

            if my_socket in rlist:
                include_length_field, ack, cmd, data = get_msg(my_socket)
                if include_length_field:
                    if data is not None:
                        print("len data r:", len(data))
                    ans(ack, cmd, data)

                else:
                    try:
                        for m in create_msg("There is no length field!"):
                            my_socket.send(m)
                        my_socket.recv(1024)
                    except ConnectionAbortedError:
                        for i in range(CONNECT_TRYING):
                            try:
                                my_socket.connect(("127.0.0.1", PORT))
                                break
                            except ConnectionResetError:
                                continue
                        output_insert(END, "Closing", OutputType.system_info.value)
                        my_socket.close()
                        return

            for message in messages_to_write:
                try:
                    w_msg = messages_ack[message]
                except KeyError:
                    messages_to_write.remove(message)
                    continue
                if w_msg[0] is Ack.bad or w_msg[0] is Ack.waiting or \
                        w_msg[0] is Ack.ack or w_msg[0] is Ack.server:
                    to_input, data, encrypt, msg_e = w_msg[1]
                    if my_socket in wlist:
                        print("len data:", len(data))
                        for m in create_msg(data):
                            if m == ERROR:
                                output_insert(END, '\n\r' + m + data,
                                              OutputType.error_msg.value, False)
                            print("len a:", len(m))
                            my_socket.send(m)

                        if encrypt is OutputType.sending:
                            if msg_e != "":
                                data = msg_e
                            output_insert(END, '\n\r' + str(to_input) + '\n\r' + data,
                                          OutputType.sending.value, False)
                        elif encrypt is OutputType.sending_e:

                            output_insert(END, '\n\r' + str(to_input) + '\n\r' + "** " + msg_e
                                          + " **", OutputType.sending_e.value, False)

                        with massage_list_lock:
                            messages_to_write.remove(message)
                            print("massage to with", messages_to_write)
                            if messages_ack[message][0] is Ack.ack or w_msg[0] is Ack.server:
                                messages_ack.pop(message)
                            else:
                                messages_ack[message][0] = Ack.send

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
            connection_fail()
        except ValueError as e:
            if e.__str__() == "ValueError: file descriptor cannot be a negative integer (-1)":
                connection_fail()
            else:
                print(e)


def connection_fail():
    for i in range(CONNECT_TRYING):
        try:
            time.sleep(3)
            my_socket.connect(("127.0.0.1", PORT))
            break
        except ConnectionResetError:
            continue
        except OSError as er:
            if er == "OSError: [WinError 10056] A connect request was made on an already connected socket":
                pass

            output_insert(END, "Closing", OutputType.system_info.value)
            my_socket.close()


def main():
    global window
    global text_input_to
    global text_input_massage
    global text_output
    global my_socket
    global text_output_lock
    global massage_list_lock
    global label_error

    my_socket.connect((ip, PORT))

    if text_output_lock.locked():
        text_output_lock.release()
    if massage_list_lock.locked():
        massage_list_lock.release()
    window = Tk()
    window.geometry('840x550')
    frame = Frame(window)
    frame.pack(fill=BOTH, expand=1)

    canvas_window = Canvas(frame)
    canvas_window.pack(side=LEFT, fill=BOTH, expand=1)

    scrollbar_window = Scrollbar(frame, orient=VERTICAL, command=canvas_window.yview)
    scrollbar_window.pack(side=RIGHT, fill=Y)

    canvas_window.configure(yscrollcommand=scrollbar_window.set)
    canvas_window.bind('<Configure>', lambda e: canvas_window.configure(scrollregion=canvas_window.bbox("all")))

    frame2 = Frame(canvas_window)
    canvas_window.create_window((0, 0), window=frame2, anchor="nw")

    window.title("Chat APP")

    text_input_to = Entry(frame2, width=100)
    text_input_massage = Text(frame2, width=100, height=3)
    text_output = tkinter.scrolledtext.ScrolledText(frame2, width=100, height=20)

    text_output.config(state=DISABLED)
    text_output.tag_config(OutputType.receive.value, foreground="#ff6800")
    text_output.tag_config(OutputType.sending.value, foreground="green")
    text_output.tag_config(OutputType.sending_e.value, foreground="blue")
    text_output.tag_config(OutputType.receive_e.value, foreground="#f45d07")
    text_output.tag_config(OutputType.system_info.value, foreground="black")
    text_output.tag_config(OutputType.server_ans.value, foreground="#585858")
    text_output.tag_config(OutputType.error_msg.value, foreground="red")
    label_error = Label(frame2, foreground="red")
    label_to = Label(frame2, text="To:", height=1, width=3, compound="left")
    label_msg = Label(frame2, text="Massage:", height=1, width=8, compound="left")

    client_loop = threading.Thread(target=main1)

    open_group_thread = threading.Thread(target=open_group)
    get_content_info_thread = threading.Thread(target=get_contact_info)
    get_names_thread = threading.Thread(target=get_names)
    change_name_thread = threading.Thread(target=change_name)
    add_people_thread = threading.Thread(target=add_people)

    send_massage_thread_s = threading.Thread(target=send_massage, args=(OutputType.sending, False))
    send_massage_thread_se = threading.Thread(target=send_massage, args=(OutputType.sending_e, False))
    send_massage_thread_i = threading.Thread(target=send_massage, args=(OutputType.sending, True))
    send_massage_thread_ie = threading.Thread(target=send_massage, args=(OutputType.sending_e, True))
    send_massage_thread_f = threading.Thread(target=send_massage, args=(OutputType.sending, False, True))
    send_massage_thread_fe = threading.Thread(target=send_massage, args=(OutputType.sending_e, False, True))

    get_name_thread = threading.Thread(target=get_name)

    create_group_button = Button(frame2, text="crate group", command=lambda: call_open_group(open_group_thread))
    my_contest_info_button = Button(frame2, text="phon book",
                                    command=lambda: call_get_contact_info(get_content_info_thread))
    get_all_names_button = Button(frame2, text="names by server", command=lambda: call_get_names(get_names_thread))
    my_name_button = Button(frame2, text="change my name", command=lambda: call_change_name(change_name_thread))
    add_people_button = Button(frame2, text="add people", command=lambda: call_add_people(add_people_thread))

    send_msg_button = Button(frame2, text="send", command=lambda: call_send_massage(send_massage_thread_s))

    send_encrypt_msg_button = Button(frame2, text="send encrypt",
                                     command=lambda: call_send_massage_e(send_massage_thread_se))
    send_image_button = Button(frame2, text="send Image", command=lambda: call_send_image(send_massage_thread_i))

    send_file_button = Button(frame2, text="send file", command=lambda: call_send_file(send_massage_thread_f))
    send_encrypt_file_button = Button(frame2, text="send file encrypt",
                                      command=lambda: call_send_file_e(send_massage_thread_fe))

    send_encrypt_image_button = Button(frame2, text="send encrypted Image",
                                       command=lambda: call_send_image_e(send_massage_thread_ie))
    get_name_button = Button(frame2, text="get name", command=lambda: call_get_name(get_name_thread))

    create_group_button.grid(row=0, column=0)
    add_people_button.grid(row=0, column=1)
    my_contest_info_button.grid(row=0, column=2)
    get_all_names_button.grid(row=0, column=3)
    get_name_button.grid(row=0, column=4)
    my_name_button.grid(row=0, column=5)
    text_output.grid(row=1, column=0, columnspan=6)

    label_to.grid(row=2, column=0, columnspan=6)
    text_input_to.grid(row=3, column=0, columnspan=6)
    label_error.grid(row=4, column=0, columnspan=6)
    label_msg.grid(row=5, column=0, columnspan=6)
    text_input_massage.grid(row=6, column=0, columnspan=6)
    send_msg_button.grid(row=7, column=1)
    send_encrypt_msg_button.grid(row=7, column=2)
    send_image_button.grid(row=7, column=3)
    send_encrypt_image_button.grid(row=7, column=4)
    send_file_button.grid(row=8, column=3)
    send_encrypt_file_button.grid(row=8, column=4)
    open_group_thread.daemon = True
    get_content_info_thread.daemon = True
    get_names_thread.daemon = True
    change_name_thread.daemon = True
    add_people_thread.daemon = True
    send_massage_thread_s.daemon = True
    send_massage_thread_se.daemon = True
    send_massage_thread_i.daemon = True
    send_massage_thread_ie.daemon = True
    get_name_thread.daemon = True
    client_loop.daemon = True

    client_loop.start()
    window.mainloop()


def call_open_group(open_group_thread):
    if not open_group_thread.is_alive():
        try:
            print("a")
            open_group_thread.start()
        except RuntimeError as e:
            try:
                open_group_thread.run()
            except AttributeError as e:

                open_group_thread = threading.Thread(target=open_group)
                open_group_thread.run()


def call_get_contact_info(get_contact_info_thread):
    if not get_contact_info_thread.is_alive():
        try:

            get_contact_info_thread.start()
        except RuntimeError as e:
            try:

                get_contact_info_thread.run()
            except AttributeError as e:

                get_contact_info_thread = threading.Thread(target=get_contact_info())
                get_contact_info_thread.run()


def call_get_names(get_names_thread):
    if not get_names_thread.is_alive():
        try:

            get_names_thread.start()
        except RuntimeError as e:
            try:

                get_names_thread.run()
            except AttributeError as e:

                get_names_thread = threading.Thread(target=get_names())
                get_names_thread.run()


def call_change_name(change_name_thread):
    if not change_name_thread.is_alive():
        try:

            change_name_thread.start()
        except RuntimeError as e:
            try:

                change_name_thread.run()
            except AttributeError as e:

                change_name_thread = threading.Thread(target=change_name())
                change_name_thread.run()


def call_add_people(add_people_thread):
    if not add_people_thread.is_alive():
        try:

            add_people_thread.start()
        except RuntimeError as e:
            try:

                add_people_thread.run()
            except AttributeError as e:

                add_people_thread = threading.Thread(target=add_people())
                add_people_thread.run()


def call_get_name(get_name_thread):
    if not get_name_thread.is_alive():
        try:

            get_name_thread.start()
        except RuntimeError as e:
            try:

                get_name_thread.run()
            except AttributeError as e:

                get_name_thread = threading.Thread(target=get_name())
                get_name_thread.run()


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


def call_send_file(ie):
    if not ie.is_alive():
        try:

            ie.start()
        except RuntimeError as e:
            try:

                ie.run()
            except AttributeError as e:

                ie = threading.Thread(target=send_massage, args=(OutputType.sending, False, True))
                ie.run()


def call_send_file_e(ie):
    if not ie.is_alive():
        try:

            ie.start()
        except RuntimeError as e:
            try:

                ie.run()
            except AttributeError as e:

                ie = threading.Thread(target=send_massage, args=(OutputType.sending_e, False, True))
                ie.run()


if __name__ == "__main__":
    main()
