import pandas as pd

FILE_PATH = "resources_app/ia_vs_human.txt"

def read_ia_vs_human():

    with open(FILE_PATH, "r") as f:
        data = f.readlines()[0].split(" ")
    return [int(d) for d in data]

def update_ia_vs_human(player: str):

    points = read_ia_vs_human()

    if player == "ai":
        points[0] += 1
    elif player == "user":
        points[1] += 1

    points = [str(p) for p in points]
    to_write = " ".join(points)

    with open(FILE_PATH, "w") as f:
        f.write(to_write)
