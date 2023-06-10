#!/usr/bin/env python3

# Generates deposition fraction
# Usage: python deposition_fraction.py <latest particle position csv> <save/show> <particle diameter>
# save/show -> optional, default is show
# particle diameter -> optional, default is 4.3; 0 -> don't add from paper

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
    elif row['z'] >= -0.225 and row['z'] < -0.205 and row['x'] >= -0.034 and row['x'] < -0.014:
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
    elif row['z'] >= -0.310 and row['z'] < -0.230 and row['x'] >= -0.066 and row['x'] < -0.020 and row['y'] >= 0.080 and row['y'] < 0.120:
        return 18
    elif row['z'] >= -0.200 and row['z'] < -0.140 and row['x'] >= -0.110 and row['x'] < -0.040 and row['y'] >= 0.080 and row['y'] < 0.134:
        return 19
    elif row['z'] >= -0.245 and row['z'] < -0.225 and row['x'] >= -0.100 and row['x'] < -0.044 and row['y'] >= 0.095 and row['y'] < 0.110:
        return 20
    elif row['z'] >= -0.230 and row['z'] < -0.150 and row['x'] >= -0.090 and row['x'] < -0.020 and row['y'] >= 0.110 and row['y'] < 0.210:
        return 21
    elif row['z'] >= -0.290 and row['z'] < -0.220 and row['x'] >= -0.070 and row['x'] < -0.025 and row['y'] >= 0.120 and row['y'] < 0.180:
        return 22
    else:
        return -1

def les1(size=4.3):
    if size == 2.5:
        return [1.383, 0.162, 0.281, 0.077, 0.355, 0.206, 0.180, 0.330, 0.285, 0.246, 0.623, 0.289, 0.090, 0.121, 0.400, 0.272, 0.492, 0.361, 0.355, 0.642, 0.928, 0.412]
    if size == 4.3:
        return [3.113, 0.454, 0.749, 0.295, 1.695, 1.347, 1.259, 0.972, 1.280, 1.079, 3.840, 2.167, 0.257, 0.651, 1.829, 1.291, 2.654, 1.686, 4.334, 4.634, 2.537, 4.704]
    if size == 8:
        return [22.495, 4.569, 5.376, 3.664, 4.706, 2.848, 1.602, 6.231, 3.502, 5.142, 7.768, 4.992, 0.167, 0.082, 6.044, 1.361, 1.554, 6.900, 4.991, 2.385, 1.381, 1.123]
    if size == 10:
        return [42.115, 8.121, 6.752, 4.776, 2.232, 1.488, 0.446, 5.784, 1.613, 4.180, 4.272, 2.492, 0.023, 0.005, 2.264, 0.297, 0.192, 3.767, 1.131, 0.272, 0.156, 0.076]

def les2(size=4.3):
    if size == 2.5:
        return [12.478, 3.354, 1.092, 0.478, 0.901, 1.060, 0.766, 0.744, 0.862, 0.801, 1.404, 1.247, 0.888, 0.813, 4.064, 2.122, 2.571, 2.810, 3.354, 2.154, 2.285, 2.353]
    if size == 4.3:
        return [17.977, 5.771, 1.797, 0.849, 1.376, 1.841, 1.507, 1.368, 1.747, 1.660, 3.122, 2.834, 0.857, 0.733, 7.614, 3.547, 3.960, 6.137, 7.182, 3.707, 4.274, 4.637]
    if size == 8:
        return [37.706, 10.597, 2.978, 2.726, 2.645, 1.750, 0.999, 4.371, 2.316, 4.183, 6.048, 3.402, 0.218, 0.004, 4.917, 1.321, 1.600, 6.412, 4.115, 1.227, 0.998, 0.998]
    if size == 10:
        return [48.105, 9.008, 3.854, 3.205, 1.567, 0.812, 0.295, 5.217, 1.166, 4.057, 4.336, 2.567, 0.013, 0.000, 2.073, 0.306, 0.291, 3.603, 0.893, 0.144, 0.123, 0.026]

