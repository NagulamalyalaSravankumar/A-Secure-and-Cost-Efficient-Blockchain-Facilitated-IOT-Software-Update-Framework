from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from datetime import date
import os
import json
from web3 import Web3, HTTPProvider
import ipfsApi
from django.core.files.storage import FileSystemStorage
import pickle
from datetime import date
import base64
import urllib, mimetypes
from django.http import HttpResponse
from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt

global details, username
details=''
global contract

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

#CP-ABE will encrypt data using plain text adn public key
def CPABEEncrypt(plainText):
    private_key, public_key = CPABEgenerateKeys()
    cpabe_encrypt = encrypt(public_key, plainText)
    return cpabe_encrypt

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

def saveDataBlockChain(currentData, contract_type):
    global details
    global contract
    details = ""
    blockchain_address = 'http://127.0.0.1:9545'
    web3 = Web3(HTTPProvider(blockchain_address))
    web3.eth.defaultAccount = web3.eth.accounts[0]
    compiled_contract_path = 'SoftwareUpdate.json' #SoftwareUpdate contract file
    deployed_contract_address = '0xE1071ad271410500F85BE057968aE484bDBcB1C9' #contract address
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
    file.close()
    contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
    readDetails(contract_type)
    if contract_type == 'users':
        details+=currentData
        msg = contract.functions.setUser(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'updates':
        details+=currentData
        msg = contract.functions.setsoftwareUpdates(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)
    if contract_type == 'payments':
        details+=currentData
        msg = contract.functions.setPayments(details).transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(msg)    

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})    

def ManufactureLogin(request):
    if request.method == 'GET':
       return render(request, 'ManufactureLogin.html', {})
    
def OwnerLogin(request):
    if request.method == 'GET':
        return render(request, 'OwnerLogin.html', {})

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Upload(request):
    if request.method == 'GET':
       return render(request, 'Upload.html', {})

def calculateBlock(file_data):
    length = len(file_data)
    tot_blocks = 0
    size = 0
    if length >= 1000:
        size = length / 10
        tot_blocks = 10
    if length < 1000 and length > 500:
        size = length / 5
        tot_blocks = 5
    if length < 500 and length > 1:
        size = length / 3
        tot_blocks = 3
    return int(size), tot_blocks, length  

def UploadAction(request):
    if request.method == 'POST':
        global username
        today = date.today()   
        filedata = request.FILES['t1'].read()
        filename = request.FILES['t1'].name
        size, tot_blocks, length = calculateBlock(filedata)
        names = ""
        code = ""
        start = 0
        end = size
        block = []
        for i in range(0, tot_blocks):
            chunk = filedata[start:end]
            chunk = CPABEEncrypt(chunk)
            block.append(chunk[0:20])
            start = end
            end = end + size
            chunk = pickle.dumps(chunk)
            hashcode = api.add_pyobj(chunk)
            names += filename+"_block_"+str(i)+" "
            code += hashcode+" "
        remain =  length - start
        if remain > 0:
            chunk = filedata[start:length]
            chunk = CPABEEncrypt(chunk)
            block.append(chunk[0:20])
            start = start + remain
            chunk = pickle.dumps(chunk)
            hashcode = api.add_pyobj(chunk)
            names += filename+"_block_"+str(len(block))+" "
            code += hashcode+" "
        names = names.strip()
        code = code.strip()
        code_arr = code.split(" ")
        names_arr = names.split(" ")
        data = username+"#"+filename+"#"+str(today)+"#"+names+"#"+code+"\n"
        saveDataBlockChain(data,"updates")
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Manufacturer Name</font></th>'
        output+='<th><font size=3 color=black>Software Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Software Block Name</font></th>'
        output+='<th><font size=3 color=black>Encrypted Block Data</font></th>'
        output+='<th><font size=3 color=black>Verification Hashcode</font></th></tr>'
        for i in range(len(block)):
            output+='<tr><td><font size=3 color=black>'+username+'</font></td>'
            output+='<td><font size=3 color=black>'+filename+'</font></td>'
            output+='<td><font size=3 color=black>'+str(today)+'</font></td>'
            output+='<td><font size=3 color=black>'+names_arr[i]+'</font></td>'
            output+='<td><font size=3 color=black>'+str(block[i])+'</font></td>'
            output+='<td><font size=3 color=black>'+code_arr[i]+'</font></td></tr>'
        context= {'data': output}
        return render(request, 'ManufacturerScreen.html', context)
        

