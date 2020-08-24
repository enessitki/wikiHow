# UKB params
import os
import time


dirname = os.path.abspath(__file__)
hardDrive = ""
storageTag = "MYST"

for item in dirname.split("/")[0:-2]:
    hardDrive += item + '/'

platform = "raspi"
print(platform)
ikaIp = '192.168.2.2'
# ukbIp = '192.168.2.3'
ukbIp = '0.0.0.0'
kgmIp = "192.168.1.108"
cabledIKAIp = "192.168.10.2"
cabledUKBIp = "192.168.10.3"
videoStreamPort = 5400
audioStreamPort = 5800
txPort = 5001
rxPort = 5002
peripheralPort = "/dev/ttyS1"
peripheralPortRate = 115200

dirDb = hardDrive + 'db/db.xml'
dirResources = hardDrive + 'resources/'
joystickSerialNumber = "00000000001A"
print(dirResources)

save_dir = time.strftime('%Y-%m-%d-%H-%M-%S') + '-' + str(time.time()).split('.')[1]
# dirStorage = SysParams.dirStorage + save_dir
dirStorage = hardDrive + "storage/" + save_dir
# os.mkdir(dirStorage)
dirStorage += "/"

print(dirStorage)
