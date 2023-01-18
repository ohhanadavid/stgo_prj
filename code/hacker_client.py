"""EX 2.6 client implementation
   Author:David Ohhana
   Date:06.11.2022
   Possible client commands defined in protocol.py
"""
import argparse
import json
import socket
import tkinter.filedialog
import tkinter.scrolledtext
from tkinter import *

import select
from PIL import ImageTk
from PIL.BmpImagePlugin import BmpImageFile
from PIL.IcoImagePlugin import IcoImageFile
from PIL.JpegImagePlugin import JpegImageFile
from PIL.PngImagePlugin import PngImageFile
from PIL.TiffImagePlugin import TiffImageFile

from protocol import *
from stego import *


class ContactInfo:
    name = ""


class OutputType(Enum):
    receive = "receive"
    sending = "sending"
    sending_e = "sending - e"
    receive_e = "receive - e"
    system_info = "system_info"
    server_ans = "server_ans"
    error_msg = "error"


def ip_from_user():
    parser = argparse.ArgumentParser(usage="security chat app", description="security chat app")
    parser.add_argument("-ip", "--ip", type=str, default='127.0.0.1', help="ip you want to connect")
    args = parser.parse_args()
    return args.ip


ip = ip_from_user()
my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
msg_input = ""
messages_to_write = []
HISTORY = dict()
INDEX = 0
SERVER_RESPONSE = ""
TYPE_SERVER_RESPONSE = ""
BLACK_LIST_SYMBOLS = "[]{}"
text_output_lock = threading.Lock()
massage_list_lock = threading.Lock()
CONNECT_TRYING = 10
EMPTY_DATA = ['\n', '\r', '\b', '\a', '', ' \n', ' \r', ' \b', ' \a', " "]
IMAGE_TYPE = [JpegImageFile.__name__, PngImageFile.__name__, GifImageFile.__name__, BmpImageFile.__name__,
              TiffImageFile.__name__, IcoImageFile.__name__, PhotoImage.__class__.__name__]


def getting_msg(ack, data=""):
    """
    The function receives the message and distributes it to the sender and the message.
    The function then checks the message for its type and handles it accordingly, and prints the received message
    :param ack:Receives the ACK number to return an ACK message that a package has been received
    :param data:The information that came from the server
    """
    # Distribution to sender and message and type message
    data = data.split(" ", 2)
    sender = data[0]
    # Checking if the sender is in contacts
    # The message type str,image,file type
    type_msg = data[1]
    # the message
    data = data[2]
    encrypt = False
    count = 0
    try:
        # Cleaning the message from empty parts that came with it
        for i in range(len(data)):
            if data[i] in EMPTY_DATA:
                count += 1
                continue
            else:
                break
        data = data[count:]

        try:
            if type_msg == Image.__name__ or type_msg in IMAGE_TYPE:
                # If the message is a GIF
                if type_msg == GifImageFile.__name__:
                    # If the content arrived as a string and not as bytes
                    if data.__class__ is not bytes:
                        data = data.encode('latin-1')
                    # Opening as a gif
                    data = Image.open(io.BytesIO(data))
                    data.save("received gif.gif ", format="gif", save_all=True)
                else:
                    # png, jpeg
                    print("len", len(data))
                    data_ = b"".join([bytes(chr(int(data[i:i + 8], 2)), "utf-8") for i in range(0, len(data), 8)])
                    decoded_b64 = base64.b64decode(data_)
                    data_ = pickle.loads(decoded_b64)
                    data = data_
        # If a gif file arrived and was not caught at first
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

        # Checking if it is encrypted information

        if data.__class__ is str:
            # Checking if it is a string or a file
            data = data.split('>', 1)
            if len(data) == 2:
                data[0] = data[0][1:]
                try:
                    # If it is a file save it
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
        # Print the message

        if data.__class__ is str:
            output_insert(END, "msg str " + '\n\r' + sender + '\n\r' + data, OutputType.receive.value)

        else:
            output_insert(END, "msg str " + '\n\r' + sender + " send:\n", OutputType.receive_e.value)
            output_insert(END, data, "")


    except:
        pass


def ans(cmd, data, ack):
    if cmd == "msg":
        getting_msg(ack, data)
    elif "ans_all" in cmd:
        data = json.loads(data)
        output = "people in server:" + '\n\r'.join([str(item) for item in data.items()])
        output_insert(END, output, OutputType.server_ans.value)
    elif "return_name" in ack:
        ack = cmd
        output_insert(END, "return_name " + ack, OutputType.server_ans.value, True, True)
    elif "ans_error" in cmd:
        output_insert(END, data, OutputType.error_msg.value)
    elif cmd == 'ans_name_':
        output_insert(END, "your name is: " + data, OutputType.server_ans.value, True, True)
    elif "ans_success" in cmd:
        output_insert(END, "your name change" + data, OutputType.server_ans.value, True, True)
    else:
        try:
            output_insert(END, ack + " " + cmd + " " + data, OutputType.server_ans.value)
        except:
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
                    output = output[0][:-1] + output[1][1:]
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
                    ans(cmd, data, ack)

                else:
                    try:
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

        except KeyboardInterrupt:
            output_insert(END, "Closing", OutputType.system_info.value)
            print("Closing\n")
            my_socket.close()
            return
        except ConnectionResetError:
            conction_fail()
        except ValueError as e:
            if e.__str__() == "ValueError: file descriptor cannot be a negative integer (-1)":
                conction_fail()


def conction_fail():
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

    my_socket.connect((ip, 5))

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

    scrollerbar_window = Scrollbar(frame, orient=VERTICAL, command=canvas_window.yview)
    scrollerbar_window.pack(side=RIGHT, fill=Y)

    canvas_window.configure(yscrollcommand=scrollerbar_window.set)
    canvas_window.bind('<Configure>', lambda e: canvas_window.configure(scrollregion=canvas_window.bbox("all")))

    frame2 = Frame(canvas_window)
    canvas_window.create_window((0, 0), window=frame2, anchor="nw")

    window.title("its sniffing time!!")

    text_output = tkinter.scrolledtext.ScrolledText(frame2, width=100, height=20)

    text_output.config(state=DISABLED)
    text_output.tag_config(OutputType.receive.value, foreground="#ff6800")
    text_output.tag_config(OutputType.sending.value, foreground="green")
    text_output.tag_config(OutputType.sending_e.value, foreground="blue")
    text_output.tag_config(OutputType.receive_e.value, foreground="#f45d07")
    text_output.tag_config(OutputType.system_info.value, foreground="black")
    text_output.tag_config(OutputType.server_ans.value, foreground="#585858")
    text_output.tag_config(OutputType.error_msg.value, foreground="red")

    client_loop = threading.Thread(target=main1)

    text_output.pack()

    client_loop.daemon = True

    client_loop.start()
    window.mainloop()


if __name__ == "__main__":
    main()
