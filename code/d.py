import msvcrt
import threading
import tkinter

import future
import requests
import rsa
import pickle
import base64
import json
from PIL import Image

import subprocess
from future.moves import *
import io
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox

g="sdfsdf"
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


def s(b):
    filer = str(b.get(1.0, END))
    print(filer)
    b.clipboard_clear()



def u(f,c):



    print(c)
    f = "False"
    w = Tk()
    b = Text(w)
    b.insert(END, c)
    b.insert(END,'\nTo:')
    b.insert(END, '\nSubject:')
    o = Button(text="cmd", command=lambda: s(b))
    o.pack()

    b.pack()
    w.mainloop()
    f = "True"


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
        print (c)

try:
    c="a"
    p=threading.Thread(target=o(c))
    p.start()
    for i in range(10):
        c+='a'
    c=""


    c=""
    while True:

        if msvcrt.kbhit() and f == "True":
            while msvcrt.kbhit():
                c+=msvcrt.getche().decode()

            t = threading.Thread(target=u(f,c))
            t.start()
        # print(x)
        x += 1

except KeyboardInterrupt:
    print(x)
