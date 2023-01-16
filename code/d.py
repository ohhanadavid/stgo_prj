import math
import msvcrt
import os
import threading
import time
import tkinter

import PIL.ImageTk
import future
import requests
import rsa
import pickle
import base64
import json
from PIL import Image

import subprocess

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from future.moves import *
import io
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter.scrolledtext
from PIL.PngImagePlugin import PngImageFile
from PIL.JpegImagePlugin import JpegImageFile
from PIL.GifImagePlugin import GifImageFile
from PIL.BmpImagePlugin import BmpImageFile
from PIL.TiffImagePlugin import TiffImageFile
from PIL.IcoImagePlugin import IcoImageFile
import hashlib
import rsa
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.fernet import Fernet

p=Image.open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\Zz04NjA3ZjljMjQ0ODkxMWViOWRjYzU1OGJkNjI1ZjVkZA==.gif",
            'r')
b=io.BytesIO()
p.save(b, save_all=True, format="gif")
n = b.getvalue().decode('latin-1')
n=n.encode('latin-1')
c = io.BytesIO(n)
a = Image.open(c)
s="שלום"
s=s.encode('latin-1')
s=s.decode('latin-1')
a="aba".encode('latin-1')
b=a.decode()
c=a.decode('latin-1')
print(a,b,c)


d={1:2,3:4,5:6}
c={1:4,7:1,8:3,9:8}
d.update(c)
co=20
for i in d.items():
    print(i)
    d.pop(i[0])
    d[co]=8
    co+=1




key = Fernet.generate_key()

d=hashlib.sha3_512

c=d(b"aba").hexdigest()

i=d(b"aba").hexdigest()

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

public_key = private_key.public_key()


