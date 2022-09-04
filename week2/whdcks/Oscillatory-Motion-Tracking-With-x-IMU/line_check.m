%% Housekeeping
addpath('ximu_matlab_library');	% include x-IMU MATLAB library
addpath('quaternion_library');	% include quatenrion library
close all;                     	% close all figures
clear;                         	% clear all variables
clc;                          	% clear the command terminal


sampleFrequency = 60;
samplePeriod = 1/sampleFrequency;

gyr = csvread("test_data\gyr.txt");
acc = csvread("test_data\acc.txt");
mag = csvread("test_data\mag.txt");


R = zeros(3,3,length(gyr));     % rotation matrix describing sensor relative to Earth
Q = zeros(1000, 4);

ahrs = MadgwickAHRS('SamplePeriod', 1/256, 'Beta', 0.1);
%KP값을 조절하여 자이로값과 자기센서값의 가중치를 선택가능
for i = 1:length(gyr)
    ahrs.Update(gyr(i,:) * (pi/180), acc(i,:), mag(i,:));	% gyroscope units must be radians
    Q(i,:) = ahrs.Quaternion;
    R(:,:,i) = quatern2rotMat(ahrs.Quaternion)';    % transpose because ahrs provides Earth relative to sensor
end

%% Calculate 'tilt-compensated' accelerometer

tcAcc = zeros(size(acc));  % accelerometer in Earth frame

for i = 1:length(acc)
    tcAcc(i,:) = R(:,:,i) * acc(i,:)';
end


%% Calculate linear acceleration in Earth frame (subtracting gravity)

linAcc = tcAcc - [zeros(length(tcAcc), 1), zeros(length(tcAcc), 1), ones(length(tcAcc), 1)];
linAcc = linAcc * 9.81;     % convert from 'g' to m/s/s


%% Calculate linear velocity (integrate acceleartion)

linVel = zeros(size(linAcc));

for i = 2:length(linAcc)
    linVel(i,:) = linVel(i-1,:) + linAcc(i,:) * samplePeriod;
end


%% High-pass filter linear velocity to remove drift

order = 1;
filtCutOff = 0.1;
% 0 < (2*filtCutOff)/(1/samplePeriod) < 1
[b, a] = butter(order, (2*filtCutOff)/(1/samplePeriod), 'high');
linVelHP = filtfilt(b, a, linVel);


%% Calculate linear position (integrate velocity)

linPos = zeros(size(linVelHP));

for i = 2:length(linVelHP)
    linPos(i,:) = linPos(i-1,:) + linVelHP(i,:) * samplePeriod;
end


%% High-pass filter linear position to remove drift

order = 1;
filtCutOff = 0.1;
% 0 < (2*filtCutOff)/(1/samplePeriod) < 1 
[b, a] = butter(order, (2*filtCutOff)/(1/samplePeriod), 'high');
linPosHP = filtfilt(b, a, linPos);

plot3(linPosHP(:,1), linPosHP(:,2), linPosHP(:,3) )