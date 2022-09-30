# 준비사항    

# 1. 파이썬 라이브러리 설치  


```
pip install -r requirements.txt
```  

# 2. ble-serial을 이용해서 가상포트로 ble 연결하기  
https://pypi.org/project/ble-serial/  
위의 파이썬 패키지를 이용해서 ble연결을 가상 시리얼 포트를 통해 할 수 있다.  

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
설치후 장치관리자에서 com0com 장치를 확인 할수 있다면 정상적으로 설치 된것이다. com0com의 정상 작동을 위해서 안전부팅을 해제해야 할 수도있다.  

### 3. ble 포트 설치  
ble-serial 패키지에는 포트연결, 초기화등을 위한 스크립트가 제공된다.  
먼저 커맨드창(cmd, powershell 등등)에서 다음 스크립트를 실행 시킨다.

```
> ble-com-setup.exe
```
정상적으로 실행 된다면 새로운 python창이 떠서 C:/Program Files (x86)/com0com/ 에 설치된 드라이버를 찾아서 ble를 위한 가상 포트를 생성한다.  

포트생성이 정상적으로 되었다면 COM9포트로 ble 장치를 연결 할 수있다.

# 실행  
```
python main.py
```  

