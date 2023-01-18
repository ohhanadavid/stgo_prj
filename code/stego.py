# importing required modules
import base64
import binascii
import io
import math
import os
import pickle
import random
import tkinter.filedialog
from math import *

import PyPDF2
from PIL import Image, ImageSequence
from PIL.GifImagePlugin import GifImageFile


class EndOfWord:
    end_word = False
    end_data = False

    def __init__(self, end__word=False, end_of_data=False):
        self.end_word = end__word
        self.end_data = end_of_data


PATH = os.path.dirname(os.path.realpath(__file__))

slash= r'\\'
def not_encoded_gif(gif):
    """
    Set the gif as unencrypted
    :param gif:
    :return:
    """
    try:
        # create a buffer to store the modified gif
        buffer = io.BytesIO()
        with gif as new_img:
            # create a dictionary to store each frame of the gif
            pixel_dict = dict()
            # copy all frames of the gif into a list
            frames = [frame.copy() for frame in ImageSequence.Iterator(new_img)]
            # store each frame in the dictionary with its index as the key
            for i, frame in enumerate(frames):
                pixel_dict[i] = frame
            # get the pixels of the first frame
            pix_encode = pixel_dict[0].load()
            # get the value of the first pixel
            pixel = pix_encode[0, 0]
            # check if the pixel value is an integer
            if pixel.__class__ is int:
                if pixel % 2 == 0:
                    if pixel == 0:
                        pixel += 1
                    else:
                        pixel -= 1
            # check if the pixel value is a tuple or list
            if pixel.__class__ is tuple or pixel.__class__ is list:
                for i in pixel[:3]:
                    if pixel % 2 == 0:
                        if pixel == 0:
                            pixel += 1
                        else:
                            pixel -= 1
            # set the modified pixel value
            pix_encode[0, 0] = pixel
            # save the modified gif using the buffer
            frames[0].save(buffer, format="gif", save_all=True, append_images=frames[1:])
            gif_image = buffer.getvalue()
            return Image.open(io.BytesIO(gif_image))
    except:
        return gif


def find_path(dir_in_path):
    files = os.walk(PATH + slash + dir_in_path)
    file_l = list(files)[0][-1]
    file_l.sort()
    return file_l


def prime(n):
    # All prime numbers are odd except two
    if n & 1:
        n -= 2
    else:
        n -= 1

    i, j = 0, 3

    for i in range(n, 2, -2):

        if i % 2 == 0:
            continue

        while j <= floor(sqrt(i)) + 1:
            if i % j == 0:
                break
            j += 2

        if j > floor(sqrt(i)):
            return i

    # It will only be executed when n is 3
    return 2


def encode_enc(new_img, data_list, len_data, codex, prime_h, prime_m):
    """
    Encrypting the information inside an image
    :param new_img:
    :param data_list:
    :param len_data:
    :param codex:
    :param prime_h:
    :param prime_m:
    :return:
    """
    # Get the width and height of the image
    w = new_img.size[0]
    h = new_img.size[1]
    # Convert the image to RGB mode if it is not already in that mode
    if new_img.mode != 'RGB':
        new_img = new_img.convert("RGB")
    # Initialize an empty list to keep track of the pixels that have been modified
    list_pix = []
    # Create iterator objects for the data and codex lists
    data = iter(data_list)
    c = iter(codex)
    # Initialize a count to keep track of how many bits have been added to the pixel
    count = 0
    # Initialize a flag to indicate whether to get the next key
    next_key = True
    # Iterate through the data
    for i in range(len_data):
        # Iterate through the RGB values of the pixel
        for k in range(3):
            if next_key:
                try:
                    # Get the next two items from the codex list
                    key1 = c.__next__()
                    key2 = c.__next__()
                    # Reset the flag
                    next_key = False
                except StopIteration as e:
                    print(e)
                    next_key = False
                # Get the ASCII values of the keys
                key1 = ord(key1)
                key2 = ord(key2)

            end = EndOfWord
            if count + 3 < 8:
                if count >= 3:
                    xy = key1 + key2
                else:
                    xy = key2 * key1
                # Get the next three items from the data list
                se = data.__next__() + data.__next__() + data.__next__()
                end.end_data = False
                end.end_word = False
                count += 3
            else:
                xy = key2 - key1
                se = data.__next__() + data.__next__()
                if i == len_data - 1:
                    end.end_data = True
                else:
                    end.end_data = False
                    end.end_word = True
                count = 0

            x = int((xy * prime_h) % w)
            y = int((xy * prime_m) % h)
            salt = 1
            # Check if the pixel has already been modified
            while (x, y) in list_pix:
                x = int((x + prime_h * salt) % w)
                y = int((y + prime_m + salt) % h)
                salt += 1
            if x < 0:
                x *= -1
            if y < 0:
                y *= -1
            list_pix.append((x, y))
            # Get the pixel and modify it
            pixel = new_img.getpixel((x, y))[:3]
            pixel = mod_pix(pixel, se, end)
            new_img.putpixel((x, y), pixel)
    print(list_pix)
    return new_img


