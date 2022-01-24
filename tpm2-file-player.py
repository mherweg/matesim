import numpy as np
import pygame
import pygame.time
import socket
import sys
import math

# erledigt: 
# * Spielfeld auf 30x28 vergrößert
# * Pixel kann jede Farbe annehemen
# * es kann TPM2 Dateien abspielen
# TODO: Daten per UDP (tpm2.net) oder seriell (TPM2) empfangen
#
 
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
 
ROW_COUNT = 28
COLUMN_COUNT = 30
MAXFRAMES = 10000
FRAMERATE = 25
filepath = "../content/wirbel.tpm2"
#filename = "../content/rubik.tpm2"
clock = pygame.time.Clock()


def readTPM2file():
    global rgbArray
    file1 = open(filepath, "rb")
 
    print("readTPM2file")
    packetBuffer = file1.read()
    file1.close()
    print("readTPM2file bytes:", len(packetBuffer) )
    
    i = 0
    frame = 0
    packetindex = 0
    while (packetindex < len(packetBuffer) ):
        if ( packetBuffer[packetindex] == 0xC9):  # header identifier
            #print ('packet start')
            packetindex +=1
            blocktype = packetBuffer[packetindex] # block type (0xDA)
            packetindex +=1
            framelength = (packetBuffer[packetindex] << 8) | packetBuffer[packetindex+1]
            packetindex +=2
            if (blocktype == 0xDA):
                #print ('blocktype=DA')
                row=ROW_COUNT-1
                col=0
                byte_of_frame=0
                #packetindex = i+4
                while(byte_of_frame < framelength ): 
                    # print (row,col, r,g,b)
                    rgbArray[frame][row][col][0] = packetBuffer[packetindex]
                    rgbArray[frame][row][col][1] = packetBuffer[packetindex+1]
                    rgbArray[frame][row][col][2] = packetBuffer[packetindex+2]
                  
                    col+=1
                    packetindex +=3
                    byte_of_frame +=3
                    if (col == COLUMN_COUNT):
                        col = 0
                        row -=1
            #print('endbyte(soll:54):',packetBuffer[packetindex] )
            #print('.')
            packetindex +=1
            frame +=1
            print (frame, packetindex)
 
    return(rgbArray,frame)
    


def create_board():
    rgbArray = np.zeros((MAXFRAMES,ROW_COUNT,COLUMN_COUNT,3), 'uint8')
    return rgbArray
 
def draw_board(frame):
    for c in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            r = rgbArray[frame][row][c][0]
            g = rgbArray[frame][row][c][1]
            b = rgbArray[frame][row][c][2]
            color = (r,g,b)
            pygame.draw.circle(screen, color, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(row*SQUARESIZE+SQUARESIZE/2)), RADIUS)
           
    pygame.display.update()


 
# program start 
rgbArray = create_board()


#initalize pygame
pygame.init()

#define our screen size
SQUARESIZE = 30
 
#define width and height of board
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT+1) * SQUARESIZE
 
size = (width, height)
 
RADIUS = int(SQUARESIZE/2 - 5)
 
screen = pygame.display.set_mode(size)

rgbArray,last_frame = readTPM2file()
#print ('rgbArray:')
#print (rgbArray)
frame=0
draw_board(frame)
pygame.display.update()
game_over = False

while not game_over:
    clock.tick(FRAMERATE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            print ('KEYDOWN')
            game_over = True
        if event.type == pygame.MOUSEBUTTONDOWN:
            pass
    frame +=1
    if (frame > last_frame):
        frame = 0
        print (".",end="")
    draw_board(frame)
            


pygame.display.quit()
pygame.quit()
sys.exit()
