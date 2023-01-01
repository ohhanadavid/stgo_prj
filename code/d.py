import requests
import rsa
import pickle
import base64
import json
from PIL import Image


import subprocess
import tkinter as tk
from tkinter import filedialog

# Open the save dialog window
filename = filedialog.asksaveasfilename(initialdir="/", title="Select file", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))

# Print the selected file name
print(filename)
b=subprocess.run(['explorer.exe', r"C:\Users\David Ohhana\Desktop\College\cyber network\project\code\file"])

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



