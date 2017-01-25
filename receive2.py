# -*- coding: windows-1251 -*-
from __future__ import print_function
import pika
import time
import base64
import sys
from Crypto.Cipher import AES
from Crypto.Cipher import ChaCha20

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue="secondqueue")
nextflagraw = int('ffffff',16)
decipher = dict()
key = 'secretkey123456!' + 'secretkey123456!'

counter = dict()
counter2 = dict()
messageid = dict()
messageidnum = 1
fullbody = dict()
iv = dict()

def xor_message_chunk(message):
  n = 3 #flag size (bytes)
  if len(message) % 3 != 0:
    message = (n - len(message) % n) * "\x00" + message
  listnya = [int(message[i:i+n].encode('hex'),16) for i in range(0, len(message), n)]
  nextflagraw = 0
  for item in listnya:
    nextflagraw = nextflagraw ^ item
  return nextflagraw

def inttoseqchar(number):
  numberinhex = hex(number)[2:].zfill(6)
  listnya = [chr(int(numberinhex[i:i+2],16)) for i in range(0, 6, 2)]
  return ''.join(listnya)

kefile = False
try:
  if sys.argv[1] == 'file':
    filenya = open(sys.argv[2], 'wb')
    kefile = True
except:
  pass

def callback(ch, method, properties, body):
  initialflag = "FFFFFF" 
  global fullbody
  global nextflagraw
  global messageid
  global messageidnum
  global decipher
  global iv
  global counter2
  global counter

  if body[:6] == 'IVIVIV':
    nextflagraw = body[6:]
    iv[messageidnum] = nextflagraw
    decipher[messageidnum] = ChaCha20.new(key = key, nonce = nextflagraw)
    nextflag = (xor_message_chunk(nextflagraw) ^ int(initialflag,16))
    messageid[messageidnum] = [nextflag % 16777216, (nextflag + 256) % 16777216]
    fullbody[messageidnum] = ''
    counter[messageidnum] = 0
    counter2[messageidnum] = 0
    messageidnum = messageidnum + 1
  
  for items in messageid:
    nextflagraw = messageid[items]
    if body[:3] == inttoseqchar(nextflagraw[0]):
      decipher[items] = ChaCha20.new(key = key, nonce = iv[items])
      fullbody[items] = fullbody[items] + decipher[items].decrypt(body[3:])
      messageid[items][0] = (nextflagraw[0] ^ xor_message_chunk(body[3:])) % 16777216
      counter[items] = counter[items] + 1
      counter2[items] = counter2[items] + 1
      #print("Received[" + str(items) + "]: " + body)
      break

    elif body[:3] == inttoseqchar(nextflagraw[1]):
      if counter[items] != 4:
        fullbody[items] = fullbody[items] + " --ADA YANG HILANG-- "
      counter[items] = 1
      decipher[items] = ChaCha20.new(key = key, nonce = iv[items])
      fullbody[items] = fullbody[items] + decipher[items].decrypt(body[3:])
      messageid[items][0] = (nextflagraw[1] ^ xor_message_chunk(body[3:])) % 16777216
      messageid[items][1] = (nextflagraw[1] + 256)  % 16777216
      counter2[items] = 1
      #print("Received[" + str(items) + "]: " + body)
      break

    elif body[:3] == inttoseqchar(nextflagraw[0] ^ int(initialflag,16)) or body[:3] == inttoseqchar(nextflagraw[1] ^ int(initialflag,16)) or body[:3] == inttoseqchar((nextflagraw[1] + 256) ^ int(initialflag,16)) :
      if counter[items] != counter2[items]:
        fullbody[items] = fullbody[items] + " --ADA YANG HILANG-- "      
      decipher[items] = ChaCha20.new(key = key, nonce = iv[items])
      fullbody[items] = fullbody[items] + decipher[items].decrypt(body[3:])
      if kefile:
        filenya.write(fullbody[items])
        filenya.close()
        fullbody.pop(items)
        messageid.pop(items)
        exit()
      else:
        #print("Received[" + str(items) + "]: " + body)
        print("Printing[" + str(items) + "]: " + fullbody[items])
      fullbody.pop(items)
      messageid.pop(items)
      break
  ch.basic_ack(delivery_tag = method.delivery_tag)

channel2.basic_consume(callback,
                      queue="secondqueue")

#print ("waiting for message(s)...")
channel2.start_consuming()
