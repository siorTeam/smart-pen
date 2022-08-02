%% Housekeeping
 
addpath('ximu_matlab_library');	% include x-IMU MATLAB library
addpath('quaternion_library');	% include quatenrion library
close all;                     	% close all figures
clear;                         	% clear all variables
clc;                          	% clear the command terminal

%%Calibrate Magnetometer
s = serialport("COM7",115200);
sampleMData = 30;
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
SampleData = 30;
imudata = zeros([SampleData 9]);

f = waitbar(0, "Move imu", 'Name', "Read data from imu");
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

ahrs = MahonyAHRS('SamplePeriod', samplePeriod, 'Kp', 1);
%KP값을 조절하여 자이로값과 자기센서값의 가중치를 선택가능
for i = 1:length(gyr)
    %ahrs.UpdateIMU(gyr(i,:) * (pi/180), acc(i,:));	% 자기센서 X
    ahrs.Update(gyr(i,:) * (pi/180), acc(i,:), mag(i, :)); % 자기센서 O
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


%% Play animation
SamplePlotFreq = 1;

SixDOFanimation(linPosHP, R, ...
                'SamplePlotFreq', SamplePlotFreq, 'Trail', 'DotsOnly', ...
                'Position', [9 39 1280 720], ...
                'AxisLength', 0.1, 'ShowArrowHead', false, ...
                'Xlabel', 'X (m)', 'Ylabel', 'Y (m)', 'Zlabel', 'Z (m)', 'ShowLegend', false, 'Title', 'Unfiltered',...
                'CreateAVI', false, 'AVIfileNameEnum', false, 'AVIfps', ((1/samplePeriod) / SamplePlotFreq));            
 
%% End of script