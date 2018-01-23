Patrick Gao
OpenCV Sudoku Readme

This project consists of 5 files: handtrackingclass.py, sudoku.py, sudokugame.py, sudokuGenerator.py, and haarcascade_frontalface_default.xml. Place all files in the same directory.

Install and import the necessary modules: OpenCV 3.0.0.10, PyGame 1.9.3, and NumPy 1.13.3
OpenCV can be tricky to install on Windows, but it is very convenient and quick through the PyCharm IDE. Simply open Settings > Project > Project Interpreter > Select Python 3.6
In the window below, press the plus sign on the right toolbar and then look for modules in the top left search bar. Select the right version and install.

Overview
handtrackingclass.py contains all the functions for hand detection, face removal, and finding the number of fingers raised, and therefore also handles the video input. 
Face removal uses Haar cascades (the haarcascade_frontalface_default.xml file developed by Intel) to detect a face, and then remove it by masking it. 
sudokugame.py imports the main hand detection loop in handtrackingclass.py, displaying the video input with the hand detection overlay, while also displaying and 
handling the game of Sudoku drawn over the video input. The game of Sudoku uses functions from sudokuGenerator.py to generate random boards of different difficulties, 
and uses sudoku.py to check player inputs to see if they are legal, and to see if the player has completed the board.

Additional instructions:
1. Hand detection is more accurate if all of the arm is covered with a dark long sleeve (pull sleeves up to wrists)
2. If closing the fist is not recognized at first, turn the fist forwards so that the knuckles are facing the screen, to minimize the vertical dimension of the hand contour
3. Keep hands in front of body and away from the face, about 1.5 to 2 feet away from the camera
4. Play in an evenly lit area against a solid background
