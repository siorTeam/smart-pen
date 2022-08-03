# evalkit_app
경로를 추적하는데에 사용되는 ahrs함수, high-pass filter에 사용되는 파라미터를 조절하며 테스트 할 수있도록 만들어졌다. 현재 조절 가능한 파라미터는 DOF, ahrs 함수의 Kp, Ki 그리고 high-pass filter의 cutoff frequency가 있다.  

# 동작 방법
evalkit_app.mlapp 코드를 matlab에서 실행 시킨다.

<img src ="https://user-images.githubusercontent.com/38479511/182533954-8793f005-1a00-4ba3-98de-41e3ab5957b5.png" width ="500" height="640"/>

1. 시리얼 연결  
앱을 열었다면 가장먼저 아두이노와 연결을 해야 한다. 아두이노가 연결된 포트를 확인하여 port 란에 입력 후 Connect 버튼을 누른다. 현재까지는 연결이 정상적으로 되었는지 확인 하는 에러가 나지 않는다면 정상 연결이 되었다고 볼수 있다. 또한 시리얼이 연결된 후에 connnet를 다시 한번 더 누르면 에러가 나서 앱이 종료 되므로 port를 변경하고 싶다면 앱을 재실행 해야 한다.

2. Magnetometer Calibration  
지자기 센서의 캘리브레이션을 하는 코드이다. 앱 실행후 최초 한번 실행하여 보정값을 얻어준다. 캘리브레이션 중에서는 imu센서를 모든 축 방향으로 회전시킨다.  

3. Data 얻기
Sampledata 입력 칸에 imu로 부터 얻기 원하는 값의 수를 정하여 입력한다. 그리고 new data버튼을 누르면 imu로 부터 데이터를 얻어온다. 얻은 데이터는 다시 new data를 클릭하거나 앱을 재실행하지 않는다면 유지된다.

4. 경로 추적 해보기  
parameter칸에 있는 Kp, Ki, 그리고 cutoff frequency를 조정할 수있다.

    + Kp, Ki  
    Kp는 경로를 구성할때 자이로센서의 값과 그외의 센서들 사이의 비중을 조절한다. Kp가 클수록 자이로 센서의 값을 더 신뢰하고 Kp가 작아지면 가속도 센서와 지자기 센서의 값을 더 신뢰한다.  
    + cutoff frequency  
    경로를 구성할때 imu의 drift를 제거 하기 위해 high-pass 필터가 linear velocity값에 한번, position값에 한번 쓰인다. 각각에서 사용되는 cutoff frequency를 조절한다.

    또한 DOF를 선택하여 경로 구성에서 지자기 센서를 포함 할지 말지를 정한다.  
    파라미터 결정이 끝났다면 RUN 버튼을 누른다. 그러면 상단 창에 그래프를 볼 수있을 것이며 새창으로 경로 구성 애니메이션이 나올 것이다.  
    그래프를 그린 후에도 파라미터 값을 조정하여 RUN을 눌러 다시 재구성하는 것이 가능하다.

    ![앱 실행화면](https://user-images.githubusercontent.com/38479511/182533959-1a26c8ec-b1da-4f42-bb86-2f27910e84be.png)