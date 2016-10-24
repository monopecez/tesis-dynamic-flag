from __future__ import print_function
import pika
import time
import base64

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel2 = connection.channel()

channel.queue_declare(queue="firstqueue")
channel2.queue_declare(queue="secondqueue")

nextflag = ""
nextflagint = 0
initialflag = "FFFFFF"

def xor_message_chunk(message):
  n = 3
  listnya = [int(message[i:i+n].encode('hex'),16) for i in range(0, len(message), n)]
  nextflag = 0
  for item in listnya:
    nextflag = nextflag ^ item
  return nextflag

def inttob64(numba):
  b64 = base64.b64encode(hex(numba)[2:].zfill(6).decode('hex'))
  return b64

def callback(ch, method, properties, body):
  global nextflag
  global nextflagint
  #print(body)
  print(body,end='')
  ch.basic_ack(delivery_tag = method.delivery_tag)
  if (nextflag != "") and (body.find(inttob64(nextflagint))) != -1:
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print(nextflagint)
      #print(xor_message_chunk(body[4:]))
      nextflagint = nextflagint ^ xor_message_chunk(body[4:])
      #print (str(nextflag) + " ---- " + inttob64(nextflagint))

  if body.find('IVIVIV') != -1:
      nextflagint = int(body[6:]) ^ int(initialflag,16) #integer
      nextflag = inttob64(nextflagint) #string
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print (nextflag) #string
      #print (nextflagint) #integer


channel.basic_consume(callback,
                      queue="firstqueue")

print ("waiting for message(s)...")
channel.start_consuming()
