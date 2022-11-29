# implements Kafka topic consumer functionality

from datetime import datetime
import hashlib
import multiprocessing
from random import randrange
from re import X
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64


_requests_queue: multiprocessing.Queue = None
PIN = 0
x1 = 0
y1 = 0
x = 0
y = 0
pincode_comp = False
attempts = 3
destination_point = False
old_id = ''
operation_status = False
coord_array = []
gps_error = False
UNIC_NAME_CENTRAL = "central"

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    user_password = str(user_password)
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

# def check_position(details):
#     if (abs(x-0) < 2) and (abs(y-0) < 2):
#         result_details = {
#             "id": id,
#             "operation": "operation_status",
#             "deliver_to": "communication"
#         }
#         result_details['status'] = operation_status
#         _requests_queue.put(result_details)
#         delivery_required = False
#     elif (abs(x - x1) < 2) and (abs(y - y1) < 2):
#         destination_point = True
#         details['deliver_to'] = 'camera'
#         details['operation'] = 'activate'
#         delivery_required = True
#         print(f"[central] event {id}, robot is in destination point, activating camera...")


def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    global PIN
    global x1
    global y1
    global pincode_comp
    global attempts
    global destination_point
    global old_id
    global operation_status
    global coord_array
    global x
    global y
    global gps_error
    
    global UNIC_NAME_CENTRAL
    try:
        details['source'] = UNIC_NAME_CENTRAL
        delivery_required = False
        if details['operation'] == 'set_name':
            
            UNIC_NAME_CENTRAL = details['name']
            #Name.unic_name_motion = details['name']
            delivery_required = False
        elif details['operation'] == 'ordering':
            pincode_comp = False
            destination_point = False
            operation_status = False
            attempts = 3
            PIN = details['pincode']
            old_id = details['id']
            details['pincode'] = ''
            x1 = details['x1']
            y1 = details['y1']
            x = 0
            y = 0
            gps_error = False
            coord_array = []

            amount = randrange(2, 11)
            for i in range(amount):
                temp_array = [x1/amount*(i+1),y1/amount*(i+1)] 
                coord_array.append(temp_array)
            print(f"[central] event {id}, order to {details['x1']} : {details['y1']} in working...")
            print(coord_array)
            global _requests_queue 
            
            confirmation_details = {
            "id": id,
            "operation": "confirmation",
            "deliver_to": "communication_out",
            "source": UNIC_NAME_CENTRAL,
            "confirmation": True
            }
            _requests_queue.put(confirmation_details)

            details['deliver_to'] = 'position'
            details['operation'] = 'count_direction'
            temp_array = coord_array.pop(0)
            details['x1'] = temp_array.pop(0)
            details['y1'] = temp_array.pop(0)
            print(f"[central] event {id}, order is counting...")
            delivery_required = True


        elif details['operation'] == 'count_direction':
            details['deliver_to'] = 'motion'
            details['operation'] = 'motion_start'
            #print(f"[central] event {id}, motion start command is sending...")
            delivery_required = True

        elif details['operation'] == 'pincoding':
            if destination_point:
                print(f"[central] event {old_id}, checking PIN...")
                #global pincode_comp
                if attempts > 0:
                    attempts-=1
                    if check_password(PIN, str(details['pincode'])):
                        pincode_comp = True
                        details['id'] = old_id
                        details['deliver_to'] = 'sensors'
                        details['operation'] = 'lock_opening'
                        #just for example this is a constant value
                        operation_status = True
                        delivery_required = True
                        print(f"[central] event {old_id}, opening locks...")
                    else: 
                        pincode_comp = False
                        print(f"[central] event {old_id}, wrong PIN detected!")
                else:
                    print(f"[central] event {old_id}, order was blocked!")

                    camera_details = {
                    "id": old_id,
                    "operation": "deactivate",
                    "deliver_to": "camera",
                    "source": UNIC_NAME_CENTRAL
                    }
                    _requests_queue.put(camera_details)

                    error_details = {
                    "id": old_id,
                    "operation": "bruteforce",
                    "deliver_to": "monitor",
                    "source": UNIC_NAME_CENTRAL
                    }
                    _requests_queue.put(error_details)

                    details['id'] = old_id
                    details['deliver_to'] = 'position'
                    details['operation'] = 'count_direction'
                    details['x1'] = 0
                    details['y1'] = 0
                    print(f"[central] event {old_id}, way back is counting...")
                    delivery_required = True
            else:
                details['id'] = old_id
                details['deliver_to'] = 'monitor'
                details['operation'] = 'attention'
                delivery_required = True
        
        elif details['operation'] == 'stop':
            x = details['x']
            y = details['y']
            details['deliver_to'] = 'gps'
            details['operation'] = 'where_am_i'
            delivery_required = True
            # put into location, here use just call location from gps (here we can read mems coordinate)m so stop -> mems
            # if gps_error -> adding new coordinate (how long?) to coord_array and use it as a new point + set flag
            #after point delivering, we will receive error again (or no)
            #so if it's second error - go home
            #else - continue
            # + if gps !+ mems -> message about mistake
            # test's by adding new functionality?
            
        
        elif details['operation'] == 'gps':
            
            if (abs(details['x'] - x) < 2) and (abs(details['y'] - y) < 2):
                gps_error = False
                #check_position(details)
                if (abs(x-0) < 2) and (abs(y-0) < 2):
                    result_details = {
                        "id": id,
                        "operation": "operation_status",
                        "deliver_to": "communication_out",
                        "source": UNIC_NAME_CENTRAL
                    }
                    result_details['status'] = operation_status
                    _requests_queue.put(result_details)
                    delivery_required = False
                elif (abs(x - x1) < 2) and (abs(y - y1) < 2):
                    destination_point = True
                    details['deliver_to'] = 'camera'
                    details['operation'] = 'activate'
                    delivery_required = True
                    print(f"[central] event {id}, robot is in destination point, activating camera...")
                elif coord_array:
                    details['deliver_to'] = 'position'
                    details['operation'] = 'count_direction'
                    temp_array = coord_array.pop(0)
                    details['x1'] = temp_array.pop(0)
                    details['y1'] = temp_array.pop(0)
                    print(f"[central] event {id}, next step is counting...")
                    delivery_required = True
                else:
                    print(f"[error] event {id}, robot is in not in correct position! Expected {x1} : {y1} but received {details['x']} : {details['y']}")
            else:
                #details['x'] = x
                #details['y'] = y
                if gps_error:
                    #coord_array = coord_array.clear()
                    error_details = {
                    "id": old_id,
                    "operation": "gps_error_repeat",
                    "deliver_to": "monitor",
                    "source": UNIC_NAME_CENTRAL
                    }
                    _requests_queue.put(error_details)
                    details['deliver_to'] = 'position'
                    details['operation'] = 'count_direction'
                    details['x1'] = 0
                    details['y1'] = 0
                    print(f"[central] event {id}, way back is counting...")
                    delivery_required = True
                else:
                    gps_error = True
                    error_details = {
                        "id": old_id,
                        "operation": "gps_bad_coord",
                        "deliver_to": "monitor",
                        "source": UNIC_NAME_CENTRAL
                        }
                    _requests_queue.put(error_details)

        elif details['operation'] == 'gps_error':
            if not gps_error:
                if (abs(x-0) < 2) and (abs(y-0) < 2):
                    result_details = {
                        "id": id,
                        "operation": "operation_status",
                        "deliver_to": "communication_out",
                        "source": UNIC_NAME_CENTRAL
                    }
                    result_details['status'] = operation_status
                    _requests_queue.put(result_details)
                    delivery_required = False
                elif (abs(x - x1) < 2) and (abs(y - y1) < 2):
                    destination_point = True
                    details['deliver_to'] = 'camera'
                    details['operation'] = 'activate'
                    delivery_required = True
                    print(f"[central] event {id}, robot is in destination point, activating camera...")
                elif coord_array:
                    details['deliver_to'] = 'position'
                    details['operation'] = 'count_direction'
                    #this code is funny, i know, but i can
                    #temp_array = coord_array.pop(0)
                    #coord_array = coord_array.reverse()
                    temp_coord_x = coord_array[0][0]#temp_array.pop(0)
                    temp_coord_y = coord_array[0][1]#temp_array.pop(0)
                    if temp_coord_x < 0:
                        new_x = temp_coord_x + abs(x - temp_coord_x)/2
                    else: 
                        new_x = temp_coord_x - abs(x - temp_coord_x)/2
                    if temp_coord_y < 0:
                        new_y = temp_coord_y + abs(y - temp_coord_y)/2
                    else: 
                        new_y = temp_coord_y - abs(y - temp_coord_y)/2
                    #coord_array.append(temp_array)
                    #coord_array = coord_array.reverse()
                    details['x1'] = new_x
                    details['y1'] = new_y
                    print(f"[central] event {id}, next step is counting...")
                    delivery_required = True
                else:
                    print(f"[error] it seems u can't be here, please, check code!")
            else:
                #coord_array = coord_array.clear()
                error_details = {
                    "id": old_id,
                    "operation": "gps_error_repeat",
                    "deliver_to": "monitor",
                    "source": UNIC_NAME_CENTRAL
                    }
                _requests_queue.put(error_details)
                details['deliver_to'] = 'position'
                details['operation'] = 'count_direction'
                details['x1'] = 0
                details['y1'] = 0
                print(f"[central] event {id}, way back is counting...")
                delivery_required = True
            gps_error = True

        elif details['operation'] == 'lock_closing':
            
            camera_details = {
            "id": id,
            "operation": "deactivate",
            "deliver_to": "camera",
            "source": UNIC_NAME_CENTRAL
            }
            _requests_queue.put(camera_details)

            details['deliver_to'] = 'position'
            details['operation'] = 'count_direction'
            details['x1'] = 0
            details['y1'] = 0
            print(f"[central] event {id}, way back is counting...")
            delivery_required = True
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config, requests_queue: multiprocessing.Queue):
    # Create Consumer instance
    central_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(central_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            central_consumer.assign(partitions)

    # Subscribe to topic
    topic = "central"
    central_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = central_consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    handle_event(id, details_str)
                except Exception as e:
                    print(
                        f"[error] Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        central_consumer.close()


def start_consumer(args, config, requests_queue):
    global _requests_queue
    _requests_queue = requests_queue
    threading.Thread(target=lambda: consumer_job(args, config, requests_queue)).start()


if __name__ == '__main__':
    start_consumer(None)
