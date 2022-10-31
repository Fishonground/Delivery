# implements Kafka topic consumer functionality

from datetime import datetime
import math
import multiprocessing
from random import randrange
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64
UNIC_NAME_POSITION = "position"

_requests_queue: multiprocessing.Queue = None
x_coord = 0
y_coord = 0

def where_am_i():
    pass

            

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    global x_coord
    global y_coord
    global UNIC_NAME_POSITION
    try:
        details['source'] = UNIC_NAME_POSITION
        delivery_required = False
        if details['operation'] == 'set_name':
            
            UNIC_NAME_POSITION = details['name']
            #Name.unic_name_motion = details['name']
            delivery_required = False
        elif details['operation'] == 'count_direction':
            details['deliver_to'] = 'central'
            details['operation'] = 'count_direction'
            dx_target = details['x1'] - x_coord
            dy_target = details['y1'] - y_coord
            details['direction'] = math.atan2(dy_target, dx_target)
            details['distance'] = math.sqrt(dx_target**2 + dy_target**2)
            details['speed'] = randrange(9)+1
            print(f"[count_direction] event {id}, {details['distance']} to {details['direction']} with speed {details['speed']}")
            delivery_required = True
        elif details['operation'] == 'location':
            details['deliver_to'] = 'central'
            details['operation'] = 'location'
            details['x'] = x_coord
            details['y'] = y_coord
            delivery_required = True
            print(f"[location] event {id}, locate in {details['x']} : {details['y']}")
        elif details['operation'] == 'motion_start':
            print(f"[motion] event {id}, confirmed motion to {details['direction']} with speed {details['speed']}, awaiting in {details['time']}")
        elif details['operation'] == 'stop':
            x_coord += math.cos(details['direction']) * details['distance']
            y_coord += math.sin(details['direction']) * details['distance']
            details['deliver_to'] = 'central'
            details['operation'] = 'stop'
            details['x'] = x_coord
            details['y'] = y_coord
            delivery_required = True

            gps_details = {
            "id": id,
            "operation": "nonexistent",
            "deliver_to": "gps",
            "source": UNIC_NAME_POSITION,
            "x": x_coord,
            "y": y_coord
            }
            proceed_to_deliver(id, gps_details)
            #_requests_queue.put(gps_details)
            
            print(f"[location] event {id}, stopped in {details['x']} : {details['y']}")
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    position_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(position_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            position_consumer.assign(partitions)

    # Subscribe to topic
    topic = "position"
    position_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = position_consumer.poll(1.0)
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
        position_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
