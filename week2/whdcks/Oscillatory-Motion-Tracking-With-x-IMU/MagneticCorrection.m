clear
s = serialport("COM12",115200);
flush(s);
readline(s);
f = waitbar(0, "Rotate each axis", 'Name', "Calibrating Magnetometer...");
tic;
stopTimer = 10;
magReadings=[];

while(toc<stopTimer)
    imudata = cast(split(readline(s), ", "),"double");
    mag = [imudata(7) imudata(8) imudata(9)];
    magReadings = [magReadings;mag];
    waitbar(toc/stopTimer,f)
end
delete(f);

figure("Name", "Magnetometor Calibration");
plot3(magReadings(:, 1), magReadings(:, 2), magReadings(:,3), "rs")
hold on

magx_min = min(magReadings(:,1));
magx_max = max(magReadings(:,1));
magy_min = min(magReadings(:,2));
magy_max = max(magReadings(:,2));
magz_min = min(magReadings(:,3));
magz_max = max(magReadings(:,3));


magx_correction = (magx_max+magx_min)/2;
magy_correction = (magy_max+magy_min)/2;
magz_correction = (magz_max+magz_min)/2;

mag_corrected = [magReadings(:, 1)-magx_correction magReadings(:, 2)-magy_correction magReadings(:, 3)-magz_correction];

plot3(mag_corrected(:,1), mag_corrected(:,2), mag_corrected(:,3), "bs");

hold off
