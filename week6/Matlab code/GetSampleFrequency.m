close all;                     	% close all figures
clear;                         	% clear all variables
clc;                          	% clear the command terminal

s = serialport("COM9",9600);

msgfig = msgbox("Now Start sampling",'modal');
uiwait(msgfig);

flush(s);
SampleData = 300;
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