from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import threading
from time import sleep
import time
import pytest
import re
import json
from urllib.request import urlopen, Request
from uuid import uuid1
import requests
from kafka import KafkaConsumer, KafkaProducer
import sys


messages = []
dict = {}


def listener(event):
    consumer = KafkaConsumer(
            bootstrap_servers=['localhost:9094'], auto_offset_reset='latest'
        )
    consumer.subscribe('monitor')
    global messages
    while not event.is_set():
        try:
            records = consumer.poll(timeout_ms=1000)
            for topic_data, consumer_records in records.items():
                for consumer_record in consumer_records:
                    messages.append(consumer_record.value.decode('utf-8'))
                    #print("Received message: " + str(consumer_record.value.decode('utf-8')))
            continue
        except Exception as e:
            print(e)
            continue

def order():
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200

### Functionally tests
### Yes, it could be done better, but it's just a simple and straightforward realization
### Also, it should be separated for modules, may be?
def test_full_functionality():
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    sleep(2)
    order()
    sleep(50)
    data = {
        "pincode": 12345
    }
    response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    sleep(50)
    event.set()
    thread.join()
    global dict
    global messages
    for m in messages:
        #print(m)
        if str(m).find('"operation": "ordering", "deliver_to": "central", "source": "communication"') > 0 :
            dict['ordering'] = 1
        elif str(m).find('"operation": "confirmation", "deliver_to": "communication", "source": "central"') > 0:
            dict['ordering'] = 2
        elif str(m).find('"operation": "count_direction", "deliver_to": "position", "source": "central"') > 0:
            dict['position'] = 1
        elif str(m).find('"operation": "count_direction", "deliver_to": "central", "source": "position"') > 0:
            dict['position'] = 2
        elif str(m).find('"operation": "motion_start", "deliver_to": "motion", "source": "central"') > 0:
            dict['motion'] = 1
        elif str(m).find('"operation": "motion_start", "deliver_to": "position", "source": "motion"') > 0 :
            dict['motion'] = 2
        elif str(m).find('"operation": "stop", "deliver_to": "position", "source": "motion"') > 0:
            dict['motion'] = 3
        elif str(m).find('"operation": "stop", "deliver_to": "central", "source": "position"') > 0 :
            dict['position'] = 3
        elif str(m).find('"operation": "activate", "deliver_to": "camera", "source": "central"') > 0 :
            dict['camera'] = 1
        elif str(m).find('"operation": "pincoding", "deliver_to": "central", "source": "hmi"') > 0 :
            dict['hmi'] = 1
        elif str(m).find('"operation": "lock_opening", "deliver_to": "sensors", "source": "central"') > 0 :
            dict['sensors'] = 1
        elif str(m).find('"operation": "lock_closing", "deliver_to": "central", "source": "sensors"') > 0 :
            dict['sensors'] = 2
        elif str(m).find('"operation": "deactivate", "deliver_to": "camera", "source": "central"') > 0 :
            dict['camera'] = 2
        elif str(m).find('"operation": "operation_status", "deliver_to": "communication", "source": "central"') > 0 :
            dict['result'] = 1
    #print (dict)
    assert dict['result'] == 1
    messages = []
    #details = json.loads(str(messages[0]))
    #details1 = json.loads(str(messages[1]))
    #assert details['id'] == details1['id'] # id
    ##assert (messages[0]['activate'] == True) or (messages[1]['activate'] == True)
    #messages = []

def test_ordering_block():
    global dict
    assert dict['ordering'] == 2

def test_position_block():
    global dict
    assert dict['position'] == 3

def test_motion_block():
    global dict
    assert dict['motion'] == 3

def test_camera_block():
    global dict
    assert dict['camera'] == 2

def test_hmi_block():
    global dict
    assert dict['hmi'] == 1

def test_sensors_block():
    global dict
    assert dict['sensors'] == 2

### Security test 13 pou of 13, but not all reallized, truthly

#2 
def test_unauthorized_order():
    #for example of part of security - here was an 'auth' header
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json"},
        )    
    assert response.status_code == 401
