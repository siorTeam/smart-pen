from ahrs.filters import Madgwick
from scipy import signal
from quatern2rotMat import quaternion_rotation_matrix as Rotation
import numpy as np
import csv
import math
from madgwickahrs import MadgwickAHRS
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

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

acc = np.array(acc)
gyr = np.array(gyr)
mag = np.array(mag)

ahrs = MadgwickAHRS(sampleperiod=(1/sample_rate),  beta=0.1)


#Q = np.tile([1., 0., 0., 0.], (len(gyr), 1))
Q = np.zeros((1000, 4))
R = np.zeros((3, 3, len(gyr)))

#update attitude
for i in range(num_samples):
    ahrs.update(gyroscope = gyr[i, :]*(math.pi/180), accelerometer = acc[i, :], magnetometer = mag[i, :])
    R[:,:,i] = np.transpose(Rotation(ahrs.quaternion.q))
    Q[i, :] = ahrs.quaternion.q
print(Q)

tcAcc = np.zeros_like(acc)
for i in range (0, len(acc)):
    tcAcc[i,:] = np.matmul(R[:,:,i], np.transpose(acc[i,:]))

linAcc = tcAcc - np.tile([0.,0.,1.], (len(tcAcc),1))
linAcc = linAcc * 9.81

linVel = np.zeros_like(linAcc)

for i in range (1,len(linAcc)):
    linVel[i,:] = linVel[i-1,:] + linAcc[i,:] * (1/sample_rate)

order = 1
filtCutOff = 0.1
b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
linVelHP = signal.filtfilt(b, a, linVel, axis = 0)

linPos = np.zeros_like(linVelHP)

for i in range (1, len(linVelHP)):
    linPos[i,:] = linPos[i-1,:] + linVelHP[i,:] * (1/sample_rate)

order = 1
filtCutOff = 0.1
b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
linPosHP = signal.filtfilt(b, a, linPos, axis = 0)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(linPosHP[:,0], linPosHP[:,1], linPosHP[:,2])

plt.show()
