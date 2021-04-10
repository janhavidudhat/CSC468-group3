import os
import sys
import time
try:
    os.environ["ROUTE_KEY"]
except:
    print("In initial worker container. Waiting to be killed.")
    sys.stdout.flush()
    time.sleep(5)
    sys.exit()

import signal
import pika
import queue
from threading import Thread, Lock
import redis
from rabbitmq.consumer import Consumer
from rabbitmq.publisher import Publisher
from rabbitmq.ThreadCommunication import ThreadCommunication
from legacy.parser import command_parse
from cmd_handler import CMDHandler

# Handles exiting when SIGTERM (sent by ^C input) is received
# in a gracefull way. Main loop will only exit after a completed iteration
# so that every service can shut down properly.
EXIT_PROGRAM = False
# def exit_gracefully(self, signum, frame):
def exit_gracefully(self, signum):
    global EXIT_PROGRAM
    EXIT_PROGRAM = True
signal.signal(signal.SIGINT, exit_gracefully)
signal.signal(signal.SIGTERM, exit_gracefully)

def queue_thread(communication):
     rabbit_queue = Consumer(
         communication=communication,
         connection_param='rabbitmq',
         exchange_name=os.environ["BACKEND_EXCHANGE"],
         queue_name=os.environ["ROUTE_KEY"],
         routing_key=os.environ["ROUTE_KEY"]
     )
     rabbit_queue.run()

def main():
    publisher = Publisher()
    publisher.setup_communication()

    redis_cache = redis.Redis(host='redishost')

    communication = ThreadCommunication(
        buffer=[],
        length=0,
        mutex=Lock()
    )
    command_handler = CMDHandler(response_publisher=publisher, redis_cache=redis_cache)

    t_consumer = Thread(target=queue_thread, args=(communication,))
    t_consumer.start()

    global EXIT_PROGRAM
    while not EXIT_PROGRAM:
        if communication.length > 0:
            buffer = None
            with communication.mutex:
                buffer = communication.buffer
                communication.buffer = []
                communication.length = 0

            for command in buffer:
                result = command_parse(command)
                command_handler.handle_command(result[0], result[1], result[2])

            sys.stdout.flush()

        else:
            time.sleep(0.1)

    t_consumer.join()

if __name__ == "__main__":
    main()
