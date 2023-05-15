#!/usr/bin/env python3

# Generates deposition fraction
# Usage: python deposition_fraction.py <latest particle position csv>

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

## segments (z from 0.02)
def categorise(row):  
    if   row['z'] >= -0.06:
        return 1
    elif row['z'] >= -0.180 and row['x'] >= -0.016 and row['x'] < 0.002:
        return 2
    elif row['z'] >= -0.200 and row['x'] >= -0.018 and row['x'] < 0.002:
        return 3
    elif row['z'] >= -0.216 and row['x'] >= -0.006 and row['x'] < 0.030:
        return 4
    elif row['z'] >= -0.220 and row['x'] >=  0.025 and row['x'] < 0.037:
        return 5
    elif row['z'] >= -0.228 and row['z'] < -0.215 and row['x'] >= 0.031 and row['x'] < 0.042:
        return 6
    elif row['z'] >= -0.217 and row['z'] < -0.207 and row['x'] >= 0.033 and row['x'] < 0.047:
        return 7
    elif row['z'] >= -0.207 and row['z'] < -0.187 and row['x'] >= -0.026 and row['x'] < -0.007:
        return 8
    elif row['z'] >= -0.206 and row['z'] < -0.190 and row['x'] >= -0.037 and row['x'] < -0.023:
        return 9
    elif row['z'] >= -0.223 and row['z'] < -0.205 and row['x'] >= -0.034 and row['x'] < -0.014:
        return 10
    elif row['z'] >= -0.230 and row['z'] < -0.221 and row['x'] >= -0.049 and row['x'] < -0.031:
        return 11
    elif row['z'] >= -0.246 and row['z'] < -0.226 and row['x'] >= -0.042 and row['x'] < -0.032:
        return 12
    elif row['z'] >= -0.210 and row['z'] < -0.150 and row['x'] >= 0.041 and row['x'] < 0.090:
        return 13
    elif row['z'] >= -0.260 and row['z'] < -0.220 and row['x'] >= 0.011 and row['x'] < 0.046:
        return 14
    elif row['z'] >= -0.310 and row['z'] < -0.230 and row['x'] >= 0.033 and row['x'] < 0.083:
        return 15
    elif row['z'] >= -0.245 and row['z'] < -0.205 and row['x'] >= 0.047 and row['x'] < 0.111:
        return 16
    elif row['z'] >= -0.260 and row['z'] < -0.222 and row['x'] >= -0.110 and row['x'] < -0.047:
        return 17
    elif row['z'] >= -0.310 and row['z'] < -0.230 and row['x'] >= -0.066 and row['x'] < -0.020 and row['y'] >= 0.080 and row['y'] < 0.130:
        return 18
    elif row['z'] >= -0.200 and row['z'] < -0.140 and row['x'] >= -0.110 and row['x'] < -0.040 and row['y'] >= 0.080 and row['y'] < 0.134:
        return 19
    elif row['z'] >= -0.245 and row['z'] < -0.225 and row['x'] >= -0.100 and row['x'] < -0.044 and row['y'] >= 0.095 and row['y'] < 0.110:
        return 20
    elif row['z'] >= -0.230 and row['z'] < -0.150 and row['x'] >= -0.090 and row['x'] < -0.020 and row['y'] >= 0.110 and row['y'] < 0.210:
        return 21
    elif row['z'] >= -0.260 and row['z'] < -0.220 and row['x'] >= -0.070 and row['x'] < -0.020 and row['y'] >= 0.120 and row['y'] < 0.180:
        return 22
    else:
        return -1
    
df = pd.read_csv(sys.argv[1])
df['section'] = df.apply(lambda row: categorise(row), axis=1)

# particles = df[df['deposited'] == 1].shape[0]

df_grouped = pd.DataFrame(df[(df['deposition'] == 1) & (df['escaped'] == 0)]['section'])
particles = df_grouped.shape[0]

# df_grouped = pd.DataFrame(df[(df['escaped'] == 0)]['section'])
df_grouped['count'] = 1
df_grouped = df_grouped.groupby('section').sum('count').reset_index()
df_grouped['Deposition fraction'] = (df_grouped['count'] / particles) * 100
df_grouped.sort_values(by=['section'], inplace=True)

print("Total particles: ", df.shape[0])
print("Total deposited: ", particles)
print("Deposition percentage: ", particles / df.shape[0] * 100)
print("Total escaped: ", df[df['escaped'] == 1].shape[0])
print("Escape percentage: ", df[df['escaped'] == 1].shape[0] / df.shape[0] * 100)
print("Total stagnant: ", df[df['deposition'] == 0].shape[0])
print("Stagnant percentage: ", df[df['deposition'] == 0].shape[0] / df.shape[0] * 100)
print("Total error: ", df[df['error'] == 1].shape[0])
print("Error percentage: ", df[df['error'] == 1].shape[0] / df.shape[0] * 100)
print(df_grouped)

plt.plot(df_grouped['section'], df_grouped['Deposition fraction'], marker="x")
plt.xlabel("Segments")
plt.ylabel("Deposition fraction (%)")
plt.yscale("log")
plt.xticks(list(range(0, 22, 2)))
plt.yticks([0.001, 0.01, 0.1, 1, 10, 100])

if len(sys.argv) > 2 and sys.argv[2] == 'save':
    plt.savefig('deposition_fraction.png', dpi=300)
else:
    plt.show()

