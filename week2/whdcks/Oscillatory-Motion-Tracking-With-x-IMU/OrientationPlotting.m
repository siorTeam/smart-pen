%% Housekeeping
addpath('ximu_matlab_library');	% include x-IMU MATLAB library
addpath('quaternion_library');	% include quatenrion library
close all;                     	% close all figures
clear;                         	% clear all variables
clc;                          	% clear the command terminal

%%Calibrate Magnetometer
s = serialport("COM7",115200);
sampleMData = 300;
f = waitbar(0, "Rotate each axis", 'Name', "Calibrating Magnetometer...");
for c = 1:sampleMData
    waitbar(c/sampleMData,f)
    imudata_calib(c,:) = cast(split(readline(s), ","),"double");
end
delete(f);

mag_calib = [imudata_calib(:, 7) imudata_calib(:, 8) imudata_calib(:, 9)];
    
magx_min = min(mag_calib(:,1));
magx_max = max(mag_calib(:,1));
magy_min = min(mag_calib(:,2));
magy_max = max(mag_calib(:,2));
magz_min = min(mag_calib(:,3));
magz_max = max(mag_calib(:,3));


magx_correction = (magx_max+magx_min)/2;
magy_correction = (magy_max+magy_min)/2;
magz_correction = (magz_max+magz_min)/2;

mag_corrected = [mag_calib(:, 1)-magx_correction mag_calib(:, 2)-magy_correction mag_calib(:, 3)-magz_correction];

%% Import data
msgfig = msgbox("Now Start sampling",'modal');
uiwait(msgfig);

flush(s);
SampleData = 300;

tic
for c = 1:SampleData
    waitbar(c/SampleData,f)
    imudata(c,:) = cast(split(readline(s), ","),"double");
end
timeInt = toc;
delete(f);

sampleFrequency = SampleData / timeInt;
samplePeriod = 1/sampleFrequency;

gyr = [imudata(:, 1) imudata(:, 2) imudata(:, 3)];
acc = [imudata(:, 4) imudata(:, 5) imudata(:, 6)];
mag = [imudata(:, 7)-magx_correction imudata(:, 8)-magy_correction imudata(:, 9)-magz_correction];


%% Process data through AHRS algorithm (calcualte orientation)
% See: http://www.x-io.co.uk/open-source-imu-and-ahrs-algorithms/

R = zeros(3,3,length(gyr));     % rotation matrix describing sensor relative to Earth

ahrs = MadgwickAHRS('SamplePeriod', 1/256, 'Beta', 0.1);
%KP값을 조절하여 자이로값과 자기센서값의 가중치를 선택가능
for i = 1:length(gyr)
    ahrs.Update(gyr(i,:) * (pi/180), acc(i,:), mag(i,:));	% gyroscope units must be radians
    R(:,:,i) = quatern2rotMat(ahrs.Quaternion)';    % transpose because ahrs provides Earth relative to sensor
end
