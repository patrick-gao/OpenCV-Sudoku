# Main file - creates interface and combines hand detection with sudoku

import pygame
import cv2
import numpy as np
import math
import copy
from handtrackingclass import handTracking
import sudokuGenerator # Outside code from
# https://github.com/JoeKarlsson/python-sudoku-generator-solver/blob/master/sudoku.py
from sudoku import *

class SudokuOpenCV(object):
    def __init__(self):
        pygame.init()
        self.h = handTracking()
        self.screenSize = self.h.getScreenSize()                               # Gets frame dimensions from handTracking
        self.margin = 20
        self.running = True
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption('OpenCV Sudoku')
        self.width, self.height = self.screenSize[0], self.screenSize[1]
        self.boardDim = self.height-2*self.margin                                 # Sets side length of the sudoku board
        self.currentSquare = (0,0)                      # Coordinates of the current selected square on the sudoku board
        self.currSquareCoord = (0,0)       # Coordinates of the top left corner of current selected square on the screen
        self.unit = (self.boardDim)/9                                       # One square side length on the sudoku board
        self.board = [
            [ 5, 3, 0, 0, 7, 0, 0, 0, 0 ],
            [ 6, 0, 0, 1, 9, 5, 0, 0, 0 ],
            [ 0, 9, 8, 0, 0, 0, 0, 6, 0 ],
            [ 8, 0, 0, 0, 6, 0, 0, 0, 3 ],
            [ 4, 0, 0, 8, 0, 3, 0, 0, 1 ],
            [ 7, 0, 0, 0, 2, 0, 0, 0, 6 ],
            [ 0, 6, 0, 0, 0, 0, 2, 8, 0 ],
            [ 0, 0, 0, 4, 1, 9, 0, 0, 5 ],
            [ 0, 0, 0, 0, 8, 0, 0, 7, 9 ]
        ]

        # self.board = [
        #         [1,2,3,4,5,6,7,8,9],
        #         [5,0,8,1,3,9,6,2,4],
        #         [4,9,6,8,7,2,1,5,3],
        #         [9,5,2,3,8,1,4,6,7],
        #         [6,4,1,2,9,7,8,3,5],
        #         [3,8,7,5,6,4,0,9,1],
        #         [7,1,9,6,2,3,5,4,8],
        #         [8,6,4,9,1,5,3,7,2],
        #         [2,3,5,7,4,8,9,1,6]
        #         ]

        self.oBoard = copy.deepcopy(self.board)       # Copy of the original board to check for new inputs to self.board
        self.gameState = 0
        self.inGame = False                               # Used to check if the player is currently in a game of sudoku
        self.black = (0,0,0)
        self.white = (255, 255, 255)
        self.gray = (169, 169, 169)
        self.red = (255,0,0)
        self.green = (0,255,0)
        self.blue = (0,0,255)

    def drawBoard(self):                                                              # Draws sudoku board on the screen
        tlCorner = ((self.width/2) - self.boardDim/2, self.margin)                                     # Top left corner
        brCorner = ((self.width/2) + self.boardDim/2, self.height - self.margin)                   # Bottom right corner
        for i in range(0, 10):
            if i % 3 == 0:                                           # Makes thicker lines every 3rd line to show blocks
                pygame.draw.line(self.screen, self.black, (tlCorner[0] + i * self.unit, tlCorner[1]),
                                 (tlCorner[0] + i * self.unit, brCorner[1]), 3)
                pygame.draw.line(self.screen, self.black, (tlCorner[0],  tlCorner[1] + i * self.unit),
                                 (brCorner[0],  tlCorner[1] + i * self.unit), 3)
            else:                                                                          # Draws the rest of the lines
                pygame.draw.line(self.screen, self.black, (tlCorner[0] + i * self.unit, tlCorner[1]),
                                 (tlCorner[0] + i * self.unit, brCorner[1]))
                pygame.draw.line(self.screen, self.black, (tlCorner[0], tlCorner[1] + i * self.unit),
                                 (brCorner[0], tlCorner[1] + i * self.unit))
        return tlCorner, brCorner

    def cvToPy(image):                                                           # Converts OpenCV image to Pygame image
        return pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")

    def dist(point1, point2):                                                        # Finds distance between two points
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1]-point2[1])**2)

    def fillNumber(self, num):                      # Fills a square with a number if it results in a legal sudoku board
        initial = self.board[self.currentSquare[0]][self.currentSquare[1]]
        self.board[self.currentSquare[0]][self.currentSquare[1]] = num                                        # Try move
        if not (isLegalSudoku(self.board)):                                                             # Check if legal
            self.board[self.currentSquare[0]][self.currentSquare[1]] = initial                       # Undo if not legal

    def text_objects(self, text, font, color):                                       # Creates surface and Rect for text
        textSurface = font.render(str(text), True, color)
        return textSurface, textSurface.get_rect()

    def showMessage(self, text, location, fontSize, color):                                # Displays text on the screen
        largeText = pygame.font.SysFont("Arial", fontSize)                                   # Font initialized to Arial
        TextSurf, TextRect = SudokuOpenCV.text_objects(self, text, largeText, color)
        TextRect.center = location                                         # Text is placed relative to its center point
        self.screen.blit(TextSurf, TextRect)

    def fillSquare(self, x, y, num, tlCorner, color):          # Fills in a square on the sudoku board at position (x,y)
        if num > 0:
            SudokuOpenCV.showMessage(self, num, (tlCorner[0] + (x + .5)*self.unit, tlCorner[1]
                                                 + (y + .5)*self.unit), self.width//20, color)


    def boardNumbers(self, tlCorner):                                                # Fills in all numbers on the board
        for j in range(len(self.board)):
            for i in range(len(self.board[0])):
                if self.board[i][j] == self.oBoard[i][j]:         # If number is part of the original board, it is black
                    SudokuOpenCV.fillSquare(self, i, j, self.board[i][j], tlCorner, self.black)
                else:                                                                            # Otherwise, it is blue
                    SudokuOpenCV.fillSquare(self, i, j, self.board[i][j], tlCorner, self.blue)

    def checkWin(board):                                            # Checks if every square is filled with a number > 0
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == 0:
                    return False
        return True

    def drawRect(self, x, y, w, h, surface, color):               # Draws a rectangle with the top left corner at (x,y),
        tlCorner = (int(x), int(y))                                                             # width = w, height = h
        rect = pygame.Rect(tlCorner, (w, h))
        pygame.draw.rect(surface, color, rect)
        return rect

    def checkInRect(self, cx, cy, tlCorner, brCorner):                      # Checks if point (cx, cy) is in a rectangle
        if (cx < brCorner[0] and cx > tlCorner[0]):
            if (cy > tlCorner[1] and cy < brCorner[1]):
                return True
        return False

    def main(self):
        while self.running:
            frame, thresh, total, handList= self.h.loop()            # Gets hand detection information from handTracking
            self.screen.fill([0, 0, 0])
            self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))                     # Blit camera feed to Pygame screen
            #### Game States ####
            '''
            0 - Title Screen
            1 - Sudoku
            2 - Input
            3 - End Screen
            4 - Help Screen
            5 - Pause Screen
            6 - Difficulty Selection Screen
            '''
            if self.gameState == 0:                                                                       # Title Screen
                self.inGame = False
                self.screen.fill([0, 0, 0])
                self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))
                                                                                                      #Makes title label
                titleRect = SudokuOpenCV.drawRect(self, self.width*.2, self.height*.2,self.width*.6,
                                                  self.width*.15,self.screen,self.green)
                SudokuOpenCV.showMessage(self, "OpenCV Sudoku!", titleRect.center, self.width//15, self.black)
                                                                                                    # Makes start button
                startBtnRect = SudokuOpenCV.drawRect(self, self.width*.4, self.height*.6,self.width*.2,
                                                     self.width*.1,self.screen,self.blue)
                SudokuOpenCV.showMessage(self, "START", startBtnRect.center, self.width//20, self.black)
                                                                                                      #Makes help button
                helpBtnRect = SudokuOpenCV.drawRect(self, self.width*.85, self.height*.1, self.width*.1,
                                                    self.width*.1, self.screen, self. red)
                SudokuOpenCV.showMessage(self, "?", helpBtnRect.center, self.width//20, self.black)

                for hand in handList:                                  # Finds center points for each hand on the screen
                    cx, cy = hand[1]
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)
                                                              # On start button press, go to difficulty selection screen
                    if SudokuOpenCV.checkInRect(self, cx, cy, startBtnRect.topleft, startBtnRect.bottomright):
                        self.gameState = 6
                                                                               # On help button press, go to help screen
                    elif SudokuOpenCV.checkInRect(self, cx, cy, helpBtnRect.topleft, helpBtnRect.bottomright):
                        self.gameState = 4

            elif self.gameState == 1:                                                                    # Sudoku screen
                self.inGame = True                                                                 # Player is in a game
                tlCorner, brCorner = SudokuOpenCV.drawBoard(self)
                                                                                                #Draws two pause buttons
                pauseRect1 = SudokuOpenCV.drawRect(self, 0, 0, self.width*.1, self.height*.2, self.screen, self.red)
                pauseRect2 = SudokuOpenCV.drawRect(self, self.width*.9, 0, self.width*.1, self.height*.2,
                                                   self.screen, self.red)
                touch = 0                          # Keeps track of how many of the pause buttons the player is touching
                for hand in handList:                                  # Finds center points for each hand on the screen
                    cx, cy = hand[1]
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)

                    if SudokuOpenCV.checkInRect(self, cx, cy, tlCorner, brCorner):
                                                                        # Finds which square the player is hovering over
                        relPosX = cx - tlCorner[0]
                        relPoxY = cy - tlCorner[1]
                        normX = relPosX / self.boardDim
                        normY = relPoxY / self.boardDim
                        boardX = int(normX * 9)
                        boardY = int(normY * 9)
                        self.currSquareCoord = (tlCorner[0] + boardX * self.unit, tlCorner[1] + boardY * self.unit)
                        SudokuOpenCV.drawRect(self, self.currSquareCoord[0], self.currSquareCoord[1],
                                              self.unit, self.unit, self.screen, self.blue)
                        if total == 0:        # If the player makes a fist on a square, select it and go to input screen
                            self.currentSquare = (boardX, boardY)
                            self.currSquareCoord = (tlCorner[0] + boardX * self.unit, tlCorner[1] + boardY * self.unit)
                                                              # Player can only select squares that are originally empty
                            if self.oBoard[self.currentSquare[0]][self.currentSquare[1]] == 0:
                                self.gameState = 2

                    elif SudokuOpenCV.checkInRect(self, cx, cy, pauseRect1.topleft, pauseRect1.bottomright) or \
                         SudokuOpenCV.checkInRect(self, cx, cy, pauseRect2.topleft, pauseRect2.bottomright):
                        touch += 1
                if touch == 2:                                   # If both pause buttons are pressed, go to pause screen
                    self.gameState = 5

                SudokuOpenCV.drawBoard(self)
                SudokuOpenCV.boardNumbers(self, tlCorner)

                if SudokuOpenCV.checkWin(self.board) == True:              # If the board is full, then go to win screen
                    self.gameState = 3

            elif self.gameState == 2:                                                                     # Input screen
                tlCorner, brCorner = SudokuOpenCV.drawBoard(self)
                SudokuOpenCV.boardNumbers(self, tlCorner)
                                                        # Makes two circles which the player must touch to make an input
                marker1 = (int(.15 * self.width), int(.3 * self.height))
                marker2 = (int(.85 * self.width), int(.3 * self.height))
                markerRad = 40
                pygame.draw.circle(self.screen, self.blue, marker1, markerRad, 3)
                pygame.draw.circle(self.screen, self.blue, marker2, markerRad, 3)
                                                                           # Shows total number of fingers on the screen
                SudokuOpenCV.showMessage(self, "Total: " + str(total), (int(self.width*.85), int(.1*self.height)),
                                         self.width//20, self.black)

                for hand in handList:
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)
                                                                    # If the player touches at least one of the markers,
                                                            # attempt to input the number and return to the play screen
                    if (SudokuOpenCV.dist(hand[1], marker1) <= markerRad or \
                        SudokuOpenCV.dist(hand[1], marker2) <= markerRad):
                        SudokuOpenCV.fillNumber(self, total)
                        self.gameState = 1

                if handList == []:                                # If no hands are on the screen, return to play screen
                    self.gameState = 1

            elif self.gameState == 3:                                                                       # Win screen
                self.inGame = False                                                        # Player is no longer in game
                self.screen.fill([0, 0, 0])
                self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))
                bgRect = SudokuOpenCV.drawRect(self, self.width * .2, self.height * .2, self.width * .6,
                                               self.height * .6, self.screen, self.green)

                SudokuOpenCV.showMessage(self, "You Win!", (self.width // 2, self.height // 3),
                                         self.width//10, self.black)
                SudokuOpenCV.showMessage(self, "Press Esc to exit", (self.width // 2, int(self.height * .6)),
                                         self.width//20, self.black)
                SudokuOpenCV.showMessage(self, "Touch both circles to restart", (self.width // 2, int(self.height * .7))
                                         , self.width//20, self.black)

                                                 # Makes two markers which the player must touch to exit to start screen
                marker1 = (int(.15 * self.width), int(.6 * self.height))
                marker2 = (int(.85 * self.width), int(.6 * self.height))
                markerRad = 30
                pygame.draw.circle(self.screen, self.blue, marker1, markerRad, 3)
                pygame.draw.circle(self.screen, self.blue, marker2, markerRad, 3)

                touch = 0
                for hand in handList:
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)
                    if (SudokuOpenCV.dist(hand[1], marker1) <= markerRad or \
                        SudokuOpenCV.dist(hand[1], marker2) <= markerRad):
                        touch += 1

                if touch == 2:                                     # If both markers are touched, return to start screen
                    SudokuOpenCV.fillNumber(self, total)
                    self.gameState = 0

            elif self.gameState == 4:                                                                      # Help screen
                self.screen.fill([0, 0, 0])
                self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))
                infoRect = SudokuOpenCV.drawRect(self, self.width*.1, self.height*.1, self.width*.8, self.height*.8,
                                                 self.screen, self.white)

                info = \
                ''' 
                Welcome to Sudoku on OpenCV! Use your hands to navigate 
                the game, but make sure to wear dark long sleeves! 
                Play against a well-lit, even white background.
                The cursors are mapped to the center of each of your hands 
                and marked with a red circle. Move the cursor to a square 
                on the board you want to select, and make a fist to enter 
                input mode. Then put up the desired amount fingers 
                corresponding to the number you want to input and touch 
                at least one of the blue circles. Pause by touching both
                hands to the red squares. Press the back button 
                to return to the start screen.
                '''
                lines = info.splitlines()
                for i, l in enumerate(lines):                # For each line of the info, display the line on the screen
                    SudokuOpenCV.showMessage(self, l, (int(self.width*.45), infoRect.top + self.width//30 * (i+1)),
                                             self.width//30, self.black)
                                                                                                     # Makes back button
                backBtnRect = SudokuOpenCV.drawRect(self, self.width * .1, self.height * .8, self.width * .1,
                                                    self.height * .1, self.screen, self.red)
                SudokuOpenCV.showMessage(self, "Back", backBtnRect.center, self.width // 30, self.black)

                for hand in handList:
                    cx, cy = hand[1]
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)
                    if SudokuOpenCV.checkInRect(self, cx, cy, backBtnRect.topleft, backBtnRect.bottomright):
                        if self.inGame:                              # If the player is in a game, return to play screen
                            self.gameState = 5
                        else:                                   # If the player is not in a game, return to start screen
                            self.gameState = 0

            elif self.gameState == 5:                                                                     # Pause screen
                self.screen.fill([0, 0, 0])
                self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))
                pauseRect = SudokuOpenCV.drawRect(self, self.width * .1, self.height * .1, self.width * .8,
                                                  self.height * .8, self.screen, self.white)
                SudokuOpenCV.showMessage(self, "Paused", (self.width//2, pauseRect.top + int(pauseRect.height*.1)),
                                         self.width//20, self.black)
                                                                                                   # Makes resume button
                resumeRect = SudokuOpenCV.drawRect(self, pauseRect.left + pauseRect.width//4,
                                                    pauseRect.top + .25*pauseRect.height, .5*pauseRect.width,
                                                   .1*pauseRect.height, self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Resume", resumeRect.center, self.width//20, self.black)
                                                                                                  # Makes restart button
                restartRect = SudokuOpenCV.drawRect(self, pauseRect.left + pauseRect.width//4,
                                                    pauseRect.top + .5*pauseRect.height, .5*pauseRect.width,
                                                    .1*pauseRect.height, self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Restart", restartRect.center, self.width//20, self.black)
                                                                                                     # Makes exit button
                exitRect = SudokuOpenCV.drawRect(self, pauseRect.left + pauseRect.width//4,
                                                 pauseRect.top + .75*pauseRect.height, .5*pauseRect.width,
                                                 .1*pauseRect.height, self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Exit", exitRect.center, self.width//20, self.black)
                                                                                                     # Makes help button
                helpBtnRect = SudokuOpenCV.drawRect(self, self.width * .8, self.height * .8, self.width * .1,
                                                    self.height * .1, self.screen, self.red)
                SudokuOpenCV.showMessage(self, "?", helpBtnRect.center, self.width // 20, self.black)

                for hand in handList:
                    cx, cy = hand[1]
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)

                    if SudokuOpenCV.checkInRect(self, cx, cy, helpBtnRect.topleft, helpBtnRect.bottomright):
                        self.gameState = 4                                  # Help button - Brings player to help screen
                    elif SudokuOpenCV.checkInRect(self, cx, cy, resumeRect.topleft, resumeRect.bottomright):
                        self.gameState = 1                                 # Resumes game - brings player to play screen
                    elif SudokuOpenCV.checkInRect(self, cx, cy, restartRect.topleft, restartRect.bottomright):
                        self.board = copy.deepcopy(self.oBoard)                                           # Restart game
                        self.gameState = 1                                       # Reset board and return to play screen
                    elif SudokuOpenCV.checkInRect(self, cx, cy, exitRect.topleft, exitRect.bottomright):
                        self.gameState = 0                                          # Exit game - return to start screen

            elif self.gameState == 6:                                                      # Difficulty selection screen
                self.screen.fill([0, 0, 0])
                self.screen.blit(SudokuOpenCV.cvToPy(frame), (0, 0))
                                                                                             # Make background rectangle
                bgRect = SudokuOpenCV.drawRect(self, self.width * .1, self.height * .1, self.width * .8,
                                               self.height * .8, self.screen, self.white)
                SudokuOpenCV.showMessage(self, "Difficulty", (self.width//2, bgRect.top + int(bgRect.height*.1)),
                                         self.width//20, self.black)
                                                                                                     # Makes easy button
                easyRect = SudokuOpenCV.drawRect(self, bgRect.left + bgRect.width//4,
                                                 bgRect.top + .25*bgRect.height, .5*bgRect.width, .1*bgRect.height,
                                                 self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Easy", easyRect.center, self.width//20, self.black)
                                                                                                   # Makes normal button
                normalRect = SudokuOpenCV.drawRect(self, bgRect.left + bgRect.width//4,
                                                   bgRect.top + .5*bgRect.height, .5*bgRect.width, .1*bgRect.height,
                                                   self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Normal", normalRect.center, self.width//20, self.black)
                                                                                                     # Makes hard button
                hardRect = SudokuOpenCV.drawRect(self, bgRect.left + bgRect.width//4,
                                                 bgRect.top + .75*bgRect.height, .5*bgRect.width, .1*bgRect.height,
                                                 self.screen, self.green)
                SudokuOpenCV.showMessage(self, "Hard", hardRect.center, self.width//20, self.black)
                                                                                                     # Makes back button
                backRect = SudokuOpenCV.drawRect(self, self.width * .8, self.height * .8, self.width * .1,
                                                    self.height * .1, self.screen, self.red)
                SudokuOpenCV.showMessage(self, "Back", backRect.center, self.width // 30, self.black)

                for hand in handList:
                    cx, cy = hand[1]
                    pygame.draw.circle(self.screen, self.red, hand[1], 20, 5)

                    if SudokuOpenCV.checkInRect(self, cx, cy, easyRect.topleft, easyRect.bottomright) and total == 0:
                        self.board = sudokuGenerator.main('Easy')       # Use sudoku generator to make random easy board
                        self.oBoard = copy.deepcopy(self.board)
                        self.gameState = 1
                    elif SudokuOpenCV.checkInRect(self, cx, cy, normalRect.topleft, normalRect.bottomright) \
                            and total == 0:
                        self.board = sudokuGenerator.main('Medium')   # Use sudoku generator to make random normal board
                        self.oBoard = copy.deepcopy(self.board)
                        self.gameState = 1
                    elif SudokuOpenCV.checkInRect(self, cx, cy, hardRect.topleft, hardRect.bottomright) and total == 0:
                        self.board = sudokuGenerator.main('Hard')       # Use sudoku generator to make random hard board
                        self.oBoard = copy.deepcopy(self.board)
                        self.gameState = 1
                    elif SudokuOpenCV.checkInRect(self, cx, cy, backRect.topleft, backRect.bottomright):
                        self.gameState = 0                                       # Return to start screen on back button

            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:                                   # Closes the game on escape press
                        exit()
                    elif event.key == pygame.K_SPACE:               # Goes to win screen on space for debugging purposes
                        self.gameState = 3
                    elif event.key == pygame.K_w:
                        self.board = [
                                    [1,2,3,4,5,6,7,8,9],
                                    [5,0,8,1,3,9,6,2,4],
                                    [4,9,6,8,7,2,1,5,3],
                                    [9,5,2,3,8,1,4,6,7],
                                    [6,4,1,2,9,7,8,3,5],
                                    [3,8,7,5,6,4,0,9,1],
                                    [7,1,9,6,2,3,5,4,8],
                                    [8,6,4,9,1,5,3,7,2],
                                    [2,3,5,7,4,8,9,1,6]
                                    ]

                        self.oBoard = copy.deepcopy(self.board)
                        self.gameState = 1
                    elif event.key == pygame.K_p:                                             # Pauses game on 'p' press
                        self.gameState = 5


game = SudokuOpenCV()
game.main()
