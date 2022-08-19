%% Housekeeping
 
addpath('ximu_matlab_library');	% include x-IMU MATLAB library
addpath('quaternion_library');	% include quatenrion library
close all;                     	% close all figures
clear;                         	% clear all variables
clc;                          	% clear the command terminal

%%Connect
smartpen = ble("SmartPen");
imu = characteristic(smartpen, "ce34243c-1ef3-11ed-861d-0242ac120002", "ce3425fe-1ef3-11ed-861d-0242ac120002");
%%Calibrate Magnetometer

%% Import data
msgfig = msgbox("Now Start sampling",'modal');
uiwait(msgfig);


SampleData = 30;


f = waitbar(0, "Move imu", 'Name', "Read data from imu");
tic

for c = 1:SampleData
    waitbar(c/SampleData,f)
    read(imu);
end

timeInt = toc;
delete(f);

sampleFrequency = SampleData / timeInt;
samplePeriod = 1/sampleFrequency;
