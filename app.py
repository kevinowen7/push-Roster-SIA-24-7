#!/usr/bin/env python


import json
import os
import requests
import datetime
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth

from flask import Flask
from flask import request
from flask import make_response

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

# firebase
cred = credentials.Certificate("./serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://minabot-aceess.firebaseio.com/'
})

#time
now = datetime.datetime.today()

# Flask app should start in global layout
app = Flask(__name__)

line_bot_api = LineBotApi('tRo0KibnDeYJgRVUj01Nnh0+MSCTUhbyZo0HgSwtfRZzGt5Gh0kZUUuiDJkOswWWWsQulRJylBl3seFXcWr10Zu2SJldz8Qxd5sdBxxEQa2k374wJdd1vcNQVrGOusGnFErAt4SPvq4FhZLUdN1vEgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0d184e88d0b01d9a5586b06abd6a1250')

@app.route('/call', methods=['GET'])


def call():
    database = db.reference()
    user = database.child("user")
    x=1
    hasillist=[]
    
    #time
    dateNow = str(datetime.datetime.now()+ timedelta(hours=7)).split(" ")[0]
    time = str(datetime.datetime.now()+ timedelta(hours=7)).split(" ")[1]
    
    #jam 6 pagi baru akan di push
    time6 = time.split(":")[0] 
    menit = time.split(":")[1] 
    if (time6=="06"):
        tahun = int(dateNow.split("-")[0])
        bulan = int(dateNow.split("-")[1])
        hari = int(dateNow.split("-")[2])
        hasil = database.child(str(tahun)+"/"+str(bulan)+"/"+str(hari)).get()
        #end time

        snapshot = user.order_by_key().get()
        for key, val in snapshot.items():
            try:
                matkul= val["matkul"]
                matkul1 = matkul.split("\n")
                for i in matkul1:
                    lt=1
                    while (lt<=5):
                        x=1
                        try:
                            while(x<len(hasil["lantai:"+str(lt)])):
                                if (hasil["lantai:"+str(lt)][x]["Mata Kuliah"]).lower() == i.lower():
                                    if hasil["lantai:"+str(lt)][x]["Nama Dosen"]==" ":
                                        hasillist.append("Jam: "+hasil["lantai:"+str(lt)][x]["Jam"]+"\n"+"Mata Kuliah: "+hasil["lantai:"+str(lt)][x]["Mata Kuliah"]+"\n"+"Ruangan: "+hasil["lantai:"+str(lt)][x]["Ruang"]+"\n"+"\n"+"\n")
                                    else:
                                        hasillist.append("Jam: "+hasil["lantai:"+str(lt)][x]["Jam"]+"\n"+"Mata Kuliah: "+hasil["lantai:"+str(lt)][x]["Mata Kuliah"]+"\n"+"Nama Dosen: "+hasil["lantai:"+str(lt)][x]["Nama Dosen"]+"\n"+"Ruangan: "+hasil["lantai:"+str(lt)][x]["Ruang"]+"\n"+"\n"+"\n")

                                x=x+1
                            print("    ")
                            print("    ")
                            print(len(hasillist))
                            lt=lt+1
                        # jika ltnya loncat langsung lt 2 dst
                        except Exception as res:
                            lt=lt+1

                if hasillist==[]:
                    line_bot_api.push_message(key, TextSendMessage(text=name+" hari ini ("+str(hari)+"/"+str(bulan)+"/"+str(tahun)+") kamu tidak ada kelas :))"))
                else:
                    name = val["name"]
                    r=""
                    for i in hasillist:
                        r=r+i
                    hasillist=[]
                    line_bot_api.push_message(key, TextSendMessage(text=name+" jangan lupa yahh ada kelas hari ini ("+str(hari)+"/"+str(bulan)+"/"+str(tahun)+") : " +"\n"+"\n"+r))
            except Exception as res:
                hasillist=[]
                name = val["name"]
                try:
                    line_bot_api.push_message(key, TextSendMessage(text=name+"Jangan lupa daftarkan Matkul nya ya , supaya bisa Mina ingatkan jadwalnya"))
                #jika gagal push tidak ada matkul
                except Exception as res:
                    print("error")
            
            

    return "Success"



        
    
    
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 4040))

    print ("Starting app on port %d" %(port))

    app.run(debug=False, port=port, host='0.0.0.0')
