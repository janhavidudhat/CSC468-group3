from argparse import ArgumentParser
import sys
import signal
import pika
import os
import gzip

''' CLI flags. For normal user based input command testing no flags
are needed. To test a workload file, specify it with the -f flag.
'''
parser = ArgumentParser(
    description='Proxy frontend for parsing and sending workload file to backend'
)
parser.add_argument('-a', '--address',
    dest='address', default='localhost',
    help='IP address for frontend server'
)
parser.add_argument('-p', '--port',
    dest='port', default=1234,
    help='Port for backend server'
)
parser.add_argument('-f', '--file',
    dest='filename',
    help='Workload file to be sent to backend',
    metavar='FILE'
)
parser.add_argument('-v', '--verbose',
    action='store_true' ,dest='verbose', default=False,
    help='Print debug information'
)
parser.add_argument('--route',
    dest='route_key', default='frontend',
    help='Specify routing key used by the exchange'
)
parser.add_argument('--exchange',
    dest='exchange', default='frontend_exchange',
    help='Rabbit queue exchange'
)
args=parser.parse_args()


connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=args.address,
        heartbeat=600,
        blocked_connection_timeout=300
    )
)
channel = connection.channel()
channel.exchange_declare(exchange=args.exchange)

''' Sends file specified in params to the backend server.
Exits once finished.
'''
def send_workload() -> None:
    temp, file_extension = os.path.splitext(args.filename)

    if(file_extension == '.gz'):
        f = gzip.open(args.filename)
        print("TODO: Implement reading from gzip file")

    else:
        f = open(args.filename, 'r')
        for l in f:
            channel.basic_publish(
                exchange=args.exchange,
                routing_key=args.route_key,
                body=l,
                properties=pika.BasicProperties()
            )

''' Keeps application alive and listening for user inputs.
Inputs ending with a newline are sent to the Rabbitmq container.
Only exits once a SIGTERM is received.
'''
def send_user_input() -> None:
    while True:
        user_input = input('Enter Command: ')

        channel.basic_publish(
            exchange=args.exchange,
            routing_key=args.route_key,
            body=user_input,
            properties=pika.BasicProperties()
        )

if __name__=='__main__':
    try:
        if(args.filename is None):
            send_user_input()
        else:
            send_workload()
    except KeyboardInterrupt:
        pass
    finally:
        connection.close()