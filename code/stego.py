# importing required modules
import base64
import binascii
import io
import math
import os
import pickle
import random
import time
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


def not_encoded_gif(gif):
    try:
        buffer = io.BytesIO()
        with gif as newimg:
            pixel_dict = dict()
            frames = [frame.copy() for frame in ImageSequence.Iterator(newimg)]
            for i, frame in enumerate(frames):
                pixel_dict[i] = frame
            pix_encode = pixel_dict[0].load()
            pixel = pix_encode[0, 0]
            if pixel.__class__ is int:
                if pixel % 2 == 0:
                    if pixel == 0:
                        pixel += 1
                    else:
                        pixel -= 1
            if pixel.__class__ is tuple or pixel.__class__ is list:
                for i in pixel[:3]:
                    if pixel % 2 == 0:
                        if pixel == 0:
                            pixel += 1
                        else:
                            pixel -= 1
            pix_encode[0, 0] = pixel
            #pixel_dict[0] = pix_encode
            frames[0].save(buffer, format="gif", save_all=True, append_images=frames[1:])
            gif_image = buffer.getvalue()
            return Image.open(io.BytesIO(gif_image))
    except:
        return gif


def find_path(dir_in_path):
    files = os.walk(PATH + r'\\' + dir_in_path)
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


def encode_enc(newimg, datalist, lendata, codex, primeh, primem):
    w = newimg.size[0]
    h = newimg.size[1]
    list_pix = []
    data = iter(datalist)
    c = iter(codex)
    count = 0
    next_key = True
    for i in range(lendata):
        for k in range(3):
            if next_key:
                try:
                    p = c.__next__()
                    o = c.__next__()
                    next_key = False
                except StopIteration as e:
                    print(e)
                    next_key = False
                p = ord(p)
                o = ord(o)

            end = EndOfWord
            if count + 3 < 8:
                if count >= 3:
                    xy = p + o
                else:
                    xy = o * p
                se = data.__next__() + data.__next__() + data.__next__()
                end.end_data = False
                end.end_word = False
                count += 3
            else:
                xy = o - p
                se = data.__next__() + data.__next__()
                if i == lendata - 1:
                    end.end_data = True
                else:
                    end.end_data = False
                    end.end_word = True
                count = 0

            x = int((xy * primeh) % w)
            y = int((xy * primem) % h)
            while (x, y) in list_pix:
                x = int((x + primeh) % w)
                y = int((y + primem) % h)
            if x < 0:
                x *= -1
            if y < 0:
                y *= -1
            list_pix.append((x, y))

            pixel = newimg.getpixel((x, y))[:3]
            pixel = mod_pix(pixel, se, end)
            newimg.putpixel((x, y), pixel)
    return newimg


def mod_pix(pixel, data, end):
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

    pix = tuple(pix)
    return pix[0:3]


