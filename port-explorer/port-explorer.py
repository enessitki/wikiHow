import serial
import serial.tools.list_ports


tty_list = list(serial.tools.list_ports.comports())


for tty in tty_list:
    print("-----------------------------------")
    print("name: ", tty.name)
    print("device: ", tty.device)
    print("hwid: ", tty.hwid)
    print("description: ", tty.description)
    print("interface: ", tty.interface)
    print("location: ", tty.location)
    print("check 1: ", tty.location == "3-3.1.3:1.0")
    print("check 2: ", tty.location == "3-3.4.3:1.0")
    print("manufacturer: ", tty.manufacturer)
    print("pid: ", tty.pid)
    print("vid: ", tty.vid)
    print("product: ", tty.product)
    print("serial_number: ", tty.serial_number)
    print("-----------------------------------")