def rans1(size=4.3):
    if size == 2.5:
        return [18.460, 6.385, 1.178, 1.161, 1.015, 1.061, 0.601, 1.589, 1.127, 1.389, 1.873, 1.368, 0.510, 0.517, 2.526, 1.030, 1.791, 2.310, 2.310, 1.818, 1.368, 1.738]
    if size == 4.3:
        return [20.087, 7.173, 1.506, 1.534, 1.328, 1.765, 0.885, 1.831, 1.409, 1.928, 3.059, 2.123, 0.548, 0.403, 2.970, 1.285, 2.227, 3.234, 3.293, 2.219, 1.540, 2.630]
    if size == 8:
        return [25.332, 7.774, 3.308, 3.983, 2.982, 2.299, 1.053, 4.103, 1.996, 4.356, 4.387, 5.204, 0.311, 0.165, 5.321, 1.093, 1.259, 7.005, 3.117, 1.287, 0.843, 1.952]
    if size == 10:
        return [34.614, 7.092, 4.738, 5.420, 2.275, 1.960, 0.558, 4.528, 1.178, 4.331, 2.642, 5.257, 0.099, 0.104, 3.358, 0.378, 0.302, 5.927, 1.214, 0.272, 0.168, 0.502]

def rans3(size=4.3):
    if size == 2.5:
        return [1.475, 0.123, 0.103, 0.049, 0.109, 0.073, 0.039, 0.176, 0.112, 0.114, 0.128, 0.071, 0.054, 0.053, 0.211, 0.132, 0.163, 0.136, 0.190, 0.284, 0.231, 0.204]
    if size == 4.3:
        return [2.992, 0.503, 0.462, 0.307, 0.878, 0.869, 0.967, 0.722, 1.146, 1.117, 1.646, 1.030, 0.186, 0.397, 1.670, 1.425, 1.452, 1.133, 2.054, 2.123, 1.866, 1.845]
    if size == 8:
        return [7.271, 1.177, 1.317, 0.971, 1.720, 1.562, 1.356, 1.366, 1.882, 1.516, 4.519, 4.104, 0.635, 0.721, 3.616, 2.512, 2.727, 2.299, 3.725, 3.187, 2.768, 2.830]
    if size == 10:
        return [14.112, 2.275, 2.346, 2.144, 3.958, 2.763, 1.989, 1.765, 2.208, 1.791, 6.580, 5.420, 0.887, 0.887, 4.017, 3.069, 2.526, 2.311, 3.459, 2.979, 2.490, 2.310]
    
def paperDf(size=4.3):
    return les1(size), les2(size), rans1(size), rans3(size)
    
df = pd.read_csv(sys.argv[1])
df['section'] = df.apply(lambda row: categorise(row), axis=1)

df_grouped = pd.DataFrame(df[(df['deposition'] == 1) & (df['escaped'] == 0)]['section'])
particles = df_grouped.shape[0]

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

if (len(sys.argv) > 3 and sys.argv[3] != 0):
    les1, les2, rans1, rans3 = paperDf(float(sys.argv[3]))
    plt.plot(list(range(1, 23)), les1, marker="o", label="LES1")
    plt.plot(list(range(1, 23)), les2, marker="s", label="LES2")
    plt.plot(list(range(1, 23)), rans1, marker="v", label="RANS1")
    plt.plot(list(range(1, 23)), rans3, marker="1", label="RANS3")
plt.plot(df_grouped['section'], df_grouped['Deposition fraction'], marker="x", label="simulation")
plt.xlabel("Segments")
plt.ylabel("Deposition fraction (%)")
plt.yscale("log")
plt.title("Deposition fraction for different segments (size = " + str(sys.argv[3]) + ")")
plt.legend()
plt.xticks(list(range(0, 22, 2)))
plt.yticks([0.001, 0.01, 0.1, 1, 10, 100])

if len(sys.argv) > 2 and sys.argv[2] == 'save':
    plt.savefig('deposition_fraction.png', dpi=300)
else:
    plt.show()