# Encode data into image
def encode_enc_gif(newimg, datalist, lendata, codex, primeh, primem, frame_len, t):
    key = (str.zfill(str(t.tm_sec.real), 2) + str.zfill(str(t.tm_min.real), 2) + str.zfill(str(t.tm_hour.real),
                                                                                           2)).encode()
    len_key = len(key) * 3
    a = "".join([format(n, '08b') for n in key])
    print("e=", a)
    key = iter(a)
    w = newimg.size[0]
    h = newimg.size[1]
    list_pix = []
    data = iter(datalist)
    c = iter(codex)
    count = 0

    keyl = []
    buffer = io.BytesIO()
    with newimg as newimg:
        frames = [frame.copy() for frame in ImageSequence.Iterator(newimg)]
        pixel_dict = dict()
        end = EndOfWord
        count = 0
        for i, frame in enumerate(frames):
            pixel_dict[i] = frame
        pix_encode = pixel_dict[0].load()
        pixel = pix_encode[0, 0]
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
            keyl.append(pixels[1, i])

        r = len(list_pix)

        print(i)
        xy = 0
        frame = 0
        change_key = True
        for i in range(lendata):
            for k in range(3):

                if change_key:
                    try:
                        p = c.__next__()
                        o = c.__next__()
                        frame1 = c.__next__()
                        change_key = False

                    except StopIteration as e:
                        print(e)
                    p = ord(p)
                    o = ord(o)
                    frame1 = ord(frame1)
                if count + 3 < 8:
                    if count >= 3:
                        xy = p + o
                        frame = (frame1 + xy)
                    else:
                        xy = p * o
                        frame = (frame1 * xy)
                    se = data.__next__() + data.__next__() + data.__next__()
                    end.end_data = False
                    end.end_word = False
                    count += 3
                else:
                    xy = o - p
                    frame = (xy - frame1)
                    change_key = True
                    se = data.__next__() + data.__next__()
                    if i == lendata - 1:
                        end.end_data = True
                    else:
                        end.end_data = False
                        end.end_word = True
                    count = 0
                salt = 1
                while frame % frame_len == 0:
                    frame += salt
                    salt += 1

                frame = int(frame % frame_len)
                if frame < 0:
                    frame *= -1
                x = int((xy * primeh) % w)

                y = int((xy * primem) % h)

                while (x, y, frame) in list_pix:
                    x = int((x + primeh) % w)
                    y = int((y + primem) % h)
                if y < 0:
                    y *= -1
                if x < 0:
                    x *= -1
                list_pix.append((x, y, frame))
                end = EndOfWord

                pixels = pixel_dict[frame].load()

                pixel = pixels[x, y]
                pixels[x, y] = mod_pix(pixel, se, end)

        print(list_pix[r:])
        frames[0].save(buffer, format="gif", save_all=True, append_images=frames[1:])
    gif_image = buffer.getvalue()
    return Image.open(io.BytesIO(gif_image))


def encoded_in_gif(books, c, codex, data, h, image, lendata, m, num_book, page_obj, pdf_file, t):
    image_frame_len = image.n_frames
    if lendata > image.size[0] * image.size[1] * image_frame_len:
        ratio = image.size[0] / image.size[1]
        rows = math.ceil(math.sqrt(lendata * 3) * ratio)
        columns = math.ceil(math.sqrt(lendata * 3) / ratio * 3)
        image = image.resize((rows, columns))
    while len(codex) < lendata * 8:
        try:
            print(c)
            codex += page_obj.extract_text()
            c += 1
            page_obj = pdf_file.pages[c]
        except IndexError:
            if num_book + 1 < len(books):
                num_book += 1
            else:
                num_book = 0
            pdf_file_obj = PATH + r'\\file\\' + books[num_book]
            pdf_file_obj = open(pdf_file_obj, 'rb')
            pdf_file = PyPDF2.PdfReader(pdf_file_obj)
            c = 0
            page_obj = pdf_file.pages[c]
    print(len(codex), lendata)
    save_image = encode_enc_gif(image, data, lendata, codex, prime(h), prime(m), image_frame_len, t)

    return save_image


def encode_info(t, data, img=""):
    books = find_path('file')
    num_book = int(pow(t.tm_min.real, t.tm_sec.real) % len(books))
    pdf_file_obj = PATH + r'\\file\\' + books[num_book]
    pdf_file_obj = open(pdf_file_obj, 'rb')
    # creating a pdf reader object
    pdf_file = PyPDF2.PdfReader(pdf_file_obj)
    if img == "":
        images_in_dir = find_path('images')
        img = PATH + r'\\images\\' + images_in_dir[random.randint(0, len(images_in_dir))]
        print(img)
    image = Image.open(img, 'r')
    image.info['date'] = t
    image.info['image name'] = img.split('\\')[-1]

    if data.__class__ is str:
        data = data.encode()
    else:
        data = pickle.dumps(data)
        data = base64.b64encode(data)
    data = "".join([format(n, '08b') for n in data])
    if len(data) == 0:
        raise ValueError('Data is empty')
    lendata = len(data) // 8
    pages = len(pdf_file.pages)
    h = t.tm_hour.real
    m = t.tm_min.real
    c = (h * m) % pages
    page_obj = pdf_file.pages[c]
    codex = ""
    if image.__class__ is not GifImageFile:
        save_image = encoded_in_image(books, c, codex, data, h, image, lendata, m, num_book, page_obj, pdf_file)
    elif image.__class__ is GifImageFile:
        save_image = encoded_in_gif(books, c, codex, data, h, image, lendata, m, num_book, page_obj, pdf_file, t)
    else:
        save_image = ""
    return save_image


