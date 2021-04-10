from consumer import Consumer
import os
import re
from threading import Lock
import sys

class Confirms():
    def __init__(self, workers, runtime_data):
        self.workers = workers
        self.runtime_data = runtime_data

        self._recv_address = "rabbitmq"
        self._consumer = None

    def connect(self):
        self._consumer = Consumer(
            call_on_callback=self.on_receive,
            connection_param=self._recv_address,
            exchange_name=os.environ["CONFIRMS_EXCHANGE"],
            exchange_type='fanout',
            queue_name="confirm",
            routing_key=""
        )

    def run(self):
        self.connect()
        self._consumer.run()

    def on_receive(self, message):
        #number = re.findall(".*?\[(.*)].*", message)
        #number = int(number[0])

        with self.runtime_data.mutex:
            if self.runtime_data.active_commands > 0:
                self.runtime_data.active_commands -= 1

        # worker_index = abs(hash(command.uid)) % self._NUM_WORKERS
        # self.workers[worker_index].remove(number)
