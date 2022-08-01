clear
s = serialport("COM7",115200);
imudata = zeros([300 9]);

f = waitbar(0, "Rotate each axis", 'Name', "Calibrating Magnetometer...");
for c = 1:300
    waitbar(c/300,f)
    imudata(c,:) = cast(split(readline(s), ","),"double");
end
delete(f);
mag = [imudata(:, 7) imudata(:, 8) imudata(:, 9)];

figure("Name", "Magnetometor Calibration");
plot3(mag(:, 1), mag(:, 2), mag(:,3), "rs")
hold on

magx_min = min(mag(:,1));
magx_max = max(mag(:,1));
magy_min = min(mag(:,2));
magy_max = max(mag(:,2));
magz_min = min(mag(:,3));
magz_max = max(mag(:,3));


magx_correction = (magx_max+magx_min)/2;
magy_correction = (magy_max+magy_min)/2;
magz_correction = (magz_max+magz_min)/2;

mag_corrected = [mag(:, 1)-magx_correction mag(:, 2)-magy_correction mag(:, 3)-magz_correction];

plot3(mag_corrected(:,1), mag_corrected(:,2), mag_corrected(:,3), "bs");

hold off
