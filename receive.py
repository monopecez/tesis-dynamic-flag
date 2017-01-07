from __future__ import print_function
import pika
import time
import base64
import random
import sys

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel2 = connection.channel()

channel.queue_declare(queue="firstqueue")
channel2.queue_declare(queue="secondqueue")

nextflag = ""
nextflagraw = 0
initialflag = "FFFFFF"
messageid = dict()
messageidnum = 1
counter2 = 0

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

def callback(ch, method, properties, body):
  global nextflag
  global nextflagraw
  global messageidnum
  global messageid
  global counter2
  ch.basic_ack(delivery_tag = method.delivery_tag)
  errordi = int(sys.argv[1])
  counter2 = counter2 + 1
  
  if body.find('IVIVIV') != -1:
      counter2 = 0
      if counter2 == errordi:
        nochartobecorrupted = random.randint(0,len(body) - 1 )
        if nochartobecorrupted == len(body):
          nochartobecorrupted = nochartobecorrupted - 1
        chartobecorrupted = body[nochartobecorrupted]
        corruptedchar = chr(int(chartobecorrupted.encode('hex'),16) + 1)
        body = body[:nochartobecorrupted] + corruptedchar + body[nochartobecorrupted+1:]
      nextflagraw = body[6:] 
      nextflag = xor_message_chunk(nextflagraw) ^ int(initialflag,16) 
      messageid[messageidnum] = [nextflag % 16777216, (nextflag + 256) % 16777216]
      messageidnum = messageidnum + 1
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))

  for items in messageid:
    nextflagraw = messageid[items]
    if (body[:3].find(inttoseqchar(nextflagraw[0]))) != -1:# and body[:3] != "IVI":
      if counter2 == errordi:
        nochartobecorrupted = random.randint(3,len(body)-1)
        chartobecorrupted = body[nochartobecorrupted]
        corruptedchar = chr(int(chartobecorrupted.encode('hex'),16) + 1)
        body = body[:nochartobecorrupted] + corruptedchar + body[nochartobecorrupted+1:]
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      messageid[items][0] = (nextflagraw[0] ^ xor_message_chunk(body[3:]))
      break
    
    elif (body[:3].find(inttoseqchar(nextflagraw[1]))) != -1:
      if counter2 == errordi:
        nochartobecorrupted = random.randint(3,len(body)-1)
        chartobecorrupted = body[nochartobecorrupted]
        corruptedchar = chr(int(chartobecorrupted.encode('hex'),16) + 1)
        body = body[:nochartobecorrupted] + corruptedchar + body[nochartobecorrupted+1:]
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      messageid[items][0] = (nextflagraw[1] ^ xor_message_chunk(body[3:])) % 16777216
      messageid[items][1] = (nextflagraw[1] + 256) % 16777216
      break
    
    elif body[:3].find(inttoseqchar(nextflagraw[0] ^ int(initialflag,16))) != -1 or body[:3].find(inttoseqchar(nextflagraw[1] ^ int(initialflag,16))) != -1 or body.find(inttoseqchar((nextflagraw[1] + 256) ^ int(initialflag,16))) != -1 :
      if counter2 == errordi:
        nochartobecorrupted = random.randint(3,len(body)-1)
        chartobecorrupted = body[nochartobecorrupted]
        corruptedchar = chr(int(chartobecorrupted.encode('hex'),16) + 1)
        body = body[:nochartobecorrupted] + corruptedchar + body[nochartobecorrupted+1:]
      messageid.pop(items)
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      break
  print(body,end=''),


channel.basic_consume(callback,
                      queue="firstqueue")

print ("waiting for message(s)...")
channel.start_consuming()
