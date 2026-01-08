import pandas as pd

def load_data():
    df = pd.read_csv("data/supply_chain_data.csv")
    return df