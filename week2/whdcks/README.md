# Reference

1. https://kr.mathworks.com/help/fusion/ug/Estimating-Orientation-Using-Inertial-Sensor-Fusion-and-MPU-9250.html
2. [Github, jrowberg, i2cdevlib, i2c-mpu library](https://github.com/jrowberg/i2cdevlib)
3. [Github, 0015, Python-Data-Sampling-App, Accessed:220721](https://github.com/0015/Python-Data-Sampling-App/tree/cb1424a9ab597acccf6ab043f2576afb36161c0d)
4. [Github, xioTechnologies, Oscillatory-Motion-Tracking-With-x-IMU, Accessed:220721](https://github.com/xioTechnologies/Oscillatory-Motion-Tracking-With-x-IMU/tree/314208abbb592c9623ad0940138ea597447774a9)

# 폴더별 설명

1. 아두이노 코드  
IMU가 연결된 아두이노 단에 업로드 되는 코드들이다.  
아두이노에서는 Serial.print를 이용해서 자이로, 가속도, 지자기 센서의 값을 출력한다.    
출력 형식  

```
"자이로x, 자이로y, 자이로x, 가속도x, 가속도y, 가속도z, 지자기x, 지자기y, 지자기z"
```

mpu9250_transmitter 코드에는 초기 실행 후 지자기 센서의 캘리브레이션이 진행된다. 하지만 지자기 센서의 캘리브레이션은 matlab코드에서 진행하므로 캘리브레이션 과정을 생략한 mpu9250_transmitter_noCalib을 이용한다.  

+ reference  
    Github, 0015, Python-Data-Sampling-App, Accessed:220721


2. Python-Data-Sampling-App  
Github, 0015, Python-Data-Sampling-App, Accessed:220721  
다음 레포지토리에서 가져온 코드로 아두이노에서 시리얼 출력한 값은 읽어서 csv파일로 저장하는데 이용된다.  
저장된 csv파일은 matlab코드에서 사용될 수있다.  


3. Oscillatory-Motion-Tracking-With-x-IMU  
Github, xioTechnologies, Oscillatory-Motion-Tracking-With-x-IMU, Accessed:220721  
해당 코드를 인용했다.  
imu에서 읽을 값을 바탕으로 경로를 구성하는 matlab코드이다.
