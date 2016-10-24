import pika
import sys
import random
import time
import base64
import os

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='firstqueue')
#channel.queue_declare(queue='secondqueue')

message = ' '.join(sys.argv[1:]) or "Hello World!"

IV = int(os.urandom(3).encode('hex'),16)
channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= "IVIVIV" + str(IV),
                      properties=pika.BasicProperties(delivery_mode = 2,))
print("[v] %r : IV is sent" % IV)

totalpadding = 32 - (len(message)%32)
message = message + totalpadding*'F'
message = base64.b64encode(message)

i = 0
while (i != len(message)/32):
  time.sleep(random.uniform(0,2))
  body = message[(i)*32:(i+1)*32]
  if i == len(message)/32 - 1:
    heading = "FFFE"
  else:
    heading = "FFFS"
  channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= heading + body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  print("[v] %r is sent" % body)
  i = i + 1

'''
time.sleep(random.uniform(0,2))
channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body="FFFF" + lenmessage + message[0:int(lenmessage)],
                      properties=pika.BasicProperties(delivery_mode = 2,))
'''
#print("[v] %r is sent" % message)

connection.close()
