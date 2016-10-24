from __future__ import print_function
import pika
import time
import base64

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue="secondqueue")
fullbody = ''
rawnextflag = int('ffffff',16)

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
  firstflag = "FFFFFF" 
  global fullbody
  global rawnextflag
  if body[:6] == 'IVIVIV':
    print(body[6:])
    rawnextflag = int(body[6:]) ^ int(firstflag,16)
    print(rawnextflag)
  elif body[:4] == inttob64(rawnextflag):
    print("Received : " + body)
    fullbody = fullbody + body[4:]
    rawnextflag = rawnextflag ^ xor_message_chunk(body[4:])
  elif body[:4] == inttob64(rawnextflag ^ int(firstflag,16)):
    print("Received : " + body)
    fullbody = fullbody + body[4:]
    print("Decoded  : " + base64.b64decode(fullbody))
    fullbody = ''
  
  ch.basic_ack(delivery_tag = method.delivery_tag)

channel2.basic_consume(callback,
                      queue="secondqueue")

print ("waiting for message(s)...")
channel2.start_consuming()