#3 
def test_incorrect_order():
    time.sleep(5)
    data = {
        "pincode": 12345,
        "x": 5000,
        "y": 5000
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 400

#1 
def test_ddos_communication():
    time.sleep(5)
    #generally, here should be also network security by host, for example, IP white_list
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    sleep(2)
    #order
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 200
    for i in range(1,8):
        response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
        assert response.status_code == 504
    sleep(3)
    event.set()
    thread.join()
    #global messages
    #for m in messages:
    #    print(m)
    sleep(50)
    data = {
        "pincode": 12345
    }
    response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    messages = []
#4 
def test_third_party_attack():
    #tbd validation
    pass
#5 
def test_communication_hacking():
    #isn't availible for nowtime
    pass
#6 
def test_repeating_order():
    time.sleep(50)
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    sleep(2)
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 200
    time.sleep(5)
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 200
    sleep(2)
    event.set()
    thread.join()
    global messages
    global dict
    for m in messages:
        if str(m).find('operation": "reordering", "deliver_to": "monitor", "source": "monitor"') > 0 :
            dict['reordering'] = 1
    sleep(50)
    data = {
        "pincode": 12345
    }
    response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    assert dict['reordering'] == 1
    messages = []
    dict = {}
#7 
def test_inaction():
    #this is a good question, what should we do with this problem
    #I'm thinking about some watchdog, which will restart components?)
    pass
#8 
def test_hidden_fields():
    pass
#9 
def test_gps_broken():
    #isn't availible for nowtime
    pass
#10 
def test_password_not_in_destination_point():
    time.sleep(50)
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    sleep(2)
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 200
    global messages
    global dict
    sleep(4)
    data = {
        "pincode": 123456
    }
    response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    time.sleep(1)
    event.set()
    thread.join()
    sleep(50)
    data = {
        "pincode": 12345
    }
    response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    
    assert response.status_code == 200
    for m in messages:
        if str(m).find('operation": "attention", "deliver_to": "monitor", "source": "central"') > 0 :
            dict['attention'] = 1
    assert dict['attention'] == 1
    messages = []
    dict = {}
#11 
def test_bruteforce():
    time.sleep(50)
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    sleep(2)
    data = {
        "pincode": 12345,
        "x": 64,
        "y": 32
    }
    response = requests.post(
        "http://0.0.0.0:6008/ordering",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
    assert response.status_code == 200
    global messages
    global dict
    sleep(40)
    data = {
        "pincode": 123456
    }
    for i in range(1,4):
        response = requests.post(
        "http://localhost:6006/pincoding",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
        )    
        assert response.status_code == 200
    time.sleep(1)
    event.set()
    thread.join()
    for m in messages:
        if str(m).find('operation": "bruteforce", "deliver_to": "monitor", "source": "central"') > 0 :
            dict['bruteforce'] = 1
    assert dict['bruteforce'] == 1
    messages = []
    dict = {}
#12 
def test_component_lie():
    #isn't availible for nowtime
    pass
#13 
def test_sensitive_output():
    #can be tested only by hands adding this information into the system,
    #cause this test suggests checking of compensation the SUCCESSFULL attack result
    #tbd validation
    pass




# def test_write_order():
#     sleep(5)
#     event = threading.Event()
#     thread = threading.Thread(target=lambda: listener(event))
#     thread.start()
#     time.sleep(5)
#     activate()
#     sleep(1)
#     event.set()
#     thread.join()
#     global messages
#     details = json.loads(str(messages[0]))
#     assert (details['operation'] == 'activate')
#     details = json.loads(str(messages[1]))
#     assert (details['operation'] == 'ask_task') # operation
#     messages = []
#     deactivate()

# ### Action tests
# def send_task():
#     data = {
#         "x1": 50,
#         "y1": 50,
#         "z1": 10,
#         "expenditure": 10,
#         "x2": 55,
#         "y2": 55,
#         "z2": 10,
#         "close_key": 12345
#     }
#     response = requests.post(
#         "http://0.0.0.0:6009/new-task",
#         data=json.dumps(data),
#         headers={"Content-Type": "application/json", "auth": "very-secure-token"},
#     )


# def test_success_result():
#     sleep(10)
#     event = threading.Event()
#     activate()
#     time.sleep(5)
#     thread = threading.Thread(target=lambda: listener(event))
#     thread.start()
#     time.sleep(5)
#     send_task()
#     time.sleep(120)
#     event.set()
#     thread.join()
#     global messages
#     assert len(messages) == 13
#     details = json.loads(str(messages[0]))
#     details1 = json.loads(str(messages[len(messages)-1]))
#     assert details['id'] == details1['id'] # id
#     assert (details1['operation'] == 'operation_status')
#     messages = []
#     deactivate()

# def test_surface_result():
#     time.sleep(10)
#     event = threading.Event()
#     activate()
#     time.sleep(5)
#     thread = threading.Thread(target=lambda: listener(event))
#     thread.start()
#     time.sleep(5)
#     send_task()
#     time.sleep(120)
#     event.set()
#     thread.join()
#     global messages
#     details = json.loads(str(messages[len(messages)-1]))
#     fields_max = 300/details['expenditure']
#     fields = 0
#     for s in details['surface']:
#         for f in s:
#             if f == 'X': 
#                 fields+=1
#     assert fields_max >= fields 
#     messages = []
#     deactivate()



#     ### security tests

# def test_activate_without_token():
#     time.sleep(10)
#     data = {
#         "somedata": "test"
#     }
#     response = requests.post(
#         "http://0.0.0.0:6009/activate",
#         data=json.dumps(data),
#         headers={"Content-Type": "application/json", "auth": "blablabla"},
#     )
#     assert response.status_code == 401
#     deactivate()

# def send_wrong_task():
#     data = {
#         "x1": 50,
#         "y1": 50,
#         "z1": 10,
#         "expenditure": 10,
#         "x2": 55,
#         "y2": 55,
#         "z2": 10,
#         "close_key": 5467
#     }
#     response = requests.post(
#         "http://0.0.0.0:6009/new-task",
#         data=json.dumps(data),
#         headers={"Content-Type": "application/json", "auth": "very-secure-token"},
#     )

# def test_bruteforce():
#      time.sleep(10)
#      event = threading.Event()
#      activate()
#      time.sleep(5)
#      thread = threading.Thread(target=lambda: listener(event))
#      thread.start()
#      time.sleep(5)
#      send_wrong_task()
#      time.sleep(1)
#      send_wrong_task()
#      time.sleep(1)
#      send_wrong_task()
#      time.sleep(1)
#      send_wrong_task()
#      time.sleep(3)
#      event.set()
#      thread.join()
#      global messages
#      details = json.loads(str(messages[len(messages)-1]))
#      assert details['operation'] == 'error' # id
#      assert details['err_msg'] == 'Task is under bruteforce!'
#      messages = []
#      deactivate()

# def test_repeated_task():
#     time.sleep(10)
#     event = threading.Event()
#     activate()
#     time.sleep(5)
#     thread = threading.Thread(target=lambda: listener(event))
#     thread.start()
#     time.sleep(5)
#     send_task()
#     time.sleep(2)
#     send_task()
#     time.sleep(2)
#     event.set()
#     thread.join()
#     global messages
#     #print(messages)
#     details = json.loads(str(messages[len(messages)-1]))
#     assert details['operation'] == 'task'
#     messages = []
#     deactivate()

    