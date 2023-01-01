# importing required modules
import binascii
import math
import os
import pickle
import random
from io import BytesIO
from PIL import Image
import time
import base64
from math import *

import PyPDF2


class EndOfWord:
    end_word = False
    end_data = False

    def __init__(self, end__word=False, end_of_data=False):
        self.end_word = end__word
        self.end_data = end_of_data


PATH = os.path.dirname(os.path.realpath(__file__))


def find_path(dir_in_path):

    files = os.walk(PATH + r'\\' + dir_in_path)
    return list(files)[0][-1]


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
    for i in range(lendata):
        for k in range(3):
            p = c.__next__()
            o = c.__next__()
            xy = ord(p) * ord(o)
            x = (xy * primeh) % w
            y = (xy * primem) % h
            while (x, y) in list_pix:
                x = (x + primeh) % w
                y = (y + primem) % h
            list_pix.append((x, y))
            # Putting modified pixels in the new image
            end = EndOfWord

            if count + 3 < 8:
                se = data.__next__() + data.__next__() + data.__next__()
                end.end_data = False
                end.end_word = False
                count += 3
            else:
                se = data.__next__() + data.__next__()
                if i == lendata - 1:
                    end.end_data = True
                else:
                    end.end_data = False
                    end.end_word = True
                count = 0
            pixel = mod_pix(newimg.getpixel((x, y))[:3], se, end)
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
    else:
        img = PATH + r'\\images\\' + img
    image = Image.open(img, 'r')
    image.info['date'] = t
    image.info['image name'] = img.split('\\')[-1]

    if data.__class__ is str:
        data = data.encode()
    else:
        data=pickle.dumps(data)
        data=base64.b64encode(data)
    data = "".join([format(n, '08b') for n in data])
    if len(data) == 0:
        raise ValueError('Data is empty')
    lendata = len(data) // 8
    if lendata > image.size[0] * image.size[1] * 3:
        ratio = image.size[0] / image.size[1]
        rows = math.ceil(math.sqrt(lendata * 3) * ratio)
        columns = math.ceil(math.sqrt(lendata * 3) / ratio * 3)
        image = image.resize((rows, columns))
    pages = len(pdf_file.pages)

    h = t.tm_hour.real
    m = t.tm_min.real
    c = (h * m) % pages
    page_obj = pdf_file.pages[c]
    codex = ""
    while len(codex) < lendata * 3:
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

    new_img_name = PATH + r"\\images\\ptt.png"
    save_image=encode_enc(image, data, lendata, codex, prime(h), prime(m))
    save_image.save(new_img_name, str(new_img_name.split(".")[1].upper()))
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
    while True:
        for i in range(2):
            try:
                xy.append(ord(c.__next__()))
            except StopIteration:
                s += 1
                if s > pdf_file.numPages:
                    if num_book + 1 < len(books):
                        num_book += 1
                    else:
                        num_book = 0
                    pdf_file_obj = PATH + r'\\images\\' + books[num_book]
                    pdf_file_obj = open(pdf_file_obj, 'rb')
                    pdf_file = PyPDF2.PdfFileReader(pdf_file_obj)
                    s = 0

                page_obj = pdf_file.pages[s]
                c = iter(page_obj.extractText())
                xy.append(ord(c.__next__()))

        mxy = xy[0] * xy[1]
        xy = []
        x = (mxy * primeh) % num_of_lines_pix
        y = (mxy * primem) % num_of_row_pix
        while (x, y) in list_pix:
            x = (x + primeh) % num_of_lines_pix
            y = (y + primem) % num_of_row_pix
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


def decode_info(image):
    data = decode_image(image)
    try:
        decoded_b64 = base64.b64decode(data)
        info = pickle.loads(decoded_b64)
    except binascii.Error:
        return data

    new_img_name = PATH + r"\\images\\" + image.info['image name']
    info.save(new_img_name, str(new_img_name.split(".")[1].upper()))
    return "image save in: " + new_img_name


def main():
    # creating a pdf file object
    pdf_file_obj = open(PATH + r'\\file\\1001 Books_ You Must Read Before You Die ( PDFDrive ).pdf', 'rb')
    pt = time

    print(pt.localtime())

    i = Image.open(PATH + r"\\images\\ptt.png", 'r')
    u=encode_info(pt.localtime(),"aba sabbab fkfgkf",'dd.png')

    print(decode_info(u))


main()
