clear
s = serialport("COM7",115200);
imudata = zeros([100 9]);


for c = 1:100
    imudata(c,:) = cast(split(readline(s), ","),"double");
end

