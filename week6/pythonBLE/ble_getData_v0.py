import asyncio
from bleak import BleakClient
import CircularQueue as cq
#address of BLE Device
address = "3B:10:77:1B:FB:14"

#address of BLE characteristic
imu_characteristic_uuid = "ce3425fe-1ef3-11ed-861d-0242ac120002"

raw_queue = cq.MyCircularQueue(10)
imu_data = list()

async def get_raw(client, characteristic_uuid):
    read_data = await client.read_gatt_char(characteristic_uuid)
    raw_queue.enqueue(read_data)

async def convert_bytes():
    if(not(raw_queue.is_empty())):
        raw_data = raw_queue.dequeue()
        converted = [float(i) for i in raw_data.decode().split(", ")]
        print(converted)
        imu_data.append(converted)

async def main(address, characteristic_uuid):
    async with BleakClient(address) as client:
        while True:
            await get_raw(client, characteristic_uuid)
            await convert_bytes()

asyncio.run(main(address, imu_characteristic_uuid))
