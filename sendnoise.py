import pika
import sys
import os
import base64
import time
import random

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='firstqueue')
i = 0

time.clock()

while True: #time.clock() < 5:
  message = os.urandom(int(random.uniform(1,20)*3))
  channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      body=message,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  print("%s" % message),
  i = i + 1
  print(i)
  time.sleep(0.1)

connection.close()
#input('Press ENTER to exit')