def mod_pix(pixel, data, end):
    """
    Encrypting the information inside the pixel
    :param pixel:
    :param data:
    :param end:
    :return:
    """
    # Extracting 3 pixels at a time
    pix = list(pixel)
    # Pixel value should be made
    # odd for 1 and even for 0
    for j in range(len(data)):

        if data[j] == '0' and pix[j] % 2 != 0:
            pix[j] -= 1

        elif data[j] == '1' and pix[j] % 2 == 0:
            if pix[j] != 0:
                pix[j] -= 1

            else:
                pix[j] += 1

    if end.end_data is True:
        if pix[-1] % 2 == 0:
            if pix[-1] != 0:
                pix[-1] -= 1

            else:
                pix[-1] += 1

    elif end.end_word is True:
        if pix[-1] % 2 != 0:
            pix[-1] -= 1

    # truncate the modified list to its first 3 elements
    pix = tuple(pix[0:3])
    return pix


# Encode data into image
def encode_enc_gif(new_img, data_list, len_data, codex, prime_h, prime_m, frame_len, t):
    """
    The function receives the gif, and the keys and information and encrypts them inside the gif
    :param new_img:the gif
    :param data_list: The information is in binary
    :param len_data:The number of bytes
    :param codex:The encryption key
    :param prime_h:hourly encryption parameter
    :param prime_m:Encryption parameter by minutes
    :param frame_len:the number of frames
    :param t:the key
    :return:
    """
    # Setting the key
    key = (str.zfill(str(t.tm_sec.real), 2) + str.zfill(str(t.tm_min.real), 2) + str.zfill(str(t.tm_hour.real),
                                                                                           2)).encode('latin-1')
    len_key = len(key) * 3
    a = "".join([format(n, '08b') for n in key])
    print("e=", a)
    key = iter(a)
    w = new_img.size[0]
    h = new_img.size[1]
    list_pix = []
    data = iter(data_list)
    c = iter(codex)

    key_list = []
    buffer = io.BytesIO()

    with new_img as new_img:
        frames = [frame.copy() for frame in ImageSequence.Iterator(new_img)]
        pixel_dict = dict()
        end = EndOfWord
        count = 0
        # Convert the gif to an array
        for i, frame in enumerate(frames):
            pixel_dict[i] = frame
        pix_encode = pixel_dict[0].load()
        pixel = pix_encode[0, 0]
        # Set gif as an encoder
        if pixel.__class__ is int:
            if pixel % 2 != 0:
                pixel -= 1
        if pixel.__class__ is tuple or pixel.__class__ is list:
            for i in pixel[:3]:
                if i % 2 != 0:
                    i -= 1
        pix_encode[0, 0] = pixel
        pixel_dict[0] = pix_encode
        pixels = pixel_dict[1].load()
        # Encrypt the key
        for i in range(len_key):
            if count + 3 < 8:
                se = key.__next__() + key.__next__() + key.__next__()
                end.end_data = False
                end.end_word = False
                count += 3

            else:
                se = key.__next__() + key.__next__()

                if i == len_key - 1:
                    end.end_data = True
                else:
                    end.end_data = False
                    end.end_word = True

                count = 0
            list_pix.append((1, i, 1))
            pixel = pixels[1, i]
            pixels[1, i] = mod_pix(pixel, se, end)
            key_list.append(pixels[1, i])

        r = len(list_pix)

        print(i)
        # If you choose a new key
        change_key = True
        # Encrypting the information
        for i in range(len_data):
            for k in range(3):
                # Key selection
                if change_key:
                    try:
                        key1 = c.__next__()
                        key2 = c.__next__()
                        frame1 = c.__next__()
                        change_key = False

                    except StopIteration as e:
                        print(e)
                    key1 = ord(key1)
                    key2 = ord(key2)
                    frame1 = ord(frame1)
                # Defining the key and choosing the information to encrypt
                if count + 3 < 8:
                    if count >= 3:
                        xy = key1 + key2
                        frame = (frame1 + xy)
                    else:
                        xy = key1 * key2
                        frame = (frame1 * xy)
                    se = data.__next__() + data.__next__() + data.__next__()
                    end.end_data = False
                    end.end_word = False
                    count += 3
                else:
                    xy = key2 - key1
                    frame = (xy - frame1)
                    change_key = True
                    se = data.__next__() + data.__next__()
                    # If it's the end of a word or the encryption
                    if i == len_data - 1:
                        end.end_data = True
                    else:
                        end.end_data = False
                        end.end_word = True
                    count = 0
                # Checking that the selected pixel is normal and that we have not used it
                salt = 1
                while frame % frame_len == 0:
                    frame += salt
                    salt += 1

                frame = int(frame % frame_len)
                if frame < 0:
                    frame *= -1
                x = int((xy * prime_h) % w)

                y = int((xy * prime_m) % h)

                while (x, y, frame) in list_pix:
                    x = int((x + prime_h) % w)
                    y = int((y + prime_m) % h)
                if y < 0:
                    y *= -1
                if x < 0:
                    x *= -1
                list_pix.append((x, y, frame))
                end = EndOfWord

                pixels = pixel_dict[frame].load()
                # Encrypting the information
                pixel = pixels[x, y]
                pixels[x, y] = mod_pix(pixel, se, end)

        print(list_pix[r:])
        frames[0].save(buffer, format="gif", save_all=True, append_images=frames[1:])
    gif_image = buffer.getvalue()
    return Image.open(io.BytesIO(gif_image))


