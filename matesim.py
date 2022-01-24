import numpy as np
import pygame
import pygame.time
import socket
import sys
import math

# erledigt: 
# * Spielfeld auf 30x28 vergrößert
# * Pixel kann jede Farbe annehemen
#
# TODO: Daten per UDP (tpm2.net) oder seriell (TPM2) empfangen
#
 
BLUE = (0,0,255)
BLACK = (0,0,0)
RED = (255,0,0)
YELLOW = (255,255,0)
 
ROW_COUNT = 28
COLUMN_COUNT = 30

clock = pygame.time.Clock()

port = 65506
PACKET_SIZE = 1357;
packetBuffer = np.zeros(PACKET_SIZE)

# das klappt noch nicht: 
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Bind the socket to the port
#server_address = ('127.0.0.1', port)
#s.bind(server_address)

def readTPM2file():
    global rgbArray
    file1 = open("../content/rubik.tpm2", "rb")
 
    print("readTPM2file")
    packetBuffer = file1.read()
    file1.close()
    if ( packetBuffer[0] == 0xC9):  # header identifier
        print ('packet start')
        blocktype = packetBuffer[1] # block type (0xDA)
        framelength = (packetBuffer[2] << 8) | packetBuffer[3]
        if (blocktype == 0xDA):
            print ('blocktype=DA')
            row=0
            col=0
            packetindex = 6
            while(packetindex < (framelength + 6)): 
                    r =packetBuffer[packetindex]
                    g =packetBuffer[packetindex+1]
                    b =packetBuffer[packetindex+2]
                    # print (row,col, r,g,b)
                    rgbArray[row][col][0] = r
                    rgbArray[row][col][1] = g
                    rgbArray[row][col][2] = b
                  
                    col+=1
                    packetindex +=3
                    if (col == COLUMN_COUNT):
                        col = 0
                        row +=1
            #pixels.show()
            #led_index = 0
            
 
    return(rgbArray)
    


# work in progress:
def tpm2NetHandle(packetBuffer, PACKET_SIZE):

    print("r")
    #We've received a packet, read the data from it
   
    if ( packetBuffer[0] == 0x9C):  # header identifier (packet start)
        blocktype = packetBuffer[1] # block type (0xDA)
        framelength = (packetBuffer[2] << 8) | packetBuffer[3] # frame length (0x0069) = 105 leds
        packagenum = packetBuffer[4]   # packet number 0-255 0x00 = no frame split (0x01)
        numpackages = packetBuffer[5]   # total packets 1-255 (0x01)
                   
        if (blocktype == 0xDA): 
        
            if ((cb >= framelength + 7) and (packetBuffer[6 + framelength] == 0x36)): 
          #header end (packet stop)
                i = 0
                packetindex = 6
                
                col=0
                row = 0
          
                while(packetindex < (framelength + 6)): 
                    r =packetBuffer[packetindex]
                    g =packetBuffer[packetindex+1]
                    b =packetBuffer[packetindex+2]
                    rgbArray[row][col][0] = r
                    rgbArray[row][col][1] = r
                    rgbArray[row][col][2] = r
                 
                    
                    col +=1
                    packetindex +=3
                    if (col == COLUMN_COUNT):
                        col = 0
                        row +=1
                    
          
        if((packagenum == numpackages) and (led_index== NUMPIXELS)): 
            pixels.show()
            led_index = 0
     
 
def create_board():
    board = np.zeros((ROW_COUNT,COLUMN_COUNT))
    rgbArray = np.zeros((ROW_COUNT,COLUMN_COUNT,3), 'uint8')
    return board,rgbArray
 
def drop_piece(board, row, col, piece):
    board[row][col] = piece
    print ('row,col:', row,col)
    if piece == 1:   #red
        rgbArray[row][col][0] = 255
    if piece == 2:   #green
        rgbArray[row][col][1] = 255
 
def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0
 
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r
 
def print_board(rgbArray):
    print(np.flip(rgbArray, 0))
 
def winning_move(board, piece):
    return False
 
def draw_board(board):
    #for c in range(COLUMN_COUNT):
        #for r in range(ROW_COUNT):
        #    pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
          #  pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
     
    for c in range(COLUMN_COUNT):
        for row in range(ROW_COUNT):
            r = rgbArray[row][c][0]
            g = rgbArray[row][c][1]
            b = rgbArray[row][c][2]
            color = (r,g,b)
            pygame.draw.circle(screen, color, (int(c*SQUARESIZE+SQUARESIZE/2), height-int(row*SQUARESIZE+SQUARESIZE/2)), RADIUS)
           
    pygame.display.update()
 
 
board,rgbArray = create_board()
print_board(rgbArray)
game_over = False
turn = 0

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
#Calling function draw_board again

rgbArray = readTPM2file()
print ('rgbArray:')
print (rgbArray)
draw_board(board)
pygame.display.update()
 
myfont = pygame.font.SysFont("monospace", 75)


rgbArray = readTPM2file()

 
while not game_over:
    # read UDP packets
    #print("####### Server is listening #######")
    #print ('.')
    #data, address = s.recvfrom(4096)
    #if data:
    #    print (data)

    clock.tick(60)
 
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
 
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == 0:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
            else: 
                pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
        pygame.display.update()
        if event.type == pygame.KEYDOWN:
            print ('KEYDOWN')
            game_over = True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0,0, width, SQUARESIZE))
            #print(event.pos)
            # Ask for Player 1 Input
            if turn == 0:
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))
 
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 1)
 
                    if winning_move(board, 1):
                        label = myfont.render("Player 1 wins!!", 1, RED)
                        screen.blit(label, (40,10))
                        game_over = True
 
 
            # # Ask for Player 2 Input
            else:               
                posx = event.pos[0]
                col = int(math.floor(posx/SQUARESIZE))
 
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, 2)
 
                    if winning_move(board, 2):
                        label = myfont.render("Player 2 wins!!", 1, YELLOW)
                        screen.blit(label, (40,10))
                        game_over = True
 
            print_board(board)
            draw_board(board)
 
            turn += 1
            turn = turn % 2
 

# pygame.time.wait(3000)
pygame.display.quit()
pygame.quit()
sys.exit()
