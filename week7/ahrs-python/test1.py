from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R
import numpy as np
import csv
import csv

acc = list()
gyr = list()
mag = list()

with open('./test_data/acc.txt', 'r', encoding='utf-8') as f:
    rdr = csv.reader(f)
    for line in rdr:
        acc.append([float(f) for f in line])
with open('./test_data/gyro.txt', 'r', encoding='utf-8') as f:
    rdr = csv.reader(f)
    for line in rdr:
        gyr.append([float(f) for f in line])
with open('./test_data/mag.txt', 'r', encoding='utf-8') as f:
    rdr = csv.reader(f)
    for line in rdr:
        mag.append([float(f) for f in line])
num_samples = len(gyr)
sample_rate = 60

madgwick = Madgwick(frequency=sample_rate)

#Initial attitude
Q = np.tile([1., 0., 0., 0.], (len(gyr), 1))
Ro = np.zeros((3, 3, len(gyr)))

#update attitude
for t in range(1, num_samples):
    Q[t] = madgwick.updateMARG(Q[t-1], gyr=np.array(gyr[t]), acc=np.array(acc[t]), mag=np.array(mag[t]))
    Ro[:,:,t] = np.transpose(R.from_quat(Q[t]).as_matrix())

tcAcc = np.zeros_like(acc)
for i in range (1, len(acc)):
    tcAcc[i,:] = Ro[:,:,i] * np.array(acc)[i,:]
    print(i)
    #Ro[:,:,i]
linAcc = tcAcc - [np.zeros((len(tcAcc), 1)), np.zeros((len(tcAcc), 1)), np.ones((len(tcAcc), 1))]
linAcc = linAcc * 9.81

#print(linAcc)