def encoded_in_gif(books, page_number, codex, data, hour_key, image, len_data, min_key, num_book, page_obj, pdf_file,
                   t):
    """
    The function receives information and a key and finds the codex to encrypt
    :param books: The Cipher Codex Repository
    :param page_number: which page to start from
    :param codex:
    :param data:
    :param hour_key:
    :param image:
    :param len_data:
    :param min_key:
    :param num_book:
    :param page_obj:
    :param pdf_file:
    :param t:
    :return: 
    """
    image_frame_len = image.n_frames
    # If the encrypted image is smaller than the amount of information to be encrypted
    if len_data > image.size[0] * image.size[1] * image_frame_len:
        ratio = image.size[0] / image.size[1]
        rows = math.ceil(math.sqrt(len_data * 3) * ratio)
        columns = math.ceil(math.sqrt(len_data * 3) / ratio * 3)
        image = image.resize((rows, columns))
    # Choosing the codex
    while len(codex) < len_data * 3:
        try:
            print(page_number)
            codex += page_obj.extract_text()
            page_number += 1
            page_obj = pdf_file.pages[page_number]
        except IndexError:
            if num_book + 1 < len(books):
                num_book += 1
            else:
                num_book = 0
            pdf_file_obj = PATH + slash + 'file' + slash + books[num_book]
            pdf_file_obj = open(pdf_file_obj, 'rb')
            pdf_file = PyPDF2.PdfReader(pdf_file_obj)
            page_number = 0
            page_obj = pdf_file.pages[page_number]
    print(len(codex), len_data)
    save_image = encode_enc_gif(image, data, len_data, codex, prime(hour_key), prime(min_key), image_frame_len, t)

    return save_image


