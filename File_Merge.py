# File_Merge.py
# 1초단위의 데이터들을 생성시각에 따라, rawperiod에 기반해 하나의 data로 묶어 저장합니다.
# 파일의 생성시각을 읽어오는 방식을 사용하고 있어 개선이 필요합니다.
# 현재 delay에 의한 데이터 누락에 대한 대책이 없음. raw_*.py처럼 last_timestamp를 백업해두고 사용하는 방식이 제일 용이해보임. conf.py에 백업하는 게 좋을까요?
# 추후 통합한 파일을 http file server에 자연스럽게 전송하면 되지 않을까... 하고 생각 중.
# 비슷한 원리로 파일 정리 시스템도 만들 예정(초단위 데이터 청소)


from calendar import c
from encodings import utf_8
import threading
import requests
import json
import os
import sys
import time
from datetime import datetime
import numpy as np
import conf

ae = conf.ae
root = conf.root

def sensor_type(aename):
    return aename.split('-')[1][0:2]

# 통합할 파일 list 작성
def filepath_list(aename, rawperiod): # 가장 최근 rawperiod간의 파일을 뽑는다
    raw_path = F"{root}/raw_data"
    if aename == "AC" :
        raw_path+="/Acceleration"
    elif aename == "DI" :
        raw_path+="/Displacement"
    elif aename == "TP" :
        raw_path+="/Temperature"
    elif aename == "TI" :
        raw_path+="/Degree"
    else :
        print("aename error")
        return

    file_list = os.listdir(raw_path)
    present_time = time.time()
    data_path_list = list()
    for i in range (len(file_list)):
        file_time = os.path.getmtime(raw_path+'/'+file_list[i])
        time_gap = present_time-file_time
        if time_gap <= rawperiod: # rawperiod에 따라 data를 수집한다. 기본값 60분
            data_path_list.append(raw_path+'/'+file_list[i])
            #print(file_list[i])
    data_path_list.sort()
    return data_path_list

def file_save(aename, rawperiod):
    save_path = F"{root}/merged_data"
    if aename == "AC" :
        save_path+="/Acceleration"
    elif aename == "DI" :
        save_path+="/Displacement"
    elif aename == "TP" :
        save_path+="/Temperature"
    elif aename == "TI" :
        save_path+="/Degree"
    else :
        print("aename error")
        return
    
    #통합 데이터를 저장할 디렉토리가 없다면 생성
    if not os.path.exists(save_path): os.makedirs(save_path)

    #통합할 데이터 list를 불러온다
    data_path_list = filepath_list(aename, rawperiod) 

    if len(data_path_list) == 0:
        print("no data to merge") #통합할 데이터가 전혀 없는 경우, 통합을 수행하지 않음
        print("waiting...")
        return

    empty_list = list() # time, data값이 dict 형태로 삽입될 배열
    
    merged_file = { # 최종적으로 rawperiod간의 데이터가 저장될 json의 dict
        "starttime":"",
        "endtime":"",
        "data":empty_list 
    }

    # 통합 대상인 파일을 하나씩 불러온다
    for file in range(len(data_path_list)):
        with open(data_path_list[file], "rb") as f:
            one_file = json.loads(f.read().decode('utf_8'))
            if file == 0:
                merged_file["starttime"] = one_file["time"]
            elif file == len(data_path_list)-1:
                merged_file["endtime"] = one_file["time"] # 가장 첫 파일과 가장 마지막 파일의 숫자를 기록한다
            
            data_file = {
                "time":one_file["time"],
                "data":one_file["data"]
            }

            merged_file["data"].append(data_file) # "data" value의 리스트에 data_file을 추가한다
            

    now = datetime.now()
    file_name = aename+now.strftime("-%Y%m%d%H%M")
    with open (F"{save_path}/inoon-{file_name}", "w") as f:
        json.dump(merged_file, f, indent=4)
        
def doit():
    for aename in ae:
        rawperiod = ae[aename]["config"]["cmeasure"]["rawperiod"]
        file_save(sensor_type(aename), rawperiod)
    
    


