# implements Kafka topic consumer functionality


import datetime
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from policies import check_operation
from producer import proceed_to_deliver
from policies import UNIC_NAME_MONITOR, UNIC_NAME_CENTRAL

log_error_flag = False

def go_back(id):
    m = {
        'id':id,
        'deliver_to': 'position',
        'operation': 'count_direction',
        'source': 'central',
        'x1': 0,
        'y1': 0
    }
    proceed_to_deliver(id, m)

def handle_event(id, details):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    global log_error_flag
    try:
        text_file = open("/storage/logs.txt", "a+")
        t = time.time()
        text_file.write(f"[{t}] id {id}, {details['source']}->{details['deliver_to']}: {details['operation']}\n")
    except Exception as e:
        print('[error] log failed')
        if not log_error_flag:
            go_back(id)
            log_error_flag = True
    #text_file.write(details + "\n")

    if not ((details['source']=='monitor' or details['source']=='central' or details['source']==UNIC_NAME_MONITOR or details['source']==UNIC_NAME_CENTRAL) 
    and details['deliver_to']=='monitor'):
        if check_operation(id, details):
            proceed_to_deliver(id, details)
        else:
            print("[error] !!!! policies check failed, delivery unauthorized !!! " \
                f"id: {id}, {details['source']}->{details['deliver_to']}: {details['operation']}"
                )
            print(f"[error] suspicious event details: {details}")
            details['deliver_to'] = 'monitor'
            details['operation'] = 'policy_error'
            details['source'] = 'monitor'
            proceed_to_deliver(id, details)


def consumer_job(args, config):
    # Create Consumer instance
    monitor_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(monitor_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            monitor_consumer.assign(partitions)

    # Subscribe to topic
    topic = "monitor"
    monitor_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = monitor_consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    # print("[debug] consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                    #     topic=msg.topic(), key=id, value=details_str))
                    handle_event(id, json.loads(details_str))
                except Exception as e:
                    print(
                        f"[error] malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        monitor_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
