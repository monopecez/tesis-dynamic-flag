from __future__ import print_function
import pika
import time
import base64
from Crypto.Cipher import AES

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue="secondqueue")
time.clock()
fullbody = ''
nextflagraw = int('ffffff',16)
totaltime = 0
key = 'secretkey123456!'
obj = AES.new(key, AES.MODE_ECB)



def xor_message_chunk(message):
  n = 3
  listnya = [int(message[i:i+n].encode('hex'),16) for i in range(0, len(message), n)]
  nextflagraw = 0
  for item in listnya:
    nextflagraw = nextflagraw ^ item
  return nextflagraw

def inttoseqchar(number):
  numberinhex = hex(number)[2:].zfill(6)
  listnya = [chr(int(numberinhex[i:i+2],16)) for i in range(0, 6, 2)]
  return ''.join(listnya)

def callback(ch, method, properties, body):
  firstflag = "FFFFFF" 
  global fullbody
  global nextflagraw
  global totaltime
  timenow = time.clock()
  if body[:6] == 'IVIVIV':
    print(body[6:])
    nextflagraw = int(body[6:]) ^ int(firstflag,16)
    print(nextflagraw)
  elif body[:3] == inttoseqchar(nextflagraw):
    print("Received : " + body)
    #fullbody = fullbody + body[3:]
    print(obj.decrypt(body[3:]))
    nextflagraw = nextflagraw ^ xor_message_chunk(body[4:])
  elif body[:3] == inttoseqchar(nextflagraw ^ int(firstflag,16)):
    print("Received : " + body)
    #fullbody = fullbody + body[3:]
    print(obj.decrypt(body[3:]))
    #print("Decoded  : " + obj.decrypt(fullbody))
    fullbody = ''
    print(totaltime)
    totaltime = 0
    print(20*'-')
  totaltime = totaltime + time.clock() - timenow

  ch.basic_ack(delivery_tag = method.delivery_tag)

channel2.basic_consume(callback,
                      queue="secondqueue")

print ("waiting for message(s)...")
channel2.start_consuming()
