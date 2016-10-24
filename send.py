import pika
import sys
import random
import time
import base64

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='firstqueue')
#channel.queue_declare(queue='secondqueue')

message = ' '.join(sys.argv[1:]) or "Hello World!"

'''
message = base64.b64encode(message)
if len(message) < 10:
  lenmessage = '0' + str(len(message))
elif len(message) > 99:
  lenmessage = '99'
else:
  lenmessage = str(len(message))
'''

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
