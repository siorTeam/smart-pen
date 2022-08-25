import asyncio
from bleak import BleakClient

#address of BLE Device
address = "3B:10:77:1B:FB:14"

#address of BLE characteristic
imu_characteristic_uuid = "ce3425fe-1ef3-11ed-861d-0242ac120002"

async def run(address):
    async with BleakClient(address) as client:
        print('connected')
        read_data = await client.read_gatt_char(imu_characteristic_uuid)
        print('read_data: ',read_data)

        read_data = await client.read_gatt_char(imu_characteristic_uuid)
        print('read_data: ',read_data)

        read_data = await client.read_gatt_char(imu_characteristic_uuid)
        print('read_data: ',read_data)

        read_data = await client.read_gatt_char(imu_characteristic_uuid)
        print('read_data: ',read_data)

        read_data = await client.read_gatt_char(imu_characteristic_uuid)
        print('read_data: ',read_data)
    print('disconnect')

loop = asyncio.get_event_loop()
loop.run_until_complete(run("SmartPen"))
print('done')
