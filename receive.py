from __future__ import print_function
import pika
import time
import base64
import random

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
  #print (str(nextflagraw))
  #print(body)
  print(body,end=''),
  ch.basic_ack(delivery_tag = method.delivery_tag)
  
  if body.find('IVIVIV') != -1:
      #print("FOUND IV")
      nextflagraw = body[6:] #integer
      nextflag = xor_message_chunk(nextflagraw) ^ int(initialflag,16) #string
      messageid[messageidnum] = [nextflag, nextflag + 256]
      messageidnum = messageidnum + 1
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print (nextflag) #string
      #print (nextflagraw) #integer

  for items in messageid:
    nextflagraw = messageid[items]
    #print(nextflagraw)
    if (body.find(inttoseqchar(nextflagraw[0]))) != -1:
      #print(" NORMAL FLAG MATCH")
      if random.random() < 0.1:
        print("--CHAR CORRUPTED--")
        nochartobecorrupted = random.randint(0,len(body))
        if nochartobecorrupted == len(body):
          nochartobecorrupted = nochartobecorrupted - 1
        #print(nochartobecorrupted)
        chartobecorrupted = body[nochartobecorrupted]
        corruptedchar = chr(int(chartobecorrupted.encode('hex'),16) + 1)
        #corruptedchar = chr(random.randint(0,255))
        body = body[:nochartobecorrupted] + corruptedchar + body[nochartobecorrupted+1:]
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print(nextflagraw)
      #print(xor_message_chunk(body[4:]))
      messageid[items][0] = nextflagraw[0] ^ xor_message_chunk(body[3:])
      #print(messageid[items])
      #print('-----' + inttoseqchar(messageid[items]) + '-----')
      break
      #print (str(nextflag) + " ---- " + inttoseqchar(nextflagraw))
    elif (body.find(inttoseqchar(nextflagraw[1]))) != -1:
      #print("--------IV + 256 ---------")
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      messageid[items][0] = nextflagraw[1] ^ xor_message_chunk(body[3:])
      messageid[items][1] = nextflagraw[1] + 256
    elif body.find(inttoseqchar(nextflagraw[0] ^ int(initialflag,16))) != -1:
      #print("--------LAST FLAG------------")
      messageid.pop(items)
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      break


channel.basic_consume(callback,
                      queue="firstqueue")

print ("waiting for message(s)...")
channel.start_consuming()
