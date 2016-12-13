import pika
import sys
import random
import time
import base64
import os
from Crypto.Cipher import AES
from Crypto.Cipher import ChaCha20

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

key = 'secretkey123456!' + 'secretkey123456!'
obj = AES.new(key, AES.MODE_ECB)
IV = "a9cd5e3cfb793413".decode('hex')
encipher = ChaCha20.new(key = key, nonce=IV)

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='firstqueue')

isLast = False
#IV = encipher.nonce

channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= "IVIVIV" + str(IV),
                      properties=pika.BasicProperties(delivery_mode = 2,))
print("[v] %s : IV is sent --->" % IV),
print(IV.encode('hex') + '   ')
initialflag = "FFFFFF"
print("XOR-ed to: "),
nextflagraw = xor_message_chunk(IV) ^ int(initialflag,16)
print(hex(nextflagraw)[2:] + '   '),
print("%s" % inttoseqchar(nextflagraw))
IVraw = nextflagraw
message = ' '.join(sys.argv[1:])

try:
  if sys.argv[1] == '1':
    message = "This1page1contains1examples1on1basic1concepts1of1C1programming1like:1loops,1functions,1pointers,1structures1etc.1All1the1examples1in1this1page1are1tested1and1verified1on1GNU1GCC1compiler,1although1almost1every1program1on1in1this1website1will1work1on1any1compiler1you1use.1Feel1free1to1copy1the1source1code1and1execute1it1in1your1device."
  elif sys.argv[1] == '2':
    message = "This2page2contains2examples2on2basic2concepts2of2C2programming2like:2loops,2functions,2pointers,2structures2etc.2All2the2examples2in2this2page2are2tested2and2verified2on2GNU2GCC2compiler,2although2almost2every2program2on2in2this2website2will2work2on2any2compiler2you2use.2Feel2free2to2copy2the2source2code2and2execute2it2in2your2device."
  elif sys.argv[1] == 'short5':
    message = "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789"
  elif sys.argv[1] == 'short6':
    message = "01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"    
  elif sys.argv[1] == 'long':
    message = 10*"01234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890"

except:
  message = "This page contains examples on basic concepts of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."


#message = "This page contains examples on basic concepts" # of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."
#totalpadding = 32 - (len(message)%32)
#message = message + totalpadding*' '

print("__________SENDING__________")

i = 0

while i != len(message)/32 + 1:
  #print(str(nextflagraw) + ' ----- ' ),
  if i == (len(message)/32):
    #print("LAST FLAG")
    #nextflagraw = nextflagraw ^ int(initialflag,16)
    isLast = True
    
  if i%4 == 0:
    # 4 karena kirim iv setiap 4 message sekali
    #print("resync")
    if not isLast:
      #print("cuma resync")
      nextflagraw = IVraw + 256 * (i/4)
    else:
      #print("tambah isLast")
      nextflagraw = (IVraw + 256 * (i/4)) ^ int(initialflag,16)
      #print nextflagraw
  
  if isLast:
    #print("tambah lagi isLast")
    nextflagraw = (IVraw + (256 * ((i/4)+1)) ^ int(initialflag,16))
    #print nextflagraw

  #print(str(nextflagraw))
  #chop and encrypt
  #itemtobesent = inttoseqchar(nextflagraw) + obj.encrypt(message[(i)*32:(i+1)*32])
  encipher = ChaCha20.new(key = key, nonce = IV)
  itemtobesent = inttoseqchar(nextflagraw) + encipher.encrypt(message[(i)*32:(i+1)*32])
  channel.basic_publish(exchange='',
                      routing_key='firstqueue',
                      #routing_key='secondqueue',
                      body= itemtobesent,
                      properties=pika.BasicProperties(delivery_mode = 2,))
  print("[v] %s is sent" % itemtobesent)
  time.sleep(random.uniform(0,0.5))
  nextflagraw = nextflagraw ^ xor_message_chunk(itemtobesent[3:])
  #print(nextflagraw)
  body = message[(i)*32:(i+1)*32]
  i = i + 1