#!/usr/bin/python
 
import sys
import datetime
import socket, sys
import json
import base64
import binascii

import http.client,urllib.parse
import requests
 
 
class HttpsClient:
 
    def __init__(self):
        pass
 
    @staticmethod
    def get(_url, _json):
        _resp = requests.get(_url, _json)
        return _resp.content
 
    @staticmethod
    def https_post(_url, _json_dict):
        _resp = requests.post(_url, _json_dict, verify=False)
        return _resp.text
 
    @staticmethod
    def https_post_with_header(_url, _json_dict, _headers):
        _resp = requests.post(_url, data=_json_dict, headers=_headers, verify=False)
        return _resp.text
 
#======================================================       
try:
    import paho.mqtt.client as mqtt
    import paho.mqtt.publish as publish
except ImportError:
    print("MQTT client not find. Please install as follow:")
    print("git clone http://git.eclipse.org/gitroot/paho/org.eclipse.paho.mqtt.python.git")
    print("cd org.eclipse.paho.mqtt.python")
    print("sudo python setup.py install")
 
# 服务器地址
strBroker = "localhost"
# 通信端口
port = 1883
# 用户名
username = 'username'
# 密码
password = 'password'
# 订阅主题名
topic = 'application/1/device/1122334455667789/rx'
 
#======================================================
def on_connect(mqttc, obj, rc):
    pass
    print("OnConnetc, rc: "+str(rc))
 
def on_publish(mqttc, obj, mid):
    pass
    print("OnPublish, mid: "+str(mid))
 
def on_subscribe(mqttc, obj, mid, granted_qos):
    pass
    print("Subscribed: "+str(mid)+" "+str(granted_qos))
 
def on_log(mqttc, obj, level, string):
    pass
    print("Log:"+string)
 
def on_message(mqttc, obj, msg):
    curtime = datetime.datetime.now()
    strcurtime = curtime.strftime("%Y-%m-%d %H:%M:%S")
    print('--------------------recv rx-------------------------')
    print(strcurtime + ": " + msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
    on_exec(msg.payload)
def transmitMQTT(node_topic, strMsg):
    print('--------------------send tx to node-------------------------')
    print('[transmitMQTT] topic:%s, msg:%s' % (node_topic, strMsg))
    strMqttChannel = node_topic
    publish.single(strMqttChannel, strMsg, hostname = strBroker)
 
def on_exec(payload):
    json_str = payload.decode()
    print("Exec:%s" % json_str)


    try:
        json_rx = json.loads(json_str)
    except Exception as e:
        print('[on_exec] in json.loads error')
        print(json_str)
        print(e)
    finally:
        pass
    try:
        dev_eui = json_rx['devEUI']
        app_id = json_rx['applicationID']
    except Exception as e:
        print('[on_exec] maybe this is tx, return')
        return
        raise e
    finally:
        pass
    


    url = "https://1.2.3.4"
#    json_dict = '{"applicationID":"1","applicationName":"caoyue","deviceName":"NFC","devEUI":"1122334455667789","txInfo":{"frequency":867300000,"dr":0},"adr":true,"fCnt":0,"fPort":2,"data":"BAAAXbnFIQ==","object":{"DecodeDataHex":"0x04,0x00,0x00,0x5d,0xb9,0xc5,0x21"}}'
    result = HttpsClient.https_post(url, json_str)
    print('--------------------http response-------------------------')
    print('http result:%s' % result)

    try:
        result_byte = binascii.a2b_hex(result)
        #print(result_byte)
        tx_topic = 'application/%s/device/%s/tx' % (app_id, dev_eui)
        b64_bin = base64.b64encode(result_byte)
        tx_msg = '{"confirmed":true,"fPort":10,"data":"%s" }' % b64_bin.decode()
        transmitMQTT(tx_topic, tx_msg)
    except Exception as e:
        print('some Exception')
        print(e)
        raise e
    finally:
        pass
    # application/20/device/0140000000008888/tx
    # { "confirmed": true, "fPort": 10, "data": "SGVsbG8=" }   base64.b64encode(s)

    
 
#=====================================================
if __name__ == '__main__':
    mqttc = mqtt.Client("test")
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_log = on_log
 
    # 设置账号密码（如果需要的话）
    #mqttc.username_pw_set(username, password=password)
 
    mqttc.connect(strBroker, port, 60)
    mqttc.subscribe(topic, 0)
    mqttc.loop_forever()
