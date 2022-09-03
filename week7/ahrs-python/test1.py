from ahrs.filters import Madgwick
from scipy.spatial.transform import Rotation as R
from scipy import signal
import numpy as np
import csv
import csv

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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

for t in range(0, num_samples):
    Ro[:,:,t] = np.transpose(R.from_quat(Q[t]).as_matrix())

tcAcc = np.zeros_like(acc)
for i in range (0, len(acc)):
    tcAcc[i,:] = np.matmul(Ro[:,:,i], np.transpose(np.array(acc)[i,:]))

linAcc = tcAcc - np.tile([0.,0.,1.], (len(tcAcc),1))
linAcc = linAcc * 9.81

linVel = np.zeros_like(linAcc)

for i in range (1,len(linAcc)):
    linVel[i,:] = linVel[i-1,:] + linAcc[i,:] * (1/sample_rate)

order = 1
filtCutOff = 0.1
b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
linVelHP = signal.filtfilt(b, a, linVel, padlen=0)

linPos = np.zeros_like(linVelHP)

for i in range (1, len(linVelHP)):
    linPos[i,:] = linPos[i-1,:] + linVelHP[i,:] * (1/sample_rate)

order = 1
filtCutOff = 0.1
b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
linPosHP = signal.filtfilt(b, a, linPos, padlen=0)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(linPosHP[:,0], linPosHP[:,1], linPosHP[:,2])
plt.show()