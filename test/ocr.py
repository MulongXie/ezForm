# encoding: utf-8
import time
import sys, io
import re

time1 = time.time()
import urllib, base64
import json


def get_token(API_Key, Secret_Key):
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_Key + '&client_secret=' + Secret_Key
    request = urllib.request.Request(host)
    request.add_header('Content-Type', 'application/json; charset=UTF-8')
    response = urllib.request.urlopen(request)
    content = response.read().decode('utf-8')
    content_json = json.loads(content)
    access_token = content_json['access_token']
    return access_token


def recognition_word_high(filename, access_token):
    url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token=' + access_token
    f = open(filename, 'rb')
    img = base64.b64encode(f.read())
    params = {"image": img}
    params = urllib.parse.urlencode(params).encode(encoding='UTF8')
    request = urllib.request.Request(url, params)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    response = urllib.request.urlopen(request)
    content = response.read()
    if (content):
        # log_id=re.findall('"log_id":"(.*?)"}',str(content),re.S)
        location = re.findall('"location": {(.*?)}', str(content), re.S)
        word = re.findall('"words": "(.*?)"}', str(content), re.S)
        for each_word in word:
            print(each_word.encode().decode())
        for each_location in location:
            print(each_location.encode().decode())
    # url_1='https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/get_request_result?access_token=' + access_token
    # params_1 = {"request_id": request_id[0],"request_type":"excel"}
    # params_1 = urllib.parse.urlencode(params_1).encode(encoding='UTF8')
    # request_1 = urllib.request.Request(url_1, params_1)
    # request_1.add_header('Content-Type', 'application/x-www-form-urlencoded')
    # response_1 = urllib.request.urlopen(request_1)
    # content_1 = response_1.read()
    # if (content_1):
    # print(content_1.decode())
    return word, location


if __name__ == '__main__':
    API_Key = "v6cd6adVIU9WlfSFB2XNiu95"
    Secret_Key = "CQ033fD5YdfArKI96sEBQOqGFBlDjSZC"
    filename = "1.jpg"
    access_token = get_token(API_Key, Secret_Key)
    word, location = recognition_word_high(filename, access_token)