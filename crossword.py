import random
import string

def wordList():
    return ["happy", "cheerful", "chipper", "effervescent", "jaunty", "jolly"]


def wordInput():
    words = []
    while True:
        word = input("Enter a word: ")
        if (word == ""):
            break
        else:
            words.append(word)
    return words

def DisplayWords(words):
    for i in words:
        print(i)

def createGrid():
    # height = int(input("Specify a height for the grid: "))
    # width = int(input("now the width: "))
    height = 15
    width = 15

    return [['_' for i in range(width)] for i in range(height)]

def displayGrid(grid):
    for i in range(len(grid)):
        print(grid[i])
    return grid

def placeWords(words, grid):
    height = len(grid)
    width = len(grid[0])
    directions = ["h", "v"]
    # loop through every word
    for word in words:
        # if word is longer than height or length
        # remove word
        if (len(word) > height and len(word) > width):
            continue
        # if word is longer than height
        # remove direction up or down
        elif (len(word) > height):
            direction = "h"
        # if word is longer than length
        # remove direction left or right
        elif (len(word) > width):
            direction = "v"
        else:
            direction = random.choice(directions)

        
        while True:
            # determine the starting position for each word based on direction
            if (direction == "h"):
                startCol = random.choice([i for i in range(width - len(word) + 1)])
                startRow = random.choice([i for i in range(height)])
            
                # check if any words are already in the spaces
                if (checkValid(word, startCol, startRow, grid, "h")):
                    # determine whether word is reversed or not
                    orientation = random.choice([1, -1])
                    for letter in word:
                        if (orientation == 1):
                            grid[startRow][startCol] = letter
                            startCol += 1
                        else:
                            revStartCol = startCol + len(word) - 1
                            grid[startRow][revStartCol] = letter
                            startCol -= 1
                else:
                    continue

            elif (direction == "v"):
                startRow = random.choice([i for i in range(height - len(word) + 1)])
                startCol = random.choice([i for i in range(width)])

                # check if any words are already in the spaces
                if (checkValid(word, startCol, startRow, grid, "v")):
                    orientation = random.choice([1, -1])
                    for letter in word:
                        if (orientation == 1):
                            grid[startRow][startCol] = letter
                            startRow += 1
                        else:
                            revStartRow = startRow + len(word) - 1
                            grid[revStartRow][startCol] = letter
                            startRow -= 1
                else:
                    continue
            break
            
    return grid

def checkValid(word, startCol, startRow, grid, direction):
    if (direction == "h"):
        for i in range(startCol, startCol + len(word)):
            if (grid[startRow][i] != "_"):
                return False
        return True
    else:
        for i in range(startRow, startRow + len(word)):
            if (grid[i][startCol] != "_"):
                return False
        return True
    

def fillCrossword(grid):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if (grid[r][c] == "_"):
                grid[r][c] = random.choice(string.ascii_lowercase)
    return grid


grid = createGrid()

words = wordList()

filledgrid = fillCrossword(grid)
displayGrid(filledgrid)