def encode_info(t, data, img=""):
    """

    :param t: time key
    :param data: what
    :param img: where
    :return:Encrypted information
    """
    # Selecting the encryption file
    books = find_path('file')
    num_book = int(pow(t.tm_min.real, t.tm_sec.real) % len(books))
    pdf_file_obj = PATH + slash + 'file' + slash + books[num_book]
    pdf_file_obj = open(pdf_file_obj, 'rb')
    # creating a pdf reader object
    pdf_file = PyPDF2.PdfReader(pdf_file_obj)

    try:
        if img == "":
            images_in_dir = find_path('images')
            image = PATH + slash + 'images' + slash + images_in_dir[random.randint(0, len(images_in_dir))]
            print(img)
        elif img.__class__ is str:
            image = Image.open(img, 'r')
        else:
            image = img
    except AttributeError:
        image = Image.open(PATH + slash + 'images' + slash + "black.png", 'r')
    image.info['date'] = t

    if data.__class__ is str:
        data = data.encode('latin-1')
    else:
        data = pickle.dumps(data)
        data = base64.b64encode(data)
    data = "".join([format(n, '08b') for n in data])
    if len(data) == 0:
        raise ValueError('Data is empty')
    len_data = len(data) // 8
    pages = len(pdf_file.pages)
    h = t.tm_hour.real
    m = t.tm_min.real
    page_number = (h * m) % pages
    page_obj = pdf_file.pages[page_number]
    codex = ""
    if image.__class__ is not GifImageFile:
        save_image = encoded_in_image(books, page_number, codex, data, h, image, len_data, m, num_book, page_obj,
                                      pdf_file)
    elif image.__class__ is GifImageFile:
        save_image = encoded_in_gif(books, page_number, codex, data, h, image, len_data, m, num_book, page_obj,
                                    pdf_file, t)
    else:
        save_image = ""
    return save_image


def encoded_in_image(books, page_number_, codex, data, hour_key, image, len_data, min_key, num_book, page_obj,
                     pdf_file):
    """
    The function receives information and a key and finds the codex to encrypt
    :param books: The Cipher Codex Repository
    :param page_number_: which page to start from
    :param codex:
    :param data:
    :param hour_key:
    :param image:
    :param len_data:
    :param min_key:
    :param num_book:
    :param page_obj:
    :param pdf_file:
    :return:
    """
    if len_data > image.size[0] * image.size[1] * 6:
        ratio = image.size[0] / image.size[1]
        rows = math.ceil(math.sqrt(len_data * 3) * ratio)
        columns = math.ceil(math.sqrt(len_data * 3) / ratio * 3)
        image = image.resize((rows, columns))
    while len(codex) < len_data * 2:
        try:
            print(page_number_)
            codex += page_obj.extract_text()
            page_number_ += 1
            page_obj = pdf_file.pages[page_number_]
        except IndexError:
            if num_book + 1 < len(books):
                num_book += 1
            else:
                num_book = 0
            pdf_file_obj = PATH + slash + 'file' + slash + books[num_book]
            pdf_file_obj = open(pdf_file_obj, 'rb')
            pdf_file = PyPDF2.PdfReader(pdf_file_obj)
            page_number_ = 0
            page_obj = pdf_file.pages[page_number_]
    print(len(codex), len_data)
    save_image = encode_enc(image, data, len_data, codex, prime(hour_key), prime(min_key))
    return save_image


