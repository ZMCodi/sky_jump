from tkinter import *
from time import sleep

window = Tk()
canvas = Canvas(window, width=800, height=800, background="lightblue")
canvas.pack()

player = canvas.create_rectangle((375, 750, 425, 800), fill="white")

xVel = 20

movingLeft = False
movingRight = False

def startMoveLeft(event):
    global movingLeft
    movingLeft = True

def stopMoveLeft(event):
    global movingLeft
    movingLeft = False

def startMoveRight(event):
    global movingRight
    movingRight = True

def stopMoveRight(event):
    global movingRight
    movingRight = False

def updatePlayer():
    if movingLeft:
        canvas.move(player, -xVel, 0)
    if movingRight:
        canvas.move(player, xVel, 0)
    window.after(16, updatePlayer)




canvas.focus_set()
canvas.bind('<KeyPress-Left>', startMoveLeft)
canvas.bind('<KeyRelease-Left>', stopMoveLeft)
canvas.bind('<KeyPress-Right>', startMoveRight)
canvas.bind('<KeyRelease-Right>', stopMoveRight)


updatePlayer()
window.mainloop()