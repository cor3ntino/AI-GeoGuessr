import pandas as pd

FILE_PATH = "resources_app/rankings_competition.csv"

def read_rankings():

    return pd.read_csv(FILE_PATH, sep="|")

def update_rankings(pseudo, location, points):

    df = read_rankings()

    ind = df.index[(df["Name"] == pseudo) & (df["Location"] == location)].tolist()

    if len(ind) > 0:
        previous_points = df["Points"].iloc[ind[0]]
        if previous_points > points:
            df["Points"].iloc[ind[0]] = points

    else:
        df = pd.concat([df, pd.DataFrame(data=[[pseudo, location, points]], columns=["Name", "Location", "Points"])], ignore_index=True)

    df.to_csv(FILE_PATH, sep="|", index=False)
