# Generates 2 groups of csv files for deposited particles and not deposited particles
# Usage: python split_particles.py <folder containing particles csv>

import os
import sys
import pandas as pd

# if len(sys.argv) == 1:
#     print("please pass the number of timesteps as argument")
#     quit()

path = sys.argv[1] or "."
deposited_path = os.path.join(path, "deposited")
not_deposited_path = os.path.join(path, "not_deposited")

all_files = os.listdir(path) 

siminhale_files = [file for file in all_files if file.startswith("siminhale_") and file.endswith(".csv")]

N = len(siminhale_files)
print("Number of files: ", N)
# N = int(sys.argv[2] or len(siminhale_files))

if not os.path.exists(deposited_path):
    os.makedirs(deposited_path)
    os.makedirs(not_deposited_path)

for filename in siminhale_files:
# for i in range(1, N, 1):
#     filename = f"siminhale_{i:04d}.csv"
#     if filename in siminhale_files:
    index = filename.split("_")[1].split(".")[0]
    df = pd.read_csv(os.path.join(path, filename))
    df_deposited = df[df["deposition"] == 1]
    df_not_deposited = df[df["deposition"] != 1]

    df_deposited.to_csv(os.path.join(deposited_path, f"siminhale_deposited_{index}.csv"), index=False)
    df_not_deposited.to_csv(os.path.join(not_deposited_path, f"siminhale_not_deposited_{index}.csv"), index=False)
