import urllib
import base64
import json
import time


def get_access_token():
    API_Key = "v6cd6adVIU9WlfSFB2XNiu95"
    Secret_Key = "CQ033fD5YdfArKI96sEBQOqGFBlDjSZC"
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + API_Key + '&client_secret=' + Secret_Key
    request = urllib.request.Request(host, headers={'Content-Type':'application/json; charset=UTF-8'})
    response = urllib.request.urlopen(request)
    content = response.read().decode('utf-8')
    content_json = json.loads(content)
    access_token = content_json['access_token']
    return access_token


def ocr_detection(img_file_path):
    start = time.clock()
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
    print('*** OCR Processing Time:%.3f s***' % (time.clock() - start))
    return detection_result


# d = ocr_detection('1.jpg')
# print(d)
