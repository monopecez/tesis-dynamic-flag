from __future__ import print_function
import pika
import time
import base64

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue="secondqueue")
fullbody = ''

def callback(ch, method, properties, body): 
  global fullbody
  print("Received : " + body)
  if body[0:4] == 'FFFS':
    fullbody = fullbody + body[4:]
  else:
    fullbody = fullbody + body[4:]
    print("Decoded  : " + base64.b64decode(fullbody))
    fullbody = ''
  ch.basic_ack(delivery_tag = method.delivery_tag)

channel2.basic_consume(callback,
                      queue="secondqueue")

print ("waiting for message(s)...")
channel2.start_consuming()