def encoded_in_image(books, c, codex, data, h, image, lendata, m, num_book, page_obj, pdf_file):
    if lendata > image.size[0] * image.size[1] * 6:
        ratio = image.size[0] / image.size[1]
        rows = math.ceil(math.sqrt(lendata * 3) * ratio)
        columns = math.ceil(math.sqrt(lendata * 3) / ratio * 3)
        image = image.resize((rows, columns))
    while len(codex) < lendata * 6:
        try:
            print(c)
            codex += page_obj.extract_text()
            c += 1
            page_obj = pdf_file.pages[c]
        except IndexError:
            if num_book + 1 < len(books):
                num_book += 1
            else:
                num_book = 0
            pdf_file_obj = PATH + r'\\file\\' + books[num_book]
            pdf_file_obj = open(pdf_file_obj, 'rb')
            pdf_file = PyPDF2.PdfReader(pdf_file_obj)
            c = 0
            page_obj = pdf_file.pages[c]
    print(len(codex), lendata)
    save_image = encode_enc(image, data, lendata, codex, prime(h), prime(m))
    return save_image


# Decode the data in the image
def decode_image(image):
    books = find_path('file')
    num_book = int(pow(image.info['date'].tm_min.real, image.info['date'].tm_sec.real) % len(books))
    pdf_file_obj = PATH + r'\\file\\' + books[num_book]
    pdf_file_obj = open(pdf_file_obj, 'rb')
    # creating a pdf reader object
    pdf_file = PyPDF2.PdfReader(pdf_file_obj)
    # img = input("Enter image name(with extension) : ")
    # img = PATH + r"\\images\\ptt.png"
    # image = Image.open(img, 'r')
    num_of_lines_pix = image.size[0]
    num_of_row_pix = image.size[1]
    list_pix = []
    pages = len(pdf_file.pages)
    h = image.info['date'].tm_hour.real
    m = image.info['date'].tm_min.real
    s = (h * m) % pages
    page_obj = pdf_file.pages[s]
    primeh = prime(h)
    primem = prime(m)
    data = ''
    xy = []
    c = iter(page_obj.extract_text())
    count = 0
    binstr = ''
    next_key = True
    while True:
        if next_key:
            xy = []
            for i in range(2):
                try:

                    xy.append(ord(c.__next__()))
                    next_key = False
                except StopIteration:
                    s += 1
                    if s > len(pdf_file.pages):
                        if num_book + 1 < len(books):
                            num_book += 1
                        else:
                            num_book = 0
                        pdf_file_obj = PATH + r'\\images\\' + books[num_book]
                        pdf_file_obj = open(pdf_file_obj, 'rb')
                        pdf_file = PyPDF2.PdfFileReader(pdf_file_obj)
                        s = 0
                    page_obj = pdf_file.pages[s]
                    c = iter(page_obj.extract_text())
                    xy.append(ord(c.__next__()))
                    next_key = False

        if count + 3 < 8:
            if count >= 3:
                mxy = xy[1] + xy[0]
            else:
                mxy = xy[0] * xy[1]
        else:
            mxy = xy[1] - xy[0]

        x = int((mxy * primeh) % num_of_lines_pix)
        y = int((mxy * primem) % num_of_row_pix)
        while (x, y) in list_pix:
            x = int((x + primeh) % num_of_lines_pix)
            y = int((y + primem) % num_of_row_pix)
        if x < 0:
            x *= -1
        if y < 0:
            y *= -1
        list_pix.append((x, y))
        pixels = image.getpixel((x, y))[:3]
        # string of binary data

        for i in pixels:
            count += 1
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'
            if count == 8:
                data += chr(int(binstr, 2))
                binstr = ''
                count = 0
                if pixels[-1] % 2 != 0:
                    return data
                else:
                    break


