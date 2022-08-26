# Python을 이용해서 ble로 부터 데이터 얻기
## Bleak 라이브러리
ble 장치 부터 데이터를 얻기 위해 파이썬 라이브러리 bleak를 사용했다.

설치법
```  
pip install bleak
```
주의) Python 버전 3.8이상의 버전을 사용해야 합니다.

버전확인
```
python --version
```

## 주요 사용법
    BleakClient(address)
ble 장치와 연결하여 디바이스에 대한 객체를 반환한다.  
파라미터로는 ble 장치의 MAC주소를 전달한다.  
ble 장치의 MAC주소를 구하는 방법은 다음을 참고하면 된다.
https://bleak.readthedocs.io/en/latest/scanning.html  

    client.read_gatt_char(characteristic_uuid)
특정 charateristic의 uuid를 이용해서 정보를 읽는다.  
읽어온 정보는 bytearray형식으로 반환된다.  

자세한 사항은 다음 공식문서를 참조하시면 됩니다.  
https://bleak.readthedocs.io/en/latest/index.html  
## 비동기 처리
Bleak 라이브러리의 함수는 I/O처리동안에 비동기 동작을 지원한다.
비동기 처리를 위해 asyncio를 사용하여 ble장치로 부터 데이터를 읽는 함수와 읽어온 데이터를 처리하는 함수로 나누어져 있다. 따라서 이 두가지 동작은 비동기적으로 처리되며 이와 같은 동작을 위해서 원형큐를 이용했다.

### 데이터 읽기
```
async def get_raw(client, characteristic_uuid)
```

### 데이터 처리
```
sync def convert_bytes()
```

### main함수
```
async def main(address, characteristic_uuid):
    async with BleakClient(address) as client:
        while True:
            await get_raw(client, characteristic_uuid)
            await convert_bytes()
```
데이터를 지속적으로 받아오기 위해 메인 함수에 무한 루프를 썼다. 그리고 루프문 안에서는 두가지의 동작(코루틴?) 을 지정하여 각각의 동작이 비동기적으로 실행된다.  

### 실행
```
asyncio.run(main(address, imu_characteristic_uuid)
```