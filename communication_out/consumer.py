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
import requests

_requests_queue: multiprocessing.Queue = None
UNIC_NAME_COMMUNICATION_OUT = "communication_out"            

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    global UNIC_NAME_COMMUNICATION_OUT
    try:
        details['source'] = UNIC_NAME_COMMUNICATION_OUT
        delivery_required = False
        if details['operation'] == 'set_name':
            
            UNIC_NAME_COMMUNICATION_OUT = details['name']
            #Name.unic_name_motion = details['name']
            delivery_required = False
        elif details['operation'] == 'confirmation':
            data = {
                "status": details['confirmation']
            }
            response = requests.post(
                    "http://fleet:6004/confirmation",
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json", "auth": "very-secure-token"},
            )
            print(f"[communication] event {id}, server answered {response}")    

        elif details['operation'] == 'operation_status':
            data = {
                "status": details['status']
            }
            response = requests.post(
                    "http://fleet:6004/status",
                    data=json.dumps(data),
                    headers={"Content-Type": "application/json", "auth": "very-secure-token"},
            )
            print(f"[communication] event {id}, server answered {response}")
            
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    communication_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(communication_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            communication_consumer.assign(partitions)

    # Subscribe to topic
    topic = "communication_out"
    communication_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = communication_consumer.poll(1.0)
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
        communication_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
