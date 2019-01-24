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



@app.route('/call', methods=['GET'])


def call():
    #time
    dateNow = str(datetime.datetime.now()+ timedelta(hours=7)).split(" ")[0]
    driver = webdriver.PhantomJS();
    driver.get('https://akademik.ithb.ac.id/default.php?mod=roster%20ruangan')
    bulan = 1
    if (bulan==1)or(bulan==3)or(bulan==5)or(bulan==7)or(bulan==8)or(bulan==10)or(bulan==12):
        tgl = 1;
        while(tgl<=31):
            lt = 1
            while lt<6:
                select = Select(driver.find_element_by_name("tgl"))
                select.select_by_value(str(tgl))
                select = Select(driver.find_element_by_name("bln"))
                select.select_by_value(str(bulan))
                select = Select(driver.find_element_by_name("thn"))
                select.select_by_value("2019")
                select = Select(driver.find_element_by_name("lantai"))
                select.select_by_value(str(lt))
                driver.find_element_by_name("cmd").click()
                return "suksessss"
                database1 = database.child("2019/"+str(bulan)+"/"+str(tgl)+"/lantai:"+str(lt))
                soup = BeautifulSoup(driver.page_source,'html.parser')
                x = soup.find_all("tbody")
                tempat = str(x[9]).split("<tr>")[4]
                w = tempat.split("<tbody>")[1]
                #tempat
                r=[]
                i=2
                add = w.split(">")
                while i<len(add):
                    r.append(w.split(">")[i].split("<")[0])
                    i=i+2
                #ruangan
                jadwal =[]
                SKSL = []
                Lruangan = []
                loop=5
                j=0
                while loop<31:
                    p1 = str(x[9]).split("<tr>")[loop]
                    jam = p1.split("</td>")[0].split('"')[12].split("<")[0].split(">")[1]
                    i=0
                    Lruangan.append([])
                    while i<len(r):
                        try:
                            row = p1.split("</td>")[i].split('"')
                            print(row)
                            if (len(row)>3):
                                if row[3]=="#FFCC66":
                                    Lruangan[j].append("1")
                                    SKS = int(row[7])/2
                                    SKSL.append(int(row[7]))
                                    kode = row[10].split("<")[0].split(">")[1]
                                    if len(row)>18:
                                        dosen = row[12].split("<")[0].split(">")[1]
                                        dosen1 = row[14].split("<")[0].split(">")[1]
                                        dosen2 = row[16].split("<")[0].split(">")[1]
                                        dosen3 = row[18].split("<")[0].split(">")[1]
                                        jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\n"+dosen3+"\\"+str(SKS)+"\\" "\\"+jam)
                                    elif len(row)>16:
                                        dosen = row[12].split("<")[0].split(">")[1]
                                        dosen1 = row[14].split("<")[0].split(">")[1]
                                        dosen2 = row[16].split("<")[0].split(">")[1]
                                        jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\\"+str(SKS)+"\\" "\\"+jam)
                                    elif len(row)>14:
                                        dosen = row[12].split("<")[0].split(">")[1]
                                        dosen1 = row[14].split("<")[0].split(">")[1]
                                        jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\\"+str(SKS)+"\\" "\\"+jam)
                                    elif len(row)>12:
                                        dosen = row[12].split("<")[0].split(">")[1]
                                        jadwal.append(kode+"\\"+dosen+"\\"+str(SKS)+"\\" "\\"+jam)
                                    else:
                                        jadwal.append(kode+"\\"+" \\"+str(SKS)+"\\" "\\"+jam)
                                else:
                                    Lruangan[j].append("0")
                            i=i+1
                        except Exception as res:
                            i=i+1
                            print("error")
                    loop=loop+1
                    j=j+1
                print(Lruangan)
                print(jadwal)
                #set array jam
                set1 = 0
                while set1<26:
                    d=0
                    while d<len(Lruangan[set1]):
                        if Lruangan[set1][d]=="1":
                            dd=1
                            set2=set1
                            while dd<SKSL[0]:
                                try:
                                    Lruangan[set2+1].insert(d,"2")
                                    set2=set2+1
                                    dd=dd+1
                                except Exception as rrr:
                                    set2=set2+1
                                    dd=dd+1
                            SKSL.pop(0)
                        d=d+1
                    set1=set1+1

                #get room
                ROOM = []
                set1=0
                while set1<26:
                    d=0
                    while d<len(Lruangan[set1]):
                        if Lruangan[set1][d]=="1":
                            ROOM.append(r[d])
                        d=d+1
                    set1=set1+1

                #hasil to firebase
                hasil=""
                kode=""
                loop=0
                urutan=0
                while loop<len(jadwal):
                    hasil = jadwal[loop]
                    ruanganA = ROOM[loop]
                    loop = loop+1
                    urutan=urutan+1
                    kode=hasil.split("\\")
                    #mulai jam pelajaran
                    mulai = kode[4].split("-")[0]
                    print(mulai.split("."))
                    mulai1 = int(mulai.split(".")[0])
                    mulai2 = int(mulai.split(".")[1])
                    #lama jam pelajaran
                    sks = kode[2].split(".")
                    #perhitungan lama pelajaran
                    sks1 = int(sks[0])
                    #lama pelajaran x.5 jam
                    if sks[1]=="0":
                        lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2)+"0"
                    else:
                        if mulai2==30:
                            lama_matkul = mulai+" - "+str(mulai1+sks1+1)+".00"
                        else:
                            lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2+30)
                    database1.update({str(urutan) :{
                                        "Mata Kuliah":kode[0],
                                        "Nama Dosen":kode[1],
                                        "Ruang":ruanganA,
                                        "Jam": lama_matkul
                                        }
                                    })
                lt=lt+1
            tgl=tgl+1
    else:
        if (bulan==2):
            tgl = 1;
            while(tgl<=28):
                lt = 1
                while lt<6:
                    select = Select(driver.find_element_by_name("tgl"))
                    select.select_by_value(str(tgl))
                    select = Select(driver.find_element_by_name("bln"))
                    select.select_by_value(str(bulan))
                    select = Select(driver.find_element_by_name("thn"))
                    select.select_by_value("2019")
                    select = Select(driver.find_element_by_name("lantai"))
                    select.select_by_value(str(lt))
                    driver.find_element_by_name("cmd").click()

                    database1 = database.child("2019/"+str(bulan)+"/"+str(tgl)+"/lantai:"+str(lt))
                    soup = BeautifulSoup(driver.page_source,'html.parser')
                    x = soup.find_all("tbody")
                    tempat = str(x[9]).split("<tr>")[4]
                    w = tempat.split("<tbody>")[1]
                    #tempat
                    r=[]
                    i=2
                    add = w.split(">")
                    while i<len(add):
                        r.append(w.split(">")[i].split("<")[0])
                        i=i+2
                    #ruangan
                    jadwal =[]
                    SKSL = []
                    Lruangan = []
                    loop=5
                    j=0
                    while loop<31:
                        p1 = str(x[9]).split("<tr>")[loop]
                        jam = p1.split("</td>")[0].split('"')[12].split("<")[0].split(">")[1]
                        i=0
                        Lruangan.append([])
                        while i<len(r):
                            try:
                                row = p1.split("</td>")[i].split('"')
                                print(row)
                                if (len(row)>3):
                                    if row[3]=="#FFCC66":
                                        Lruangan[j].append("1")
                                        SKS = int(row[7])/2
                                        SKSL.append(int(row[7]))
                                        kode = row[10].split("<")[0].split(">")[1]
                                        if len(row)>18:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            dosen2 = row[16].split("<")[0].split(">")[1]
                                            dosen3 = row[18].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\n"+dosen3+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>16:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            dosen2 = row[16].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>14:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>12:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\\"+str(SKS)+"\\" "\\"+jam)
                                        else:
                                            jadwal.append(kode+"\\"+" \\"+str(SKS)+"\\" "\\"+jam)
                                    else:
                                        Lruangan[j].append("0")
                                i=i+1
                            except Exception as res:
                                i=i+1
                                print("error")
                        loop=loop+1
                        j=j+1
                    print(Lruangan)
                    #set array jam
                    set1 = 0
                    while set1<26:
                        d=0
                        while d<len(Lruangan[set1]):
                            if Lruangan[set1][d]=="1":
                                dd=1
                                set2=set1
                                while dd<SKSL[0]:
                                    try:
                                        Lruangan[set2+1].insert(d,"2")
                                        set2=set2+1
                                        dd=dd+1
                                    except Exception as rrr:
                                        set2=set2+1
                                        dd=dd+1
                                SKSL.pop(0)
                            d=d+1
                        set1=set1+1

                    #get room
                    ROOM = []
                    set1=0
                    while set1<26:
                        d=0
                        while d<len(Lruangan[set1]):
                            if Lruangan[set1][d]=="1":
                                ROOM.append(r[d])
                            d=d+1
                        set1=set1+1

                    #hasil to firebase
                    hasil=""
                    kode=""
                    loop=0
                    urutan=0
                    while loop<len(jadwal):
                        hasil = jadwal[loop]
                        ruanganA = ROOM[loop]
                        loop = loop+1
                        urutan=urutan+1
                        kode=hasil.split("\\")
                        #mulai jam pelajaran
                        mulai = kode[4].split("-")[0]
                        mulai1 = int(mulai.split(".")[0])
                        mulai2 = int(mulai.split(".")[1])
                        #lama jam pelajaran
                        sks = kode[2].split(".")
                        #perhitungan lama pelajaran
                        sks1 = int(sks[0])
                        #lama pelajaran x.5 jam
                        if sks[1]=="0":
                            lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2)+"0"
                        else:
                            if mulai2==30:
                                lama_matkul = mulai+" - "+str(mulai1+sks1+1)+".00"
                            else:
                                lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2+30)
                        database1.update({str(urutan) :{
                                            "Mata Kuliah":kode[0],
                                            "Nama Dosen":kode[1],
                                            "Ruang":ruanganA,
                                            "Jam": lama_matkul
                                            }
                                        })
                    lt=lt+1
                tgl=tgl+1
        else:
            tgl = 1;
            while(tgl<=30):
                lt = 1
                while lt<6:
                    select = Select(driver.find_element_by_name("tgl"))
                    select.select_by_value(str(tgl))
                    select = Select(driver.find_element_by_name("bln"))
                    select.select_by_value(str(bulan))
                    select = Select(driver.find_element_by_name("thn"))
                    select.select_by_value("2019")
                    select = Select(driver.find_element_by_name("lantai"))
                    select.select_by_value(str(lt))
                    driver.find_element_by_name("cmd").click()

                    database1 = database.child("2019/"+str(bulan)+"/"+str(tgl)+"/lantai:"+str(lt))
                    soup = BeautifulSoup(driver.page_source,'html.parser')
                    x = soup.find_all("tbody")
                    tempat = str(x[9]).split("<tr>")[4]
                    w = tempat.split("<tbody>")[1]
                    #tempat
                    r=[]
                    i=2
                    add = w.split(">")
                    while i<len(add):
                        r.append(w.split(">")[i].split("<")[0])
                        i=i+2
                    #ruangan
                    jadwal =[]
                    SKSL = []
                    Lruangan = []
                    loop=5
                    j=0
                    while loop<31:
                        p1 = str(x[9]).split("<tr>")[loop]
                        jam = p1.split("</td>")[0].split('"')[12].split("<")[0].split(">")[1]
                        i=0
                        Lruangan.append([])
                        while i<len(r):
                            try:
                                row = p1.split("</td>")[i].split('"')
                                print(row)
                                if (len(row)>3):
                                    if row[3]=="#FFCC66":
                                        Lruangan[j].append("1")
                                        SKS = int(row[7])/2
                                        SKSL.append(int(row[7]))
                                        kode = row[10].split("<")[0].split(">")[1]
                                        if len(row)>18:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            dosen2 = row[16].split("<")[0].split(">")[1]
                                            dosen3 = row[18].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\n"+dosen3+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>16:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            dosen2 = row[16].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\n"+dosen2+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>14:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            dosen1 = row[14].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\n"+dosen1+"\\"+str(SKS)+"\\" "\\"+jam)
                                        elif len(row)>12:
                                            dosen = row[12].split("<")[0].split(">")[1]
                                            jadwal.append(kode+"\\"+dosen+"\\"+str(SKS)+"\\" "\\"+jam)
                                        else:
                                            jadwal.append(kode+"\\"+" \\"+str(SKS)+"\\" "\\"+jam)
                                    else:
                                        Lruangan[j].append("0")
                                i=i+1
                            except Exception as res:
                                i=i+1
                                print("error")
                        loop=loop+1
                        j=j+1
                    print(Lruangan)
                    #set array jam
                    set1 = 0
                    while set1<26:
                        d=0
                        while d<len(Lruangan[set1]):
                            if Lruangan[set1][d]=="1":
                                dd=1
                                set2=set1
                                while dd<SKSL[0]:
                                    try:
                                        Lruangan[set2+1].insert(d,"2")
                                        set2=set2+1
                                        dd=dd+1
                                    except Exception as rrr:
                                        set2=set2+1
                                        dd=dd+1
                                SKSL.pop(0)
                            d=d+1
                        set1=set1+1

                    #get room
                    ROOM = []
                    set1=0
                    while set1<26:
                        d=0
                        while d<len(Lruangan[set1]):
                            if Lruangan[set1][d]=="1":
                                ROOM.append(r[d])
                            d=d+1
                        set1=set1+1

                    #hasil to firebase
                    hasil=""
                    kode=""
                    loop=0
                    urutan=0
                    while loop<len(jadwal):
                        hasil = jadwal[loop]
                        ruanganA = ROOM[loop]
                        loop = loop+1
                        urutan=urutan+1
                        kode=hasil.split("\\")
                        #mulai jam pelajaran
                        mulai = kode[4].split("-")[0]
                        mulai1 = int(mulai.split(".")[0])
                        mulai2 = int(mulai.split(".")[1])
                        #lama jam pelajaran
                        sks = kode[2].split(".")
                        #perhitungan lama pelajaran
                        sks1 = int(sks[0])
                        #lama pelajaran x.5 jam
                        if sks[1]=="0":
                            lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2)+"0"
                        else:
                            if mulai2==30:
                                lama_matkul = mulai+" - "+str(mulai1+sks1+1)+".00"
                            else:
                                lama_matkul = mulai+" - "+str(mulai1+sks1)+"."+str(mulai2+30)
                        database1.update({str(urutan) :{
                                            "Mata Kuliah":kode[0],
                                            "Nama Dosen":kode[1],
                                            "Ruang":ruanganA,
                                            "Jam": lama_matkul
                                            }
                                        })
                    lt=lt+1
                tgl=tgl+1
    driver.close()
    return "Success"



        
    
    
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 4040))

    print ("Starting app on port %d" %(port))

    app.run(debug=False, port=port, host='0.0.0.0')
