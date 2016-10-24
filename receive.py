from __future__ import print_function
import pika
import time

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel2 = connection.channel()

channel.queue_declare(queue="firstqueue")
channel2.queue_declare(queue="secondqueue")

def callback(ch, method, properties, body):
  print(body,end=''),
  ch.basic_ack(delivery_tag = method.delivery_tag)
  if body.find('FFFS') != -1:
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  elif body.find('FFFE') != -1:
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  elif body.find('IVIVIV') != -1:
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))


channel.basic_consume(callback,
                      queue="firstqueue")

print ("waiting for message(s)...")
channel.start_consuming()
