from tkinter import *
from time import sleep

window = Tk()
canvas = Canvas(window, width=800, height=800, background="lightblue")
canvas.pack()

player = canvas.create_rectangle((375, 750, 425, 800), fill="white")

xVel = 10
isOnGround = True
ground_Y=750
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

def jump(event):
    global isOnGround
    if isOnGround:  # Only jump if on ground
        isOnGround = False
        diff = 0
        y = -3
        grav = .1
        while diff >= 0:
            canvas.move(player, 0, y)
            canvas.update()
            sleep(.01)
            diff -= y
            y += grav
        
        # Check if we're back on ground
        coords = canvas.coords(player)
        if coords[1] >= ground_Y:
            isOnGround = True
            # Snap back to ground exactly
            canvas.coords(player, coords[0], ground_Y, coords[2], ground_Y + 50)
    

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
canvas.bind('<Up>', jump)


updatePlayer()
window.mainloop()