def MakePayment(request):
    if request.method == 'GET':
        global username
        manufacturer = request.GET['manufacture']
        software = request.GET['file']
        output = '<tr><td><font size="" color="black">Manufacturer&nbsp;Name</b></td><td><input type="text" name="t1" style="font-family: Comic Sans MS" size="30" value='+manufacturer+' readonly/></td></tr>'   
        output += '<tr><td><font size="" color="black">Software&nbsp;Name</b></td><td><input type="text" name="t2" style="font-family: Comic Sans MS" size="30" value='+software+' readonly/></td></tr>'   
        context= {'data1': output}        
        return render(request, 'MakePayment.html', context)

def MakePaymentAction(request):
    if request.method == 'POST':
        global username
        manufacturer = request.POST.get('t1', False)
        software = request.POST.get('t2', False)
        amount = request.POST.get('t3', False)
        iot = request.POST.get('t4', False)
        today = date.today()
        data = username+"#"+manufacturer+"#"+iot+"#"+amount+"#"+str(today)+"#"+software+"\n"
        saveDataBlockChain(data,"payments")
        context= {'data':'Payment successfully done for IOT '+iot}
        return render(request, 'OwnerScreen.html', context)
        

def PurchaseUpdates(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Manufacturer Name</font></th>'
        output+='<th><font size=3 color=black>Software Updates Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Click Here to Purchase</font></th></tr>'
        readDetails("updates")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
            output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
            output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
            output+='<td><a href=\'MakePayment?manufacture='+arr[0]+'&file='+arr[1]+'\'><font size=3 color=black>Click Here</font></a></td></tr>'
        context= {'data': output}        
        return render(request, 'OwnerScreen.html', context)

def ViewBlocks(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Manufacturer Name</font></th>'
        output+='<th><font size=3 color=black>Software Filename</font></th>'
        output+='<th><font size=3 color=black>Uploading Date</font></th>'
        output+='<th><font size=3 color=black>Software Block Names</font></th>'
        output+='<th><font size=3 color=black>Verification Hash</font></th></tr>'
        readDetails("updates")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td></tr>'
        context= {'data': output}        
        return render(request, 'ManufacturerScreen.html', context)

def ViewPayments(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Owner Name</font></th>'
        output+='<th><font size=3 color=black>Manufacturer Name</font></th>'
        output+='<th><font size=3 color=black>Payment Received for IOT ID</font></th>'
        output+='<th><font size=3 color=black>Amount</font></th>'
        output+='<th><font size=3 color=black>Payment Date</font></th>'
        output+='<th><font size=3 color=black>Purchased Software Filename</font></th></tr>'
        readDetails("payments")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[1] == username:
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>IOT '+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[5]+'</font></td></tr>'
        context= {'data': output}        
        return render(request, 'ManufacturerScreen.html', context)

def ViewOwnerPayments(request):
    if request.method == 'GET':
        global username
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Owner Name</font></th>'
        output+='<th><font size=3 color=black>Manufacturer Name</font></th>'
        output+='<th><font size=3 color=black>Payment Received for IOT ID</font></th>'
        output+='<th><font size=3 color=black>Amount</font></th>'
        output+='<th><font size=3 color=black>Payment Date</font></th>'
        output+='<th><font size=3 color=black>Purchased Software Filename</font></th></tr>'
        readDetails("payments")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username:
                output+='<tr><td><font size=3 color=black>'+arr[0]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[1]+'</font></td>'
                output+='<td><font size=3 color=black>IOT '+arr[2]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[3]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[4]+'</font></td>'
                output+='<td><font size=3 color=black>'+arr[5]+'</font></td></tr>'
        context= {'data': output}        
        return render(request, 'OwnerScreen.html', context)    

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        address = request.POST.get('address', False)
        usertype = request.POST.get('type', False)
        record = 'none'
        readDetails("users")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[1] == username:
                record = "exists"
                break
        if record == 'none':
            data = username+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+usertype+"\n"
            saveDataBlockChain(data,"users")
            context= {'data':'Signup process completed and record saved in Blockchain'}
            return render(request, 'Register.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'Register.html', context)
        
def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        usertype = request.POST.get('type', False)
        status = 'none'
        readDetails("users")
        rows = details.split("\n")
        for i in range(len(rows)-1):
            arr = rows[i].split("#")
            if arr[0] == username and arr[1] == password and usertype == arr[5]:
                status = 'success'
                break
        if status == 'success':
            if usertype == 'Manufacturer':
                context= {'data':"Welcome "+username}
                return render(request, 'ManufacturerScreen.html', context)
            else:
                context= {'data':"Welcome "+username}
                return render(request, 'OwnerScreen.html', context)                
        else:
            if usertype == 'Manufacturer':
                context= {'data':'Invalid login details'}
                return render(request, 'ManufactureLogin.html', context)
            if usertype == 'Owner':
                context= {'data':'Invalid login details'}
                return render(request, 'OwnerLogin.html', context)


        
        



        
            
