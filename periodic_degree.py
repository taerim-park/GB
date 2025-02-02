# Periodical_Status.py
# date : 2022-05-06

from encodings import utf_8
import threading
import requests
import json
import os
import sys
import time
from datetime import datetime
import create

import conf
host = conf.host
port = conf.port
cse = conf.cse
ae = conf.ae
root=conf.root

# string find_pathlist()
# 통계의 대상이 될 파일 path를 return합니다.
# 저장되어있는 json file의 생성일자를 모두 살펴본 후, 가장 최근에 생성된 파일을 골라냅니다.
def find_path(cmeasure):
    path = F"{root}/raw_data/Degree"
    file_list = os.listdir(path)
    present_time = time.time()
    min_value = cmeasure["measureperiod"]*100
    min_index = 0
    if len(file_list)==0:
        print("no data to upload")
        print("waiting...")
        return "0"
    else:
        
        for i in range (len(file_list)):
            file_time = os.path.getmtime(path+'/'+file_list[i])
            time_gap = present_time-file_time
            if time_gap < min_value:
                min_value = time_gap
                min_index = i
        return path+'/'+file_list[min_index]

def read(aename):
    cmeasure = ae[aename]['config']['cmeasure']

    if cmeasure['usefft'] in {'Y','y'}:
        print(f'no fft implementation for {aename}')
    return

    data_path = find_path(cmeasure)
    now = datetime.now()
    
    if data_path != '0':
        with open(data_path) as f:
            json_data = json.load(f)
    
        dmeasure = {}
        dmeasure['val'] = json_data["data"]
        ae[aename]['data']['dmeasure'] = dmeasure

        create.ci(aename, 'data', 'dmeasure')

def report():
    global ae
    print('trigger and fft ')
    for aename in ae:
        read(aename)

