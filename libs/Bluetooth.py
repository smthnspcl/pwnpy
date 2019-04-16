from os import geteuid

from bluepy.btle import Scanner as btleScanner
from bluetooth import discover_devices

from libs import Scanner


class BluetoothDevice(object):
    address = None
    name = None

    def __init__(self, address, name):
        self.address = address
        self.name = name

    @staticmethod
    def dummy():
        return BluetoothDevice("FF:FF:FF:FF:FF:FF", "")


class BluetoothLEDevice(BluetoothDevice):
    rssi = None
    connectable = None
    advertisements = []

    def __init__(self, address, name, rssi, connectable):
        BluetoothDevice.__init__(self, address, name)
        self.rssi = rssi
        self.connectable = connectable


class Bluetooth(Scanner):
    name = "bluetooth"

    def _on_run(self):
        self.do_run = geteuid() == 0  # dont need to try if we dont have rights

    def scan_classic(self):
        devs = discover_devices(duration=self.cfg["classicScanTime"], lookup_names=True)
        for addr, name in devs:
            self.db.bluetooth_classic_device_insert(BluetoothDevice(addr, name))  # todo read more

    def scan_btle(self):
        devs = btleScanner().scan(self.cfg["leScanTime"])
        for dev in devs:
            d = BluetoothLEDevice(dev.addr, "", dev.rssi, dev.connectable)  # todo read more
            for adtype, desc, val in dev.getScanData():
                d.advertisements.append({
                    "type": adtype,
                    "desc": desc,
                    "value": val
                })
            self.db.bluetooth_le_device_insert(d)

    def _work(self):
        if self.cfg["onlyClassic"] or not self.cfg["onlyLE"]:
            self.scan_classic()
        if self.cfg["onlyLE"] or not self.cfg["onlyClassic"]:
            self.scan_btle()
