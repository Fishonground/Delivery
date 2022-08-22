# implements Kafka topic consumer functionality

import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64
from hashlib import sha256


def consumer_job(args, config):
    # Create Consumer instance
    positioning_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(positioning_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            positioning_consumer.assign(partitions)

    # Subscribe to topic
    topic = "positioning"
    positioning_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = positioning_consumer.poll(1.0)
            if msg is None:
                pass
            else: print(f" {topic}: now is working here :)")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        positioning_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
