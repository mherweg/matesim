import numpy as np
import pygame
import pygame.time
import socket
import sys
import math

# erledigt: 
# * Spielfeld auf 30x28 vergrößert
# * Pixel kann jede Farbe annehemen
# * Daten per UDP (tpm2.net)
#
# TODO:
# seriell (TPM2) senden
#

# max channels in glediator regelt die framelength statisch! Egal wie viele Channel tatsächlich genutzt werden.
# 8x8 Feld - bei max channels 512 trotzdem framelength = 512

LOCAL_IP = '192.168.8.3' # configured in tpm2_net player software (jinx, glediator)
 
ROW_COUNT = 28 #8 #28
COLUMN_COUNT = 30 #8 #30
NUMPIXELS = ROW_COUNT * COLUMN_COUNT
TPM2_NET_HEADERSIZE = 6 #Bytes

game_over = 0

#define our screen size
SQUARESIZE = 30
#define width and height of board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT) * SQUARESIZE
size = (width, height)
 
RADIUS = int(SQUARESIZE/2 - 5)

clock = pygame.time.Clock()

port = 65506
PACKET_SIZE = 1357
packetBuffer = np.zeros(PACKET_SIZE)
pixels = np.zeros((NUMPIXELS, 3), 'uint8')

# bind to local UDP socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
server_address = (LOCAL_IP, port)
s.bind(server_address)
    
    

# work in progress:
led_index = 0
def tpm2NetHandle(packetBuffer, PACKET_SIZE):
    global led_index
    global pixels

    #print("r")
    #We've received a packet, read the data from it

    if ( packetBuffer[0] == 0x9C):  # header identifier (packet start)
        blocktype = packetBuffer[1] # block type (0xDA)
        framelength = (packetBuffer[2] << 8) | packetBuffer[3] # frame length (0x0069) = 105 leds
        packagenum = packetBuffer[4]   # packet number 0-255 0x00 = no frame split (0x01)
        numpackages = packetBuffer[5]   # total packets 1-255 (0x01)

        #print("blocktype     : ", hex(blocktype))
        #print("framelength   : ", framelength)
        #print("packetnumber  : ", packagenum)
        #print("total packets : ", numpackages)
                   
        if (blocktype == 0xDA):

            #print("frame #", packagenum+1, " (length: ", framelength, "bytes) from ", numpackages)

            #if ((cb >= framelength + 7) and (packetBuffer[6 + framelength] == 0x36)): #header end (packet stop)
            if (packetBuffer[TPM2_NET_HEADERSIZE + framelength] == 0x36): #header end (packet stop)
                i = 0
                packetindex = TPM2_NET_HEADERSIZE
                
                if(packagenum == 0):
                    led_index = 0
                    #print("RGB: ", hex(packetBuffer[packetindex])[2:], hex(packetBuffer[packetindex+1])[2:], hex(packetBuffer[packetindex+2])[2:])
          
                #while(packetindex < (framelength + 6)):
                # framelength in glediator always equal max channels not matrix size
                while(packetindex < (framelength + TPM2_NET_HEADERSIZE)): # and packetindex < (NUMPIXELS*3 + TPM2_NET_HEADERSIZE)):
                    try:
                        r = packetBuffer[packetindex]
                        g = packetBuffer[packetindex+1]
                        b = packetBuffer[packetindex+2]
                    except:
                        print("NO")
                    pixels[led_index][0] = r
                    pixels[led_index][1] = g
                    pixels[led_index][2] = b
                    #print("RGB: ", hex(r)[2:], hex(g)[2:], hex(b)[2:])
                    led_index +=1        
                    packetindex +=3
        #draw_board() #draw every packet
        #if((packagenum+1) == numpackages): # and (led_index == NUMPIXELS)):
        #print (led_index, NUMPIXELS)            
        if (led_index >= NUMPIXELS):
            draw_board()
            #print ('.')
            #pixels = np.zeros((NUMPIXELS, 3), 'uint8') #unkommentiert schneller?
            led_index = 0
     
def draw_board():
    #for c in range(COLUMN_COUNT):
        #for r in range(ROW_COUNT):
        #    pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
          #  pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
     
    for c in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            r = pixels[row*COLUMN_COUNT+c][0]
            g = pixels[row*COLUMN_COUNT+c][1]
            b = pixels[row*COLUMN_COUNT+c][2]
            color = (r,g,b)
            pygame.draw.circle(screen, color, (int(c*SQUARESIZE+SQUARESIZE/2), int(row*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            #pygame.draw.rect(screen, color, (c*SQUARESIZE, row*SQUARESIZE, c*SQUARESIZE+SQUARESIZE, row+SQUARESIZE+SQUARESIZE)) #slower

    pygame.display.update()
 
 
#initalize pygame
pygame.init()
pygame.display.set_caption('Matesim')
screen = pygame.display.set_mode(size)
#screen.convert() no difference

draw_board()
pygame.display.update()
 

print("####### Server is listening #######")
while not game_over:
    # read UDP packets
    data, address = s.recvfrom(4096)
    #print ('.')
    #print(data)
    #if data:
    #    print (data)
    #if address:
    #    print (address)
    tpm2NetHandle(data, PACKET_SIZE)

    clock.tick(100)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
 
        if event.type == pygame.KEYDOWN:
            print ('KEYDOWN')
            game_over = 1
 

# pygame.time.wait(3000)
pygame.display.quit()
pygame.quit()
sys.exit()
