import asyncio
from bleak import BleakClient
#frome https://www.programiz.com/dsa/circular-queue
class MyCircularQueue():

    def __init__(self, k):
        self.k = k
        self.queue = [None] * k
        self.head = self.tail = -1

    def is_empty(self):
        if(self.head == -1):
            return True
        return False
    # Insert an element into the circular queue
    def enqueue(self, data):

        if ((self.tail + 1) % self.k == self.head):
            print("The circular queue is full\n")

        elif (self.head == -1):
            self.head = 0
            self.tail = 0
            self.queue[self.tail] = data
        else:
            self.tail = (self.tail + 1) % self.k
            self.queue[self.tail] = data

    # Delete an element from the circular queue
    def dequeue(self):
        if (self.head == -1):
            print("The circular queue is empty\n")

        elif (self.head == self.tail):
            temp = self.queue[self.head]
            self.head = -1
            self.tail = -1
            return temp
        else:
            temp = self.queue[self.head]
            self.head = (self.head + 1) % self.k
            return temp

    def printCQueue(self):
        if(self.head == -1):
            print("No element in the circular queue")

        elif (self.tail >= self.head):
            for i in range(self.head, self.tail + 1):
                print(self.queue[i], end=" ")
            print()
        else:
            for i in range(self.head, self.k):
                print(self.queue[i], end=" ")
            for i in range(0, self.tail + 1):
                print(self.queue[i], end=" ")
            print()
#address of BLE Device
address = "3B:10:77:1B:FB:14"

#address of BLE characteristic
imu_characteristic_uuid = "ce3425fe-1ef3-11ed-861d-0242ac120002"

raw_queue = MyCircularQueue(10)
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
