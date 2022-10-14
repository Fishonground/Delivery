# implements Kafka topic consumer functionality

from datetime import datetime
import multiprocessing
import random
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64


_requests_queue: multiprocessing.Queue = None
x = 0
y = 0


def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        delivery_required = False
        global x
        global y
        if details['operation'] == 'where_am_i':
            if random.randint(1, 30) <= 25:
                details = {
                'id' : id,
                'deliver_to' : 'central',
                'operation' : 'gps',
                'source' : 'gps',
                'x' : x,
                'y' : y
                }
                delivery_required = True

                extra_details_wrong = {
                'id' : id,
                'deliver_to' : 'central',
                'operation' : 'gps',
                'source' : 'gps',
                'x' : -3,
                'y' : -3
                }
                proceed_to_deliver(id, extra_details_wrong)
                time.sleep(0.1)
                proceed_to_deliver(id, extra_details_wrong)
                # extra_details_correct = {
                # 'id' : id,
                # 'deliver_to' : 'central',
                # 'operation' : 'gps',
                # 'source' : 'gps',
                # 'x' : x,
                # 'y' : y
                # }
                # proceed_to_deliver(id, extra_details_correct)

            else:
                details = {
                'id' : id,
                'deliver_to' : 'central',
                'operation' : 'gps_error',
                'source' : 'gps'
                }
                delivery_required = True
        elif details['operation'] == 'nonexistent':
            x = details['x']
            y = details['y']
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    gps_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(gps_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            gps_consumer.assign(partitions)

    # Subscribe to topic
    topic = "gps"
    gps_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = gps_consumer.poll(1.0)
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
        gps_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
