# Checks if sudoku boards are legal

import math
#################################################
# Helper functions
#################################################

def almostEqual(d1, d2, epsilon=10**-7):
    # note: use math.isclose() outside 15-112 with Python version 3.5 or later
    return (abs(d2 - d1) < epsilon)

import decimal
def roundHalfUp(d):
    # Round to nearest with ties going away from zero.
    rounding = decimal.ROUND_HALF_UP
    # See other rounding options here:
    # https://docs.python.org/3/library/decimal.html#rounding-modes
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))

### Your lab5 functions below ###

def areLegalValues(values):
    if ((len(values)**.5)%1) == 0:
        #checks if the board is a square
        for i in range(len(values)):
            if values[i] > len(values):
                #checks that numbers are less than or equal to
                #the maximum number of squares
                return False
            for j in range(i + 1,len(values)):
                if values[i] > 0 and values[i] == values[j]:
                    #checks if there are any repeats in the list
                    return False
        return True
    else:
        return False

def isLegalRow(board, row):
    #checks if all values in a row are legal
    return(areLegalValues(board[row]))

def isLegalCol(board, col):
    column = []
    #creates a column and then checks if all values
    #within it are legal
    for i in range(len(board)):
        column.append(board[i][col])
    return areLegalValues(column)

def isLegalBlock(board, block):
    N = int(math.sqrt(len(board)))
    resultBlock = []
    for i in range((block // N) * N, (((block // N) + 1) * N)):
        for j in range((block % N)*N, ((block % N) + 1) * N):
            #adds all values within a block to the list resultBlock
            resultBlock.append(board[i][j])
    #checks if all values in the block are legal
    return areLegalValues(resultBlock)

def isLegalSudoku(board):
    for i in range(len(board)):
        #checks if all rows, columns, and blocks are legal
        if isLegalRow(board, i) == False:
            return False
        if isLegalCol(board, i) == False:
            return False
        if isLegalBlock(board, i) == False:
            return False
    return True