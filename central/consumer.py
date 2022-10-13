# implements Kafka topic consumer functionality

from datetime import datetime
import hashlib
import multiprocessing
from random import randrange
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
pincode_comp = False
attempts = 3
destination_point = False
old_id = ''
operation_status = False
coord_array = []

def check_password(hashed_password, user_password):
    password, salt = hashed_password.split(':')
    user_password = str(user_password)
    return password == hashlib.sha256(salt.encode() + user_password.encode()).hexdigest()

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
    
    try:
        delivery_required = False
        if details['operation'] == 'ordering':
            pincode_comp = False
            destination_point = False
            operation_status = False
            attempts = 3
            PIN = details['pincode']
            old_id = details['id']
            details['pincode'] = ''
            x1 = details['x1']
            y1 = details['y1']
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
            "deliver_to": "communication",
            "source": "",
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
            print(f"[central] event {id}, motion start command is sending...")
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
                    "deliver_to": "camera"
                    }
                    _requests_queue.put(camera_details)

                    error_details = {
                    "id": old_id,
                    "operation": "bruteforce",
                    "deliver_to": "monitor"
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
            if (round(details['x'],-1) == 0) and (round(details['y'],-1) == 0):
                result_details = {
                    "id": id,
                    "operation": "operation_status",
                    "deliver_to": "communication"
                    }
                result_details['status'] = operation_status
                _requests_queue.put(result_details)
                delivery_required = False
            elif (round(details['x'],-1) == round(x1,-1)) and (round(details['y'],-1) == round(y1,-1)):
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
                print(f"[error] event {id}, robot is in not correct position! Expected {x1} : {y1} but received {details['x']} : {details['y']}")
        
        elif details['operation'] == 'lock_closing':
            
            camera_details = {
            "id": id,
            "operation": "deactivate",
            "deliver_to": "camera"
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
