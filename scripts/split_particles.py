# Generates 2 groups of csv files for deposited particles and not deposited particles
# Usage: python split_particles.py <folder containing particles csv>

import os
import sys
import pandas as pd
from tqdm import tqdm

path = sys.argv[1] or "."
deposited_path = os.path.join(path, "deposited")
not_deposited_path = os.path.join(path, "not_deposited")

all_files = os.listdir(path) 

siminhale_files = [file for file in all_files if file.startswith("siminhale_") and file.endswith(".csv")]

N = len(siminhale_files)
print("Number of files: ", N)
print("Deposited path: ", deposited_path)
print("Not deposited path: ", not_deposited_path)

if not os.path.exists(deposited_path):
    os.makedirs(deposited_path)
    os.makedirs(not_deposited_path)

for i in tqdm(range(len(siminhale_files))):
    filename = siminhale_files[i]
    index = filename.split("_")[1].split(".")[0]
    df = pd.read_csv(os.path.join(path, filename))
    df_deposited = df[df["deposition"] == 1]
    df_not_deposited = df[df["deposition"] != 1]

    if df_deposited.empty:
       df_deposited[0, :] = [0 for _ in range(len(df.columns))] 

    df_deposited.to_csv(os.path.join(deposited_path, f"siminhale_deposited_{index}.csv"), index=False)
    df_not_deposited.to_csv(os.path.join(not_deposited_path, f"siminhale_not_deposited_{index}.csv"), index=False)
