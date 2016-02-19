# coding:utf-8
import pika
from pika.credentials import PlainCredentials
from hichao.base.config import RABBITMQ_CONF


THRONE_SERVER = {
    # rabbitmq
    'RABBITMQ_CONF': {
        'host': '192.168.1.147',
        'port': 5672,
        'queue_name':'search_db_to_esthreads_online',
        'exchange': 'exchange_search_online',
        'routing_key': 'threads.insert',
        'username': 'admin',
        'password': 'pGgEz2V^Gjh#Ol-#-OBjcKJs1~3hh4',
    },
}


class RmqPublisher(object):

    _connection = None
    _channel = None

    @staticmethod
    def close():
        if RmqPublisher._connection:
            try:
                RmqPublisher._connection.close()
            except:
                pass

        if RmqPublisher._channel:
            try:
                RmqPublisher._channel.close()
            except:
                pass

    @staticmethod
    def get_channel(reconnect=False):
        if not RmqPublisher._channel or reconnect:
            RmqPublisher.close()
            RmqPublisher._connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=THRONE_SERVER['RABBITMQ_CONF']['host'],
                port=THRONE_SERVER['RABBITMQ_CONF']['port'],
                credentials=PlainCredentials(THRONE_SERVER['RABBITMQ_CONF']['username'],
                                             THRONE_SERVER['RABBITMQ_CONF']['password'])))
            RmqPublisher._channel = RmqPublisher._connection.channel()
            RmqPublisher._channel.confirm_delivery()
            result = RmqPublisher._channel.queue_declare(queue=THRONE_SERVER['RABBITMQ_CONF']['queue_name'], durable=True)
            RmqPublisher._channel.queue_bind(exchange=THRONE_SERVER['RABBITMQ_CONF']['exchange'],
                                             queue=result.method.queue)
        return RmqPublisher._channel

    @staticmethod
    def publish(msg):
        print 'hello'
        ret = RmqPublisher.get_channel().basic_publish(exchange=THRONE_SERVER['RABBITMQ_CONF']['exchange'],
                                                     routing_key=THRONE_SERVER['RABBITMQ_CONF']['routing_key'],
                                                     body=msg,properties=pika.BasicProperties(content_type='text/plain', delivery_mode=1))
        if not ret:
            print 'publish failed!'
            RmqPublisher.get_channel().basic_publish(exchange=THRONE_SERVER['RABBITMQ_CONF']['exchange'],
                                                     routing_key=THRONE_SERVER['RABBITMQ_CONF']['routing_key'],
                                                     body=msg,properties=pika.BasicProperties(content_type='text/plain', delivery_mode=1))

def send(msg):
    RmqPublisher.publish(msg)

class RabbitMqNew():
    #parameters = pika.URLParameters('amqp://admin:admin@192.168.1.222:5672/%2F')
    # Open a connection to RabbitMQ on localhost using all default parameters
    #connection = pika.BlockingConnection(parameters)
    
    def __init__(self,rabbit_url,pwd = ''):
        self.parameters = pika.URLParameters(rabbit_url)
        if pwd: 
            self.parameters.credentials.password = pwd
        self.connection = pika.BlockingConnection(self.parameters)
        self.channel = self.connection.channel()
        

    def rabbitmq_new(self,queue_name,exchange,routing_key,body):
        self.channel.queue_declare(queue=queue_name, durable=True, exclusive=False, auto_delete=False)
        if self.connection.is_closed:
            #self.parameters = pika.URLParameters(rabbit_url)
            # Open a connection to RabbitMQ on localhost using all default parameters
            self.connection = pika.BlockingConnection(self.parameters)

            # Open the channel
            self.channel = self.connection.channel()

             # Declare the queue
            self.channel.queue_declare(queue=queue_name, durable=True, exclusive=False, auto_delete=False)

        # Turn on delivery confirmations
        self.channel.confirm_delivery()

        # Send a message
        print body
        if self.channel.basic_publish(exchange=exchange,
                             routing_key=routing_key,
                             body=body,
                             properties=pika.BasicProperties(content_type='text/plain',
                                                             delivery_mode=1)):
            print 'Message publish was confirmed'
        else:
            print 'Message could not be confirmed'
            self.channel.basic_publish(exchange=exchange,
                             routing_key=routing_key,
                             body=body,
                             properties=pika.BasicProperties(content_type='text/plain',
                                                             delivery_mode=1))

#rmq_con = RabbitMqNew(RABBITMQ_CONF['rmq_url'],RABBITMQ_CONF.get('rmq_pwd',''))
def get_thread_rab():
    return RabbitMqNew(RABBITMQ_CONF['rmq_url'],RABBITMQ_CONF.get('rmq_pwd',''))
def send_thread(msg):
    rmq = get_thread_rab()
    rmq.rabbitmq_new(queue_name=RABBITMQ_CONF['thread_conf']['queue_name'],exchange=RABBITMQ_CONF['thread_conf']['exchange'],routing_key=RABBITMQ_CONF['thread_conf']['routing_key'],body=msg)

if __name__ == '__main__':
    print 'hello'
    #send('{"token": "testtoken", "user_id": 1}')
    #rm = RabbitMqNew('amqp://admin:admin@192.168.1.222:5672/%2F')
    #for i  in xrange(0,1000):
       #rm.rabbitmq_new(queue_name="exchange_search_v1",exchange='exchange_search_v1',routing_key='threads.insert',body='Hello World!')
    #   print send_thread('hello')
