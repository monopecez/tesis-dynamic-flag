from __future__ import print_function
import pika
import time
import base64
from Crypto.Cipher import AES
from Crypto.Cipher import ChaCha20

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel2 = connection.channel()
channel2.queue_declare(queue="secondqueue")
time.clock()
#fullbody = ''
nextflagraw = int('ffffff',16)
totaltime = dict()
decipher = dict()
key = 'secretkey123456!' + 'secretkey123456!'
#obj = AES.new(key, AES.MODE_ECB)

messageid = dict()
messageidnum = 1
fullbody = dict()

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
  global messageid
  global messageidnum
  global decipher
  timenow = time.clock()

  if body[:6] == 'IVIVIV':
    print(body[6:])
    nextflagraw = body[6:] # nextflagraw = nonce
    decipher[messageidnum] = ChaCha20.new(key = key, nonce = nextflagraw)
    nextflag = xor_message_chunk(nextflagraw) ^ int(firstflag,16)
    messageid[messageidnum] = [nextflag, nextflag + 1]
    fullbody[messageidnum] = ''
    totaltime[messageidnum] = time.clock() - timenow
    messageidnum = messageidnum + 1
    #print(nextflagraw)
  
  for items in messageid:
    nextflagraw = messageid[items]
    if body[:3] == inttoseqchar(nextflagraw[0]):
      print("Received [" + str(items) + "] : " + body)
      fullbody[items] = fullbody[items] + body[3:]
      #print(obj.decrypt(body[3:]))
      messageid[items][0] = nextflagraw[0] ^ xor_message_chunk(body[3:])
      totaltime[items] = totaltime[items] + time.clock() - timenow
      break
    elif body[:3] == inttoseqchar(nextflagraw[1]):
      #print("MASUUUUK")
      print("Received [" + str(items) + "] : " + body)
      fullbody[items] = fullbody[items] + body[3:]
      #print(obj.decrypt(body[3:]))
      messageid[items][0] = nextflagraw[1] ^ xor_message_chunk(body[3:])
      messageid[items][1] = nextflagraw[1] + 1
      totaltime[items] = totaltime[items] + time.clock() - timenow
      break
    elif body[:3] == inttoseqchar(nextflagraw[0] ^ int(firstflag,16)):
      print("Received [" + str(items) + "] : " + body)
      fullbody[items] = fullbody[items] + body[3:]
      #print(obj.decrypt(body[3:]))
      print("Decoded  [" + str(items) + "] : " + decipher[items].decrypt(fullbody[items]))
      fullbody.pop(items)
      messageid.pop(items)
      print(str(items) + '-' + str(totaltime.pop(items) + time.clock() - timenow))
      print(20*'-')
      break
    totaltime[items] = totaltime[items] + time.clock() - timenow

  ch.basic_ack(delivery_tag = method.delivery_tag)

channel2.basic_consume(callback,
                      queue="secondqueue")

print ("waiting for message(s)...")
channel2.start_consuming()