def decode_gif(image):
    key = ""
    count = 0
    binstr = ''
    list_pix = []
    keyl = []
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

        flag = True
        for k in range(0, 18):
            pixels = pixel_dict[1].getpixel((1, k))[:3]
            keyl.append(pixels)
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
        min = int(key[2:4])
        hour = int(key[4:])
        h = hour
        m = min
        books = find_path('file')
        num_book = int(pow(min, sec) % len(books))
        pdf_file_obj = PATH + r'\\file\\' + books[num_book]
        pdf_file_obj = open(pdf_file_obj, 'rb')
        pdf_file = PyPDF2.PdfReader(pdf_file_obj)
        num_of_lines_pix = image.size[0]
        num_of_row_pix = image.size[1]

        pages = len(pdf_file.pages)

        s = (h * m) % pages
        page_obj = pdf_file.pages[s]
        primeh = prime(h)
        primem = prime(m)
        data = ''
        xyframe = []
        c = iter(page_obj.extract_text())

        print(len(pixel_dict))
        frame_len = image.n_frames
        key_flag = True
        while True:
            if key_flag:
                xyframe = []
                for i in range(3):
                    try:
                        xyframe.append(ord(c.__next__()))
                        key_flag = False
                    except StopIteration:
                        s += 1
                        if s > len(pdf_file.pages):
                            if num_book + 1 < len(books):
                                num_book += 1
                            else:
                                num_book = 0
                            pdf_file_obj = PATH + r'\\images\\' + books[num_book]
                            pdf_file_obj = open(pdf_file_obj, 'rb')
                            pdf_file = PyPDF2.PdfFileReader(pdf_file_obj)
                            s = 0

                        page_obj = pdf_file.pages[s]
                        c = iter(page_obj.extract_text())
                        xyframe.append(ord(c.__next__()))
                        key_flag = False
            if count + 3 < 8:
                if count >= 3:
                    mxy = xyframe[0] + xyframe[1]
                    frame_number = (xyframe[2] + mxy)
                else:
                    mxy = xyframe[0] * xyframe[1]
                    frame_number = (mxy * xyframe[2])

            else:
                mxy = xyframe[1] - xyframe[0]
                frame_number = (mxy - xyframe[2])
                key_flag = True
            salt = 1
            while frame_number % frame_len == 0:
                frame_number += salt
                salt += 1

            frame_number = int(frame_number % frame_len)
            if frame_number < 0:
                frame_number *= -1
            x = int((mxy * primeh) % num_of_lines_pix)

            y = int((mxy * primem) % num_of_row_pix)

            while (x, y, frame_number) in list_pix:
                x = int((x + primeh) % num_of_lines_pix)
                y = int((y + primem) % num_of_row_pix)
            if x < 0:
                x *= -1
            if y < 0:
                y *= -1
            list_pix.append((x, y, frame_number))
            image.seek(frame_number)
            image.load()
            pixels = image.getpixel((x, y))[:3]
            # string of binary data

            for i in pixels:
                count += 1
                if i % 2 == 0:
                    binstr += '0'
                else:
                    binstr += '1'
                if count == 8:
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
    pt = time
    p = Image.open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\map.JPG", 'r')
    # u = encode_info(pt.localtime(), "aba saba daba",                    r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\Zz04NjA3ZjljMjQ0ODkxMWViOWRjYzU1OGJkNjI1ZjVkZA==.gif")
    y = encode_info(pt.localtime(), "lama ama sav af af a tama",
                    r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\map.JPG")
    # print(decode_info(u) == "aba saba daba")
    print(decode_info(y) == "lama ama sav af af a tama")


if __name__ == "__main__":
    main()
