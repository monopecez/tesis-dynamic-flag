import pika
import sys
import random
import time
import base64
import os

def xor_message_chunk(message):
  n = 3
  listnya = [int(message[i:i+n].encode('hex'),16) for i in range(0, len(message), n)]
  nextflagraw = 0
  for item in listnya:
    nextflagraw = nextflagraw ^ item
  return nextflagraw

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='firstqueue')

IV = int(os.urandom(3).encode('hex'),16)
channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= "IVIVIV" + str(IV),
                      properties=pika.BasicProperties(delivery_mode = 2,))
print("[v] %r : IV is sent" % IV)
initialflag = "FFFFFF"

nextflagraw = IV ^ int(initialflag,16)

message = ' '.join(sys.argv[1:]) or "This page contains examples on basic concepts of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."
#message = "This page contains examples on basic concepts" # of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."
totalpadding = 27 - (len(message)%27)
message = message + totalpadding*' '

print("__________SENDING__________")

i = 0

while i != len(message)/27:
  if i == (len(message)/27)-1:
    nextflagraw = nextflagraw ^ int(initialflag,16)
  itemtobesent = base64.b64encode(hex(nextflagraw)[2:].zfill(6).decode('hex') + message[(i)*27:(i+1)*27])
  channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= itemtobesent,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  print("[v] %r is sent" % itemtobesent)
  time.sleep(random.uniform(0,1.5))
  nextflagraw = nextflagraw ^ xor_message_chunk(itemtobesent[4:])
  body = message[(i)*27:(i+1)*27]
  i = i + 1