# ble-serial을 이용해서 가상포트로 ble연결하기  
https://pypi.org/project/ble-serial/  
위의 파이썬 패키지를 이용해서 ble연결을 가상 시리얼 포트를 통해 할 수 있다.  

## 아두이노 코드 변경  
ble 통신을 시리얼포트로 하기 위해서 Tx, Rx 역할을 하는 Charateristic을 각각 만들어야 한다. 따라서 기존에 존재했던  IMUCharateristic은 IMU_Tx_Charateristic로 이름을 바꾸었고 Rx역할을 하는 IMU_Rx_Charateristic을 추가 했다.  
```
BLECharacteristic IMU_Tx_Charateristic(IMUServiceTxCharacteristicUUID, BLERead | BLENotify, BLE_BUFFER_SIZE);
BLECharacteristic IMU_Rx_Charateristic(IMUServiceRxCharacteristicUUID, BLEWriteWithoutResponse | BLEWrite, BLE_BUFFER_SIZE, RX_BUFFER_FIXED_LENGTH);
```
Service와 Charateristic의 UUID도 변경 되었으니 확인 바란다.
```
const char* IMUServiceUUID = "7078692c-2793-11ed-a261-0242ac120002";

const char* IMUServiceTxCharacteristicUUID = "70786bca-2793-11ed-a261-0242ac120002";
const char* IMUServiceRxCharacteristicUUID = "70786cec-2793-11ed-a261-0242ac120002";
```
이외의 코드와 동작방식은 기존과 동일하다.

## ble-serial 로 포트 생성하기
https://pypi.org/project/ble-serial/   
위의 링크에서 내용을 가져왔다. 자세한 내용은 위 사이트를 참조하면 좋을것 같다.

### 1. ble-serial 패키지 설치
```
> pip install ble-serial
```
### 2. com0com 드라이버 설치  
Windows에서는 가상 시리얼 포트 연결을 위해서 별도의 드라이버를 설치 해야 한다.
https://sourceforge.net/projects/signed-drivers/files/com0com/v3.0/
위의 사이트에서 Setup_com0com_v3.0.0.0_W7_x64_signed.exe 혹은 Setup_com0com_v3.0.0.0_W7_x86_signed.exe을 다운로드해서 설치한다.  
설치후 장치관리자에서 com0com 장치를 확인 할수 있다면 정상적으로 설치 된것이다.  

### 3. ble 포트 설치  
ble-serial 패키지에는 포트연결, 초기화등을 위한 스크립트가 제공된다.  
먼저 커맨드창(cmd, powershell 등등)에서 다음 스크립트를 실행 시킨다.

```
> ble-com-setup.exe
```
정상적으로 실행 된다면 새로운 python창이 떠서 C:/Program Files (x86)/com0com/ 에 설치된 드라이버를 찾아서 ble를 위한 가상 포트를 생성한다.  

포트생성이 정상적으로 되었다면 COM9포트로 ble 장치를 연결 할 수있다.

## BLE장치 연결 하기  

ble-serial 패키지에서 제공하는 스크립트를 이용한다. 명령어는 커맨드창(cmd, powershell 등등)에서 실행한다.  
### 스캔
```
> ble-scan -h
```
스캔 결과로 주변에 있는 ble장치들의 MAC주소와 이름이 나타난다.

### 주소를 이용한 스캔  
```
> ble-scan -d [MAC_ADDRESS]
(예시) > ble-scan -d 3B:10:77:1B:FB:14
```
해당 주소의 디바이스에 존재하는 Service와 Charateristic 정보를 제공한다.  

### 장치 연결 (MAC주소 이용)  
 ```
> ble-serial -d [MAC_ADDRESS] -r [READ_UUID] -w [WRITE_UUID]
(예시) > ble-serial -d 3B:10:77:1B:FB:14 -w 70786cec-2793-11ed-a261-0242ac120002 -r 70786bca-2793-11ed-a261-0242ac120002
 ```
BLE장치의 MAC주소를 이용해서 연결한다.  
MAC주소는 nano 33 ble 보드에 따라 달라질수 있으니 직접 확인해야 한다.  

READ_UUID : Tx 역할을 하는 Charateristic의 UUID  
-> 70786bca-2793-11ed-a261-0242ac120002  

WRITE_UUID : Rx 역할을 하는 Charateristic의 UUID  
-> 70786cec-2793-11ed-a261-0242ac120002   

### 장치연결 (Serive의 UUID 이용)  
```
ble-serial -s 7078692c-2793-11ed-a261-0242ac120002 -w 70786cec-2793-11ed-a261-0242ac120002 -r 70786bca-2793-11ed-a261-0242ac120002
```
MAC주소 대신에 Serive의 UUID를 이용한다. 따라서 이 방법이 좀 더 일반적으로 사용 하기 편할 것 같다.  

연결이 완료 되면 | INFO | main.py: Running main loop! 라는 문구가 뜬다. 그러면 putty나 아두이노 시리얼 모니터와 같은 시리얼 모니터 도구를 이용해서 ble장치로 부터 읽은 값을 확인 할수있다.   

포트는 COM9, 보드레이트는 9600으로 설정 해야 한다.  


## MATLAB 앱 코드 수정  
ble-serial 명령을 수행후 PC에 ble포트(COM9) 가 생성 되었다면 기존에 만들었던 MATLAB앱을 사용할 수있다. 이때 시리얼 포트를 COM9로 그리고 보드레이트를 9600으로 변경하였다.  
