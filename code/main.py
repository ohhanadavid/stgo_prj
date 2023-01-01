# Python program implementing Image Steganography
import os

# PIL module is used to extract
# pixels of image and modify it
from PIL import Image
import base64
import math

path = os.path.dirname(os.path.realpath(__file__))+'\\images\\'

def gen_data(data):
    # list of binary codes
    # of given data
    newd = []
    for i in data:
        for j in str(i):
            newd.append(format(ord(j), '08b'))
    return newd


def mod_pix(pixel, datalist, lendata):
    imdata = iter(pixel)
    count = 0
    print(lendata)
    for i in range(0, lendata):

        if count == lendata:
            print(count)
        # Extracting 3 pixels at a time
        pix = [value for value in imdata.__next__()[:3] + imdata.__next__()[:3] + imdata.__next__()[:3]]
        t = datalist[count:count + 8]
        count += 8
        # Pixel value should be made
        # odd for 1 and even for 0
        for j in range(0, 8):
            if t[j] == '0' and pix[j] % 2 != 0:
                pix[j] -= 1

            elif t[j] == '1' and pix[j] % 2 == 0:
                if pix[j] != 0:
                    pix[j] -= 1

                else:
                    pix[j] += 1

            # pix[j] -= 1

        # Eighth pixel of every set tells
        # whether to stop ot read further.
        # 0 means keep reading; 1 means thec
        # message is over.
        if i == lendata - 1:
            if pix[-1] % 2 == 0:
                if pix[-1] != 0:
                    pix[-1] -= 1

                else:
                    pix[-1] += 1

        else:
            if pix[-1] % 2 != 0:
                pix[-1] -= 1

        pix = tuple(pix)
        yield pix[0:3]
        yield pix[3:6]
        yield pix[6:9]


def encode_enc_1(newimg, datalist, lendata):
    w = newimg.size[0]
    print(w, newimg.size)
    (x, y) = (0, 0)
    count = 0
    for pixel in mod_pix(newimg.getdata(), datalist, lendata):
        # Putting modified pixels in the new image
        newimg.putpixel((x, y), pixel)
        count += 1
        if x == w - 1:
            x = 0
            y += 1
            if y == newimg.size[1] - 1:
                print(y)
        else:
            x += 1


# Encode data into image
def encode_image():
    img_code = r"tomer.png"
    image_code = Image.open(img_code, 'r')
    image_decode_file = open("jdfjdf.png", 'rb')
    image_file = image_decode_file.read()
    image_decode_file.close()
    data = base64.b64encode(image_file)
    data = "".join([format(n, '08b') for n in data])
    if len(data) == 0:
        raise ValueError('Data is empty')
    newimg = image_code.copy()
    image_code.close()
    lendata = len(data) // 8
    yachas = newimg.size[0] / newimg.size[1]
    w = math.ceil(math.sqrt(lendata * 3) * yachas)
    h = math.ceil(math.sqrt(lendata * 3) / yachas * 3)
    newimg = newimg.resize((w, h))
    print(w, h)

    encode_enc_1(newimg, data, lendata)
    newimg.save(r"0enphoto.png", str(r"0enphoto.png".split(".")[1].upper()))
    newimg.close()


# Decode the data in the image
def decode_image():
    # img = input("Enter image name(with extension) : ")
    img = r"0enphoto.png"
    image = Image.open(img, 'r')

    data = ''
    imgdata = iter(image.getdata())
    for i in range(0):
        next(imgdata)
    while True:
        pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]]
        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            data = data.encode()
            c = base64.b64decode(data)
            f = open("df.png", 'wb')
            f.write(c)
            f.close()
            return "gg"


# Encode data into image
def encode_text():
    img = path+"jdfjdf.png"
    image = Image.open(img, 'r')

    data = "aba saba daba"
    if len(data) == 0:
        raise ValueError('Data is empty')
    data = data.encode()
    data = "".join([format(n, '08b') for n in data])
    newimg = image.copy()
    encode_enc_1(newimg, data, len(data) // 8)

    new_img_name = "texte.png"
    newimg.save(path+new_img_name, str(new_img_name.split(".")[1].upper()))


# Decode the data in the image
def decode_text():
    # img = input("Enter image name(with extension) : ")
    img = r"texte.png"
    image = Image.open(img, 'r')

    data = ''
    imgdata = iter(image.getdata())
    for i in range(0):
        next(imgdata)
    while True:
        pixels = [value for value in imgdata.__next__()[:3] + imgdata.__next__()[:3] + imgdata.__next__()[:3]]
        # string of binary data
        binstr = ''

        for i in pixels[:8]:
            if i % 2 == 0:
                binstr += '0'
            else:
                binstr += '1'

        data += chr(int(binstr, 2))
        if pixels[-1] % 2 != 0:
            return data


# Main Function
def main():
    a = int(input(":: Welcome to Steganography ::\n"
                  "1. Encode\n2. Decode\n"))
    if a == 1:
        encode_text()

    elif a == 2:
        print("Decoded Word : " + decode_text())
    else:
        raise Exception("Enter correct input")


# Driver Code
if __name__ == '__main__':
    # Calling main function
    main()
