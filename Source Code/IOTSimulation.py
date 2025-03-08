import tkinter
from tkinter import *
import math
import random
from threading import Thread 
from collections import defaultdict
from tkinter import ttk
import numpy as np
import time
import random
import os
import json
from web3 import Web3, HTTPProvider
import ipfsApi

global mobile, labels, mobile_x, mobile_y, text, canvas, mobile_list, root, num_nodes, tf1, nodes, optimal_cluster, cluster_label, ieeecp, eecp
option = 0
details = ""

api = ipfsApi.Client(host='http://127.0.0.1', port=5001)

#function to generate public and private keys for CP-ABE algorithm
def CPABEgenerateKeys():
    if os.path.exists("model/public.txt") == False:
        secret_key = generate_eth_key()
        private_key = secret_key.to_hex()  # hex string
        public_key = secret_key.public_key.to_hex()
        with open('model/public.txt', 'wb') as file:
            pickle.dump(public_key, file)
        file.close()
        with open('model/private.txt', 'wb') as file:
            pickle.dump(private_key, file)
        file.close()
    else:
        with open('model/public.txt', 'rb') as file:
            public_key = pickle.load(file)
        file.close()
        with open('model/private.txt', 'rb') as file:
            private_key = pickle.load(file)
        file.close()        
    return private_key, public_key

#CP-ABE will decrypt data using private key and encrypted text
def CPABEDecrypt(encryptedData):
    private_key, public_key = CPABEgenerateKeys()
    cpabe_decrypt = decrypt(private_key, encryptedData)
    return cpabe_decrypt

def readDetails(contract_type):
    global details
    details = ""
    print(contract_type+"======================")
    blockchain_address = 'http://127.0.0.1:9545' #Blokchain connection IP
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'SoftwareUpdate.json' #SoftwareUpdate contract code
    deployed_contract_address = '0xE1071ad271410500F85BE057968aE484bDBcB1C9' #hash address to access Decentralized contract
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi) #now calling contract to access data
    if contract_type == 'users':
        details = contract.functions.getUser().call()
    if contract_type == 'updates':
        details = contract.functions.getsoftwareUpdates().call()
    if contract_type == 'payments':
        details = contract.functions.getPayments().call()    
    print(details)    

def getDistance(iot_x,iot_y,x1,y1):
    flag = False
    for i in range(len(iot_x)):
        dist = math.sqrt((iot_x[i] - x1)**2 + (iot_y[i] - y1)**2)
        if dist < 60:
            flag = True
            break
    return flag    
    
def generateIOT():
    global mobile, labels, mobile_x, mobile_y, num_nodes, tf1, nodes
    mobile = []
    mobile_x = []
    mobile_y = []
    labels = []
    nodes = []
    canvas.update()
    num_nodes = int(tf1.get().strip())
    
    for i in range(0,num_nodes):
        run = True
        while run == True:
            x = random.randint(100, 450)
            y = random.randint(50, 600)
            flag = getDistance(mobile_x,mobile_y,x,y)
            if flag == False:
                nodes.append([x, y])
                mobile_x.append(x)
                mobile_y.append(y)
                run = False
                name = canvas.create_oval(x,y,x+40,y+40, fill="red")
                lbl = canvas.create_text(x+20,y-10,fill="darkblue",font="Times 8 italic bold",text="IOT "+str(i))
                labels.append(lbl)
                mobile.append(name)    

def startUpdates(text,canvas,selected_iot, src_x, src_y, labels, mobiles, nodes):
    class SimulationThread(Thread):
        def __init__(self,text,canvas,selected_iot, src_x, src_y, labels, mobiles, nodes): 
            Thread.__init__(self) 
            self.canvas = canvas
            self.selected_iot = selected_iot
            self.src_x = src_x
            self.src_y = src_y
            self.text = text
            self.labels = labels
            self.mobiles = mobiles
            self.nodes = nodes
 
        def run(self):
            time.sleep(1)
            for i in range(0,3):
                self.canvas.delete(self.labels[self.selected_iot])
                self.canvas.delete(self.mobiles[self.selected_iot])
                name = self.canvas.create_oval(self.src_x,self.src_y,self.src_x+40,self.src_y+40, fill="green")
                lbl = self.canvas.create_text(self.src_x-20,self.src_y-10,fill="green",font="Times 8 italic bold",text="IOT "+str(self.selected_iot))
                self.labels[self.selected_iot] = lbl
                self.mobiles[self.selected_iot] = name
                time.sleep(1)
                self.canvas.delete(self.labels[self.selected_iot])
                self.canvas.delete(self.mobiles[self.selected_iot])
                name = self.canvas.create_oval(self.src_x,self.src_y,self.src_x+40,self.src_y+40, fill="red")
                lbl = canvas.create_text(self.src_x-20,self.src_y-10,fill="darkblue",font="Times 8 italic bold",text="IOT "+str(self.selected_iot))
                self.labels[self.selected_iot] = lbl
                self.mobiles[self.selected_iot] = name
                time.sleep(1)
            self.canvas.update()
            
    newthread = SimulationThread(text,canvas,selected_iot, src_x, src_y, labels, mobiles, nodes) 
    newthread.start()    

def receiveUpdates():
    global labels, mobile, nodes
    text.delete('1.0', END)
    readDetails("payments")
    rows = details.split("\n")
    flag = False
    for i in range(len(rows)-1):
        flag = True
        arr = rows[i].split("#")
        selected_iot = int(arr[2])
        temp = nodes[selected_iot]
        src_x = temp[0]
        src_y = temp[1]
        text.insert(END,"Software Updates Received for IOT : "+str(selected_iot)+"\n")
        text.update_idletasks()
        startUpdates(text,canvas,selected_iot, src_x, src_y, labels, mobile, nodes)
        option = 1
    if flag == False:
        text.insert(END,"No software updates received\n")
        
def Main():
    global root, tf1, text, canvas, mobile_list
    root = tkinter.Tk()
    root.geometry("1300x1200")
    root.title("IOT Simulation for Software Updates Receive")
    root.resizable(True,True)
    font1 = ('times', 12, 'bold')

    canvas = Canvas(root, width = 800, height = 700)
    canvas.pack()

    l2 = Label(root, text='Num IOT:')
    l2.config(font=font1)
    l2.place(x=820,y=10)

    tf1 = Entry(root,width=10)
    tf1.config(font=font1)
    tf1.place(x=970,y=10)

    l1 = Label(root, text='IOT ID:')
    l1.config(font=font1)
    l1.place(x=820,y=60)

    mid = []
    for i in range(0,20):
        mid.append(str(i))
    mobile_list = ttk.Combobox(root,values=mid,postcommand=lambda: mobile_list.configure(values=mid))
    mobile_list.place(x=970,y=60)
    mobile_list.current(0)
    mobile_list.config(font=font1)

    createButton = Button(root, text="Generate IOT Network", command=generateIOT)
    createButton.place(x=820,y=110)
    createButton.config(font=font1)

    updateButton = Button(root, text="Received Software Updates", command=receiveUpdates)
    updateButton.place(x=820,y=160)
    updateButton.config(font=font1)

    text=Text(root,height=18,width=60)
    scroll=Scrollbar(text)
    text.configure(yscrollcommand=scroll.set)
    text.place(x=820,y=210)
    
    
    root.mainloop()
   
 
if __name__== '__main__' :
    Main ()
    
