#oi bruv dis programme wuz made boi shystudios and is loicensed unda da gee pea el v2 innit
#i havn't written python in like 10 years but it werkz, plz read the comment in the id_create func
#because the entire list needs to be ran through twice to get full coverage i think

import socket
import time
import ssl
import base62 #python.exe -m pip install pybase62
import signal
import os.path
from threading import Thread

IDFILENAME = "last_id.txt"
FILENAME = "working_id5s.txt"
TCP_HOST = 'i.imgur.com' # as you can see i wasn't using ssl to begin with 
TCP_PORT = 443 # it didnt work without ssl, those bastards, why do you force ssl for a static image???
MAX_LIMIT = 4 # some weird multiple of the data it gets, at 4 it gets 10 total bytes, 5 is 16 idk why
TEST_ID = 558288318 #known good imgur id5 url (monopoy man) bmWII.jpg
MAX_URLS = 916132831 #max num of possible imgur urls
imgurid = "00000" #just a placeholder string
buffer_list = []
chunk_size = 64 #number of iterations per thread
NUM_WORKERS = 8 #number of threads to spawn
ERROR_MODE = 0
msg_top = "GET /"
msg_bottom = ".jpg HTTP/1.1\r\n" \
"HOST: i.imgur.com\r\n" \
"Accept: */*\r\n\n"


if not os.path.isfile(IDFILENAME):
     print("setting up file for the first time")
     file = open(IDFILENAME, "a+")
     file.write("0\n")
     file.close() #do this in case the file doesn't exist at all



#set up ssl and sockets
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE 


#generates the ID and pads it with 0's
def id_create(idnum):
    url=base62.encode(idnum)
    while len(url) < 5:
        url += str(0)
    #url_reverse = url[::-1] #i think this algo will not get every possible product, like 00001 etc so you gotta run it backwards after u run it one the normal way
    #return url_reverse #just uncomment these after you run it once, then delete the start id file, you can deduplicate the id list later with other software
    return url

#makes sure stuff is closed before closing (maybe not needed?
def handler(signum, frame):
    global file
    global startid
    global threads
    res = input("quit for real? y/n?")
    if res == 'y':
        file.close() #in case it is open
        for workers in threads:
          workers.join()
        write_buffers()
        print("OK CLOSING")
        exit(1)
                   
#makes the above function actually function
signal.signal(signal.SIGINT, handler)
                   
def write_buffers():
    print("writing buffers")
    global file
    global startid
    global buffer_list
    global ERROR_MODE
    file = open(IDFILENAME, "w")
    if ERROR_MODE == 1:
         file.write(str(startid - NUM_WORKERS - (NUM_WORKERS*chunk_size))) #writes the id before the error
    if ERROR_MODE == 0:
         file.write(str(startid)) #normal
    file.close()
    file = open(FILENAME, "a")
    for i in buffer_list:
         file.write(i)
         file.write("\n")
    buffer_list.clear()

def worker(num):
     #actually process the shit
     global context
     global buffer_list
     global chunk_size
     global MAX_LIMIT
     global TCP_HOST
     global TCP_PORT
     global msg_top
     global msg_bottom
     global ERROR_MODE
     print("worker start")
     limit = num + chunk_size
     while num <= limit:
          #begin loop
          imgurid = id_create(num)
          MESSAGE = (msg_top + imgurid + msg_bottom)#create the message
          s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #set up the socket new
          s_s = context.wrap_socket(s, server_hostname=TCP_HOST)#set up the ssl again
          s_s.connect((TCP_HOST, TCP_PORT)) # Connect to remote socket
          s_s.send(MESSAGE.encode("utf-8")) # send that shit
          time.sleep(0.1) # wait a sec to make sure shit gets sent (might break stuff idk)
          #this delay might be why im getting 10 bytes instead of 4 (max limit) so if you
          #remove this delay to make it faster you might want to check if you are still
          #actually getting 10 total bytes 
          curr_size = 0
          data = ""
          while curr_size < MAX_LIMIT:
               data += (s_s.recv(MAX_LIMIT - curr_size).decode("utf-8"))
               curr_size = curr_size + 1
          s_s.close() # close the socket (hopefully quickly)
          #print(data[9]) #debug
          if (data[9] == '2'):#the 10th byte will be either 2 or 3 depending on if the image exists or not
               print("GOOD URL FOUND!:", imgurid)
               buffer_list.append(imgurid)
          elif (data[9] == '4'):
               print("4 detected, likely rate limited or something")
               print("force stopping thread!!")
               limit = 0
               ERROR_MODE = 1
               break
               
          num += 1
        #if the url is a good url the response will be 200 but it only rx's data up to that first
          #number because if it is a bad url it will be 300 the program never actually downloads
          #any image or anything, it ideally is closing the connection before the entire responce
          #gets here, thus saving on download size, with 2 billion possible combos (forwards and
          #backwards) and allegedly only rxing 10 bytes per address attempt, it should only take
          #20gb of data to fully check the entire id5 set, with less than half of those being
          #good urls Im sure the upload is a lot higher though, since you are sending about
          #70 bytes per request? idk. it would take me about 9 days non stop using my full
          #upload speed to upload 70gb of data so its too late for me, maybe you can help
          #for all i know the entire id5 set has been archived already.
          #when you want to start downloading the images just append.jpg and prepend i.imgur.com/
          #to the id, it doesn't matter what the file name is, imgur will send the correct format
          #via data, just ignore the url extention with your download system 
        
          

          



file = open(IDFILENAME, "r") #open file to read the current pos
startid = int(file.readline()) 
#startid = int(input("Enter a number to start:")) #for manual input
print("starting at",startid)
#imgurid = id_create(startid)
#print ("".join("starting at i.imgur.com/" + imgurid +".jpg\n"))

file.close()
file = open(FILENAME, "a+") #initial setup if the file doesn't exist
file.close()
while startid <= MAX_URLS:

     threads = []
     for i in range(NUM_WORKERS):
          workers = Thread(target=worker, args=(startid,))
          threads.append(workers)
          workers.start()
          startid += (chunk_size +1)

     for workers in threads:
          workers.join()
          
     if len(buffer_list) > 0:
          write_buffers()
     elif len(buffer_list) == 0:
          print("no new buffer entries, something prob went wrong, exiting")
          exit(1)
     



 

