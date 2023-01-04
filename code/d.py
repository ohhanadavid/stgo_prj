import msvcrt
import threading
import time
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
from  PIL import Image


import tkinter as tk

# Create the main window
window = tk.Tk()

# Define the size of the grid as 3 rows and 3 columns
for i in range(3):
    window.rowconfigure(i, minsize=100)
    window.columnconfigure(i, minsize=100)

# Create a label and place it in the first row and first column of the grid
label1 = tk.Label(window, text="Label 1")
label1.grid(row=0, column=0)

# Create a second label and place it in the first row and second column of the grid
label2 = tk.Label(window, text="Label 2")
label2.grid(row=0, column=1)

# Create a third label and place it in the second row and first column of the grid
label3 = tk.Label(window, text="Label 3")
label3.grid(row=1, column=0)

# Create a fourth label and place it in the second row and second column of the grid
label4 = tk.Label(window, text="Label 4")
label4.grid(row=1, column=1)

# Run the Tkinter event loop
window.mainloop()


msg="dfsfdsf"
#msg = "".join([format(n, '08b') for n in msg])
data = b"".join([bytes(chr(int(msg[i:i + 8], 2)), "utf-8") for i in range(0, len(msg), 8)])
decoded_b64 = base64.b64decode(data)
data = pickle.loads(decoded_b64)

o=time.localtime()
u=json.dumps(o)
u=json.loads(u)
c=tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
d=Image.open(c,'r')
k=open(c,'rb')
k=k.read()
l=tkinter.filedialog.asksaveasfilename(title="open image", filetypes=(("Image files", "*.png"),))
j=open(l,'wb')
d.info["sdsdfsd"]="sdfdsfdssdsdfsdf"
d.save(l+'.png',"png")
p=Image.open(l+'.png','r')
o=pickle.dumps(d)
o=base64.b64decode(o)
j.write(o)
t=open("nnnnn.png",'wb')
t.write(k)



path_image = tkinter.filedialog.askopenfilename(title="open image", filetypes=(("Image files", "*.png"),))
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


def s(b,w):
    filer = str(b.get(1.0, END))
    print(filer)




def u(f,c):
    print(c)
    f = "False"
    w = Tk()
    b = Text(w)
    #b.configure(height=12,width=20)
    b.grid(column=1,row=0)
    l=Label(w,text="aba")
    l.configure(height=10,width=3)
    l.grid(column=0,row=0)
    #l.pack()
    c=Text(w)
    c.grid(column=1)
   # c.pack()
    b.insert(END, f)
    b.insert(END,'\nTo:')
    b.insert(END, '\nSubject:')
    o = Button(text="cmd", command=lambda: s(b,w),compound="top")
    o.grid(column=2)

   # b.pack()
    Text(w).insert(END,"blalb")
    w.mainloop()
    f = "True"

u("true","g")
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
