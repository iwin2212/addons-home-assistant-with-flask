import broadlink
import base64
import broadlink
import time


def custom_check_data(device):
    packet = bytearray(device._request_header)
    packet.append(0x04)
    response = device.send_packet(0x6a, packet)
    try:
        broadlink.check_error(response[0x22:0x24])
        payload = device.decrypt(bytes(response[0x38:]))
        return payload[len(device._request_header) + 4:]
    except Exception as error:
        print(error)


iden = '24:DF:A7:F1:04:EA(host:192.168.1.43)'
mac = iden.split("(host:")[0]
ip = iden.split("(host:")[1][:-1]
device = broadlink.rm4((ip, 80), mac, None)
device.auth()
device.sweep_frequency()
print("sweeping...; LED should be RED")

i = 0
while True:
    f = device.check_frequency()
    if not (f == 0):
        break
    i = i + 1
    time.sleep(1)
    print("check frequency... ", i)

if f == 1:
    print("frequency found! check LED, should be off")
else:
    device.cancel_learning()
    print("frequency not found... ")
    exit()
time.sleep(1)

print("learning command")

device.find_rf_packet()

i = 0
while True:
    data = custom_check_data(device)
    if data:
        break
    elif i > 10:
        device.cancel_learning()
        print("command not learned")
        exit()
    i = i + 1
    time.sleep(1)
    print("check command... ", i)

print("command learned")

encodedData = ''.join(format(x, '02x') for x in bytearray(data))
print(encodedData)
