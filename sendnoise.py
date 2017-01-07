import pika
import sys
import os
import base64
import time
import random

credentials = pika.PlainCredentials('tesis','tesis')
recipientaddr = 'localhost'
#recipientaddr = '192.168.18.133'
portaddr = 5672

parameters = pika.ConnectionParameters(recipientaddr, portaddr,'/',credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='firstqueue')
i = 0

while True:
  message = os.urandom(int(random.uniform(1,20)*3))
  channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      body=message,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  print("%s" % message),
  time.sleep(random.uniform(0,0.5))

connection.close()
#input('Press ENTER to exit')