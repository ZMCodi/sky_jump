import os

list = os.listdir("player_faces")

for face in list:
    print(face.removesuffix(".png"))