# Decode the data in the image
def decode_image(image):
    books = find_path('file')
    num_book = int(pow(image.info['date'].tm_min.real, image.info['date'].tm_sec.real) % len(books))
    pdf_file_obj = PATH + slash + 'file' + slash + books[num_book]
    pdf_file_obj = open(pdf_file_obj, 'rb')

    pdf_file = PyPDF2.PdfReader(pdf_file_obj)
    num_of_lines_pix = image.size[0]
    num_of_row_pix = image.size[1]
    list_pix = []
    pages = len(pdf_file.pages)
    h = image.info['date'].tm_hour.real
    m = image.info['date'].tm_min.real
    s = (h * m) % pages
    page_obj = pdf_file.pages[s]
    prime_h = prime(h)
    prime_m = prime(m)
    data = ''
    xy = []
    key_decode = iter(page_obj.extract_text())
    count = 0
    binstr = ''
    next_key = True
    while True:
        if next_key:
            xy = []
            # Choosing the encryption keys
            for i in range(2):
                try:

                    xy.append(ord(key_decode.__next__()))
                    next_key = False
                except StopIteration:
                    s += 1
                    if s > len(pdf_file.pages):
                        if num_book + 1 < len(books):
                            num_book += 1
                        else:
                            num_book = 0
                        pdf_file_obj = PATH + slash + 'images' + slash + books[num_book]
                        pdf_file_obj = open(pdf_file_obj, 'rb')
                        pdf_file = PyPDF2.PdfFileReader(pdf_file_obj)
                        s = 0
                    page_obj = pdf_file.pages[s]
                    key_decode = iter(page_obj.extract_text())
                    xy.append(ord(key_decode.__next__()))
                    next_key = False

        if count + 3 < 8:
            if count >= 3:
                mxy = xy[1] + xy[0]
            else:
                mxy = xy[0] * xy[1]
        else:
            mxy = xy[1] - xy[0]

        x = int((mxy * prime_h) % num_of_lines_pix)
        y = int((mxy * prime_m) % num_of_row_pix)
        salt = 1
        while (x, y) in list_pix:
            x = int((x + prime_h * salt) % num_of_lines_pix)
            y = int((y + prime_m + salt) % num_of_row_pix)
            salt += 1
        if x < 0:
            x *= -1
        if y < 0:
            y *= -1
        list_pix.append((x, y))
        pixels = image.getpixel((x, y))[:3]


        for i in pixels:
            count += 1
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
            if count == 8:
                # string of binary data
                data += chr(int(binstr, 2))
                binstr = ''
                count = 0
                if pixels[-1] % 2 != 0:
                    print(list_pix)
                    return data
                else:
                    break


def decode_gif(image):
    """
    The function receives the gif and checks what the encryption key is then decrypts the encryption
    :param image:
    :return:
    """
    key = ""
    count = 0
    binstr = ''
    list_pix = []
    key_list = []
    frames = [frame.copy() for frame in ImageSequence.Iterator(image)]
    pixel_dict = dict()
    try:
        for i, frame in enumerate(frames):
            pixel_dict[i] = frame
        pixel = pixel_dict[0].load()
        pixel = pixel[0, 0]
        if pixel.__class__ is int:
            if pixel % 2 != 0:
                return None
        elif pixel.__class__ is tuple or pixel.__class__ is list:
            if sum(pixel) % 2 != 0:
                return None
        # Getting the encryption key
        flag = True
        for k in range(0, 18):
            pixels = pixel_dict[1].getpixel((1, k))[:3]
            key_list.append(pixels)
            list_pix.append((1, k, 1))
            for i in pixels:
                count += 1
                if i % 2 == 0:
                    binstr += '0'
                else:
                    binstr += '1'
                if count == 8:
                    key += chr(int(binstr, 2))
                    print(binstr, end="")
                    binstr = ''
                    count = 0
                    if pixels[-1] % 2 != 0:
                        flag = False
                        break
                    else:
                        break
            if not flag:
                break
        r = len(list_pix)

        sec = int(key[:2])
        _min = int(key[2:4])
        hour = int(key[4:])
        books = find_path('file')
        num_book = int(pow(_min, sec) % len(books))
        pdf_file_obj = PATH + slash + 'file' + slash + books[num_book]
        pdf_file_obj = open(pdf_file_obj, 'rb')
        pdf_file = PyPDF2.PdfReader(pdf_file_obj)
        num_of_lines_pix = image.size[0]
        num_of_row_pix = image.size[1]

        pages = len(pdf_file.pages)

        s = (hour * _min) % pages
        page_obj = pdf_file.pages[s]
        prime_h = prime(hour)
        prime_m = prime(_min)
        data = ''
        xy_frame = []
        c = iter(page_obj.extract_text())

        print(len(pixel_dict))
        frame_len = image.n_frames
        key_flag = True
        # Decryption
        while True:
            if key_flag:
                xy_frame = []
                for i in range(3):
                    try:
                        xy_frame.append(ord(c.__next__()))
                        key_flag = False
                    except StopIteration:
                        s += 1
                        if s > len(pdf_file.pages):
                            if num_book + 1 < len(books):
                                num_book += 1
                            else:
                                num_book = 0
                            pdf_file_obj = PATH + slash + 'images' + slash + books[num_book]
                            pdf_file_obj = open(pdf_file_obj, 'rb')
                            pdf_file = PyPDF2.PdfFileReader(pdf_file_obj)
                            s = 0

                        page_obj = pdf_file.pages[s]
                        c = iter(page_obj.extract_text())
                        xy_frame.append(ord(c.__next__()))
                        key_flag = False
            # Choosing the encryption keys
            if count + 3 < 8:
                if count >= 3:
                    mxy = xy_frame[0] + xy_frame[1]
                    frame_number = (xy_frame[2] + mxy)
                else:
                    mxy = xy_frame[0] * xy_frame[1]
                    frame_number = (mxy * xy_frame[2])

            else:
                mxy = xy_frame[1] - xy_frame[0]
                frame_number = (mxy - xy_frame[2])
                key_flag = True
            salt = 1
            while frame_number % frame_len == 0:
                frame_number += salt
                salt += 1

            frame_number = int(frame_number % frame_len)
            if frame_number < 0:
                frame_number *= -1
            x = int((mxy * prime_h) % num_of_lines_pix)

            y = int((mxy * prime_m) % num_of_row_pix)

            while (x, y, frame_number) in list_pix:
                x = int((x + prime_h) % num_of_lines_pix)
                y = int((y + prime_m) % num_of_row_pix)
            if x < 0:
                x *= -1
            if y < 0:
                y *= -1
            list_pix.append((x, y, frame_number))
            image.seek(frame_number)
            image.load()
            pixels = image.getpixel((x, y))[:3]

            #Decryption using the keys
            for i in pixels:
                count += 1
                if i % 2 == 0:
                    binstr += '0'
                else:
                    binstr += '1'
                if count == 8:
                    # string of binary data
                    data += chr(int(binstr, 2))
                    binstr = ''
                    count = 0
                    if pixels[-1] % 2 != 0:
                        print(list_pix[r:])
                        return data
                    else:
                        break
    except ValueError:
        return None


def decode_info(image):
    """
    which receives an image and sends it to be decoded
    :param image:
    :return:
    """
    if image.format.lower() == "gif" or image.__class__ is GifImageFile:
        data = decode_gif(image)
        if data is None:
            return None
    else:
        data = decode_image(image)
    try:
        decoded_b64 = base64.b64decode(data)
        info = pickle.loads(decoded_b64)
    except binascii.Error:
        return data
    except pickle.UnpicklingError:
        return data
    except EOFError:
        return data
    except ValueError:
        return data
    except TypeError:
        return data
    new_img_name = tkinter.filedialog.asksaveasfilename(title="open image", filetypes=(("Image files", "*.png"),))
    info.save(new_img_name, str(new_img_name.split(".")[1].upper()))
    return "image save in: " + new_img_name


def main():
    pass


if __name__ == "__main__":
    main()
