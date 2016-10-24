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
nextflagraw = 0
initialflag = "FFFFFF"

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
  global nextflag
  global nextflagraw
  #print (str(nextflagraw))
  #print(body)
  print(body,end=''),
  ch.basic_ack(delivery_tag = method.delivery_tag)
  if (nextflag != "") and (body.find(inttoseqchar(nextflagraw))) != -1:
      print("FLAG MATCH")
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print(nextflagraw)
      #print(xor_message_chunk(body[4:]))
      nextflagraw = nextflagraw ^ xor_message_chunk(body[4:])
      #print (str(nextflag) + " ---- " + inttoseqchar(nextflagraw))
  elif body.find('IVIVIV') != -1:
      print("FOUND IV")
      nextflagraw = int(body[6:]) ^ int(initialflag,16) #integer
      nextflag = inttoseqchar(nextflagraw) #string
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))
      #print (nextflag) #string
      #print (nextflagraw) #integer
  elif body.find(inttoseqchar(nextflagraw ^ int(initialflag,16))) != -1:
      print("LAST FLAG")
      channel2.basic_publish(exchange='',
                      routing_key='secondqueue',
                      body=body,
                      properties=pika.BasicProperties(delivery_mode = 2,))

channel.basic_consume(callback,
                      queue="firstqueue")

print ("waiting for message(s)...")
channel.start_consuming()
