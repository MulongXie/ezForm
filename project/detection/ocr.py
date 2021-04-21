import urllib
import base64
import json
import time
import requests
import cv2
import os
from base64 import b64encode


# ******** Baidu *********
def get_access_token():
    API_Key = "v6cd6adVIU9WlfSFB2XNiu95"  # iyyblNxLrtFBowE8FfRNo3Fm
    Secret_Key = "CQ033fD5YdfArKI96sEBQOqGFBlDjSZC"  # MNTGdNPpvyhZC5CUcOQ5y4Yj1HbQ1t5m
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_Key + '&client_secret=' + Secret_Key
    request = urllib.request.Request(host, headers={'Content-Type':'application/json; charset=UTF-8'})
    response = urllib.request.urlopen(request)
    content = response.read().decode('utf-8')
    content_json = json.loads(content)
    access_token = content_json['access_token']
    return access_token


def ocr_detection_baidu(img_file_path):
    access_token = get_access_token()
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=' + access_token
    f = open(img_file_path, 'rb')
    img = base64.b64encode(f.read())
    params = urllib.parse.urlencode({"image": img}).encode(encoding='UTF8')
    request = urllib.request.Request(url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    response = urllib.request.urlopen(request)
    detection_result = response.read().decode(encoding='UTF8')
    if detection_result:
        detection_result = json.loads(detection_result)
    return detection_result


# ******** Google *********
def Google_OCR_makeImageData(imgpath):
    with open(imgpath, 'rb') as f:
        ctxt = b64encode(f.read()).decode()
        img_req = {
            'image': {
                'content': ctxt
            },
            'features': [{
                # 'type': 'DOCUMENT_TEXT_DETECTION',
                'type': 'TEXT_DETECTION',
                'maxResults': 1
            }]
        }
    return json.dumps({"requests": img_req}).encode()


def ocr_detection_google(img):
    imgpath = 'data/output/temp.jpg'
    cv2.imwrite(imgpath, img)
    url = 'https://vision.googleapis.com/v1/images:annotate'
    api_key = 'AIzaSyAxjrH4Me8dQCC6BTtxHFcUphWHPNR2VGQ'
    imgdata = Google_OCR_makeImageData(imgpath)
    response = requests.post(url,
                             data=imgdata,
                             params={'key': api_key},
                             headers={'Content_Type': 'application/json'})
    os.remove(imgpath)
    if response.json()['responses'] == [{}]:
        # No Text
        return None
    else:
        return response.json()['responses'][0]['textAnnotations'][1:]
