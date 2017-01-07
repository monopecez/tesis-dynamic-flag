# -*- coding: utf-8 -*-
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
#encipher= AES.new(key, AES.MODE_ECB)
#####IV = "a9cd5e3cfb793413".decode('hex')
IV = "7365c71905dd1e4c".decode('hex')
#IV = "0000ffffff000000".decode('hex')
encipher = ChaCha20.new(key = key, nonce=IV)
#encipher = ChaCha20.new(key = key)

credentials = pika.PlainCredentials('tesis','tesis')
recipientaddr = '192.168.18.133'
#recipientaddr = 'localhost'
portaddr = 5672

parameters = pika.ConnectionParameters(recipientaddr, portaddr,'/',credentials)

connection = pika.BlockingConnection(parameters)
channel = connection.channel()

channel.queue_declare(queue='firstqueue')

isLast = False
IV = encipher.nonce

#message = "Ранее Европейское агентство по окружающей среде сообщило, что в Европе загрязнение воздуха ежегодно приводит к преждевременной смерти около 467 тысяч человек."
#message = "Two world-leading clean energy projects have opened in the south Indian state of Tamil Nadu. A £3m industrial plant is capturing the CO2 emissions from a coal boiler and using the CO2 to make valuable chemicals. It is a world first. And just 100km away is the world's biggest solar farm, making power for 150,000 homes on a 10 sq km site."
message = ' '.join(sys.argv[1:])

notfound = False
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
  elif sys.argv[1] == 'abjad':
    message = 9*"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
  elif sys.argv[1] == 'numb':
    message = 45*"0123456789"
  elif sys.argv[1] == 'korean':
    message = "우병우(사진) 전 청와대 민정수석이 정부에 비판적인 교수들이 국공립대 총장에 임명되지 못하도록 하는 데 핵심적인 역할을 했다는 증언이 나왔다. 특히 범법 여부보다는 주로 사상이나 성향을 문제 삼아 후보자의 결격을 주장했다는 것이다. <본지 1월 2일자 12면, 3일자 6면>"
  elif sys.argv[1] == 'japanese':
    message = "民進党関係者によると、総支部事務所の駐車場に止めていた街宣用ワゴン車も、フロントガラスなどが割られ、タイヤ数本がパンクさせられていた。タイヤは刃物か工具のようなもので穴を開けられていたという。総支部事務所は３１日夕から無人で、１日朝に訪れた市議が被害に気付いた。"
  elif sys.argv[1] == 'cyrillic':
    message = "Ранее Европейское агентство по окружающей среде сообщило, что в Европе загрязнение воздуха ежегодно приводит к преждевременной смерти около 467 тысяч человек."
  elif sys.argv[1] == 'arabic':
    message = "وأوضح الجهاز في نشرة إحصاءات السياحة الشهرية، أن عدد السائحين الذين زاروا مصر خلال أكتوبر الماضي، بلغ نحو 506.2 ألف سائح، مقارنة بعدد 437 ألف سائح لسبتمبر الماضي."
  elif sys.argv[1] == 'file':
    try:
      message = open(sys.argv[2], 'rb').read()
    except:
      print(sys.argv[2]) + " not found"
      notfound = True
except:
  message = "This page contains examples on basic concepts of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."

noresync = False
  
'''
try:
  if sys.argv[2] == "noresync":
    noresync = True
except:
  noresync = False
'''

#message = "This page contains examples on basic concepts" # of C programming like: loops, functions, pointers, structures etc. All the examples in this page are tested and verified on GNU GCC compiler, although almost every program on in this website will work on any compiler you use. Feel free to copy the source code and execute it in your device."
#totalpadding = 32 - (len(message)%32)
#message = message + totalpadding*' '

if not notfound:
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
  
  print("__________SENDING__________")

  i = 0

  while i != len(message)/32 + 1:
    #print(str(nextflagraw) + ' ----- ' ),
    if i == (len(message)/32):
      #print("LAST FLAG")
      if noresync:
        nextflagraw = nextflagraw ^ int(initialflag,16)
      isLast = True
    
    if not noresync:
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

    nextflagraw = nextflagraw % 16777216

    #print(str(nextflagraw))
    #chop and encrypt
    #itemtobesent = inttoseqchar(nextflagraw) + obj.encrypt(message[(i)*32:(i+1)*32])
    #encipher = AES.new(key, AES.MODE_ECB)
    encipher = ChaCha20.new(key = key, nonce = IV)

    itemtobesent = inttoseqchar(nextflagraw) + encipher.encrypt(message[(i)*32:(i+1)*32])
    channel.basic_publish(exchange='',
                        routing_key='firstqueue',
                        #routing_key='secondqueue',
                        body= itemtobesent,
                        properties=pika.BasicProperties(delivery_mode = 2,))
    print("[v] %s is sent" % itemtobesent)
    time.sleep(random.uniform(0,0.001))
    nextflagraw = nextflagraw ^ xor_message_chunk(itemtobesent[3:])
    #print(nextflagraw)
    body = message[(i)*32:(i+1)*32]
    i = i + 1

connection.close()
#input("press Enter to exit")