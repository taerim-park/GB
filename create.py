# start.py
# date : 2022-05-06
# 리소스 생성

from encodings import utf_8
import requests
import json
import sys
import os
from datetime import datetime

import conf
host = conf.host
port = conf.port
cse = conf.cse
ae = conf.ae

root=conf.root
slack=""

def ci(aename, cnt, subcnt):
    global ae
    now = datetime.now()
    h={
        "Accept": "application/json",
        "X-M2M-RI": "12345",
        "X-M2M-Origin": "S",
        "Host": F'{host}',
        "Content-Type":"application/vnd.onem2m-res+json;ty=4"
    }
    body={
        "m2m:cin":
        {
            "con": { }
        }
    }
    if cnt in {'config','info','data'}:
        url = F"http://{host}:7579/{cse['name']}/{aename}/{cnt}/{subcnt}"
        body["m2m:cin"]["con"] = ae[aename][cnt][subcnt]
    else:
        url = F"http://{host}:7579/{cse['name']}/{aename}/{cnt}"
        body["m2m:cin"]["con"] = ae[aename][cnt]
    #body["m2m:cin"]["con"]["time"]=now.strftime("%Y-%m-%d %H:%M:%S")
    #print(f'{url} {json.dumps(body)[:40]}')
              
    gotok=False
    try:
        r = requests.post(url, data=json.dumps(body), headers=h)
        r.raise_for_status()
        if "m2m:dbg" in r.json():
            print(f'got error {r.json}')
        else:
            print(f'  created ci {cnt}/{subcnt}/{r.json()["m2m:cin"]["rn"]} \n    ==> {r.json()["m2m:cin"]["con"]}')
            gotok=True
    except requests.exceptions.RequestException as e:
        print(f'failed to ci {e}')


    if gotok and os.path.exists('slackkey.txt'):
        global slack
        if slack=="":
            with open("slackkey.txt") as f: slack=f.read()
            print('activate slack alarm')
        url2=f'http://damoa.io:8999/?msg=created {url}/{r.json()["m2m:cin"]["rn"]}&channel={slack}'
        #print(url2)
        try:
            r = requests.get(url2)
        except requests.exceptions.RequestException as e:
            print(f'failed to slack {e}')

# (ae.323376-TP_A1_01_X, {'info','config'})
def allci(aei, all):
    global ae
    print(f'create ci for containers= {all}')
    for cnti in ae[aei]:
        for subcnti in ae[aei][cnti]:
            if cnti in all:
                print(f'{aei}/{cnti}/{subcnti}')
                ci(aei, cnti, subcnti)

if __name__== "__main__":
    doit()
