# implements Kafka topic consumer functionality

from datetime import datetime
import multiprocessing
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64


_requests_queue: multiprocessing.Queue = None

def close_lock(id, details, was):
    while True:
        now = time.time()
        if (now-was) >= 5:
            print(f"[lock_closing] event {id}, {now}")
            details['deliver_to'] = 'central'
            details['operation'] = 'lock_closing'
            proceed_to_deliver(id, details)
            break
        else:
            time.sleep(1)


def cleanup_extra_fields(details):
    # remove the blob content from the message payload before sending
    #del details['blob']
    # also remove digest details as it will not be further used
    #del details['digest_alg']
    #del details['digest']
    pass

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        delivery_required = False
        if details['operation'] == 'lock_opening':
            details['deliver_to'] = 'central'
            details['operation'] = 'lock_opening'
            delivery_required = True
            was = time.time();
            print(f"[lock_opening] event {id}, {was}")
            threading.Thread(target=lambda: close_lock(id, details, was)).start()
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    sensors_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(sensors_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            sensors_consumer.assign(partitions)

    # Subscribe to topic
    topic = "sensors"
    sensors_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = sensors_consumer.poll(1.0)
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
        sensors_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