pem1 = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
ciphertext = public_key.encrypt(
    key,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
o=open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\d.png", 'rb').read()
o = Image.open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\d.png", 'r')
o = pickle.dumps(o)
o = base64.b64encode(o)
o = "".join([format(n, '08b') for n in o])
o=o.encode()
cipher = Fernet(key)
ciphertext1 = cipher.encrypt(o)
print(len(ciphertext1+ciphertext))
decrypted_key = private_key.decrypt(
    ciphertext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)
cipher = Fernet(decrypted_key)
original_data = cipher.decrypt(ciphertext1)





cipher = Fernet(key)
ciphertext = cipher.encrypt(o)
original_data = cipher.decrypt(ciphertext)
ciphertext = public_key.encrypt(
    o,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

key = os.urandom(32)
backend = default_backend()
cipher = Cipher(algorithms.AES(key), modes.CBC(os.urandom(16)), backend=backend)
decryptor = cipher.decryptor()
decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
hash_value, image_data = decrypted_data.split(b":")
















o = Image.open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\d.png", 'r')
o = pickle.dumps(o)
o = base64.b64encode(o)
o = "".join([format(n, '08b') for n in o])
o=o.encode()
d=hashlib.sha3_512()
d.update(o)
d=d.hexdigest()


def a(i):
    t=i+2
    p=i+5
    return t,p

for i in a(3):
    print(i)



d=hashlib.sha3_512()
d.update("aba".encode())
p=d.hexdigest()
tkinter.filedialog.askopenfilename(title="open image to send", filetypes=(("png", "*.png"),("jpeg", "*.jpg"),("jpeg", "*.jpeg")))
# Generate a pair of RSA keys
(pubkey, privkey) = rsa.newkeys(10000)

f='a'*52
t=rsa.encrypt(f.encode(),pubkey)
p=pickle.dumps(pubkey)
o = base64.b64encode(p)
o = "".join([format(n, '08b') for n in o])
i=len(o)
# Encrypt data using the public key
data = "my secret data".encode()
encrypted_data = rsa.encrypt(data, pubkey)

# Decrypt the encrypted data using the private key
decrypted_data = rsa.decrypt(encrypted_data, privkey).decode()

print(decrypted_data) # prints "my secret data"

d=hashlib.sha256(b"aba saba daba")
p=d.digest()

print(p)
l=['a','d','b','c']
l.sort()
print(l)


f = open("1.txt", 'r').read()
p = open("2.txt", 'r').read()
o = Image.open(r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\d.png", 'r')
o = pickle.dumps(o)
o = base64.b64encode(o)
o = "".join([format(n, '08b') for n in o])
print(o == f)
print(o == p)
print(p == f)

data = b"".join([bytes(chr(int(p[i:i + 8], 2)), "utf-8") for i in range(0, len(p), 8)])
print("len", len(data))
decoded_b64 = base64.b64decode(data)
data = pickle.loads(decoded_b64)

print(2.000000000000001 / 2)
print(math.ceil(2.0000000000000000000000000000000000000000000000000000000001 / 2))
p = "acvfdf001"
c = p[-3:]
d = p[-1:-3]
print(c, d)

l = [1, 2, 3, 4]
for i in range(0, len(l), 3):
    print(i)

for i in range(5):
    while True:
        try:
            print(next(p))
        except StopIteration:
            break
    l += [11, 12, 13, 14]

w = Tk()
t = tkinter.scrolledtext.ScrolledText(w, width=100, height=20)
i = r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\images\d.png"
im = Image.open(i, 'r')
im = im.resize((int(100 * (im.size[0] / im.size[1])), int(100 / (im.size[0] / im.size[1]))))
im = ImageTk.PhotoImage(im)
t.image_create(END, image=im)
t.pack()
w.mainloop()

import tkinter as tk


class A:
    a = ""
    b = 0

    def __init__(self, a, b):
        self.a = a
        self.b = b


o = dict()

for i in range(6):
    o[ord(str(i))] = A(str(i), i)
print(o.items())
print('\n\r'.join([str(item) for item in o.items()]))
print("o:", o)
p = [y.a for y in o.values()]
print(p)
f = threading.Lock()
d = {1: 2, 2: 3, 4: 5}
o = json.dumps(d)
print(o)
print(json.loads(o))
p = list(d)
for i in p:
    print(i)

i = 0
f.acquire(blocking=False)
print(f.locked())
f.release()
print(f.locked())
with f:
    print(f.locked())
    print(i)
    i += 1
print(f.locked())

c = "p"


def i(a):
    print(a)


print(o.items())
e = list(map(lambda x, y: {x: y.a}, o.keys(), o.values()))
print(e)
t = threading.Thread(target=i, args=c)
t.daemon = False
t.run()
if t.is_alive():
    t.run()
else:
    t.isAlive()
    t.run()

d = ['k', 'j', 'k', 't']
print(str(set(d)))
print(d, set(d))

d = dict()
d['r'] = "asd"
d['tt'] = "fdgd"
p = str(d)
print(p)
for i in d.items():
    print(i)

# Create the main window
window = tk.Tk()


def error():
    if 'a' in t.get():
        b.configure(state=DISABLED)
        return False
    b.configure(state=NORMAL)
    return True


b = Button(window, text="ldld")
b.pack()
t = Entry(window, width=20, validatecommand=error, validate="key")
t.pack()
# Run the Tkinter event loop
window.mainloop()

msg = "dfsfdsf"
# msg = "".join([format(n, '08b') for n in msg])
data = b"".join([bytes(chr(int(msg[i:i + 8], 2)), "utf-8") for i in range(0, len(msg), 8)])
decoded_b64 = base64.b64decode(data)
data = pickle.loads(decoded_b64)

o = time.localtime()
u = json.dumps(o)
u = json.loads(u)
c = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
d = Image.open(c, 'r')
k = open(c, 'rb')
k = k.read()
l = tkinter.filedialog.asksaveasfilename(title="open image", filetypes=(("Image files", "*.png"),))
j = open(l, 'wb')
d.info["sdsdfsd"] = "sdfdsfdssdsdfsdf"
d.save(l + '.png', "png")
p = Image.open(l + '.png', 'r')
o = pickle.dumps(d)
o = base64.b64decode(o)
j.write(o)
t = open("nnnnn.png", 'wb')
t.write(k)

path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
g = "sdfsdf"
print(g.__class__.__name__)
f = "True"
"""
# Open the save dialog window
filename = filedialog.askopenfile(initialdir="/", title="Select file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
filename=str(filename.name)
# Print the selected file name
print(filename)


k= Image.open("d.png",'r')
public_key,private_key = rsa.newkeys(1024)
print(private_key,public_key,sep="\n"*3)

server = "https://web-production-39c4.up.railway.app"
k.text['j']=3
i=pickle.dumps(k)
p=base64.b64encode(i)
ii="".join([format(n, '08b') for n in p])
ll=len(ii)
t=json.dumps({"size":"800x800", "sindex": "100x10" ,"0":+3 , "1":-3 })
l=base64.b64decode(p)
h=pickle.loads(i)
t=k.copy()
h.save("time.png", str("dd.png".split(".")[1].upper()))
respone = (requests.get(server+"/",params={"public_key":base64.b64encode(pickle.dumps(public_key))}).content)
data_block= json.loads(rsa.decrypt(respone,priv_key=private_key).decode(encoding="ascii"))
"""


def inp(inpt, f):
    if msvcrt.kbhit() and f == "True":
        f = "False"
        ch = msvcrt.getche().decode()
        p = input("enter input: ")
        inpt = ch + p
        f = "True"


def s(b, w):
    filer = str(b.get(1.0, END))
    print(filer)


def u(f, c):
    print(c)
    f = "False"
    w = Tk()
    b = Text(w)
    # b.configure(height=12,width=20)
    b.grid(column=1, row=0)
    l = Label(w, text="aba")
    l.configure(height=10, width=3)
    l.grid(column=0, row=0)
    # l.pack()
    c = Text(w)
    c.grid(column=1)
    # c.pack()
    b.insert(END, f)
    b.insert(END, '\nTo:')
    b.insert(END, '\nSubject:')
    o = Button(text="cmd", command=lambda: s(b, w), compound="top")
    o.grid(column=2)

    # b.pack()
    Text(w).insert(END, "blalb")
    w.mainloop()
    f = "True"


u("true", "g")
user_input = ""
x = 0
"""
root = Tk()
b = Text(root)
b.insert(END,"v")
b.pack()
root.mainloop()
root.destroy()
"""


def o(c):
    while c != "":
        print(c)


try:
    c = "a"
    p = threading.Thread(target=o(c))
    p.start()
    for i in range(10):
        c += 'a'
    c = ""

    c = ""
    while True:

        if msvcrt.kbhit() and f == "True":
            while msvcrt.kbhit():
                c += msvcrt.getche().decode()

            t = threading.Thread(target=u(f, c))
            t.start()
        # print(x)
        x += 1

except KeyboardInterrupt:
    print(x)
