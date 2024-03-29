import ubluetooth
import pyb
import time
import mainInit as main


# volé sans aucune form de honte depuis ici :
# https://techtotinker.blogspot.com/2021/08/025-esp32-micropython-esp32-bluetooth.html

ble_msg = ''
connected = False

class STM32_BLE():
    def __init__(self, name):
        self.led = pyb.LED(3)
        
        self.name = name
        self.ble = ubluetooth.BLE()
        self.ble.active(True)
        self.disconnected()
        self.ble.irq(self.ble_irq)
        self.register()
        self.advertiser()

    def connected(self):
        global connected
        connected = True
        self.led.on()

    def disconnected(self):
        global connected
        connected = False     
        self.led.off()

    def ble_irq(self, event, data):
        global ble_msg
        
        if event == 1: #_IRQ_CENTRAL_CONNECT:
                       # A central has connected to this peripheral
            self.connected()

        elif event == 2: #_IRQ_CENTRAL_DISCONNECT:
                         # A central has disconnected from this peripheral.
            self.advertiser()
            self.disconnected()
        
        elif event == 3: #_IRQ_GATTS_WRITE:
                         # A client has written to this characteristic or descriptor.          
            buffer = self.ble.gatts_read(self.rx)
            ble_msg = buffer.decode('UTF-8').strip()
            
    def register(self):        
        # Nordic UART Service (NUS)
        NUS_UUID = '6E400001-B5A3-F393-E0A9-E50E24DCCA9E'
        RX_UUID = '6E400002-B5A3-F393-E0A9-E50E24DCCA9E'
        TX_UUID = '6E400003-B5A3-F393-E0A9-E50E24DCCA9E'
            
        BLE_NUS = ubluetooth.UUID(NUS_UUID)
        BLE_RX = (ubluetooth.UUID(RX_UUID), ubluetooth.FLAG_WRITE)
        BLE_TX = (ubluetooth.UUID(TX_UUID), ubluetooth.FLAG_NOTIFY)
            
        BLE_UART = (BLE_NUS, (BLE_TX, BLE_RX,))
        SERVICES = (BLE_UART, )
        ((self.tx, self.rx,), ) = self.ble.gatts_register_services(SERVICES)

    def send(self, data):
        self.ble.gatts_notify(0, self.tx, data + '\n') # le \n était déjà là, est-il nécessaire ?

    def advertiser(self):
        name = bytes(self.name, 'UTF-8')
        adv_data = bytearray('\x02\x01\x02') + bytearray((len(name) + 1, 0x09)) + name
        self.ble.gap_advertise(100, adv_data)
        #print(adv_data)
        #print("\r\n")
                # adv_data
                # raw: 0x02010209094553503332424C45
                # b'\x02\x01\x02\t\tESP32BLE'
                #
                # 0x02 - General discoverable mode
                # 0x01 - AD Type = 0x01
                # 0x02 - value = 0x02
                
                # https://jimmywongiot.com/2019/08/13/advertising-payload-format-on-ble/
                # https://docs.silabs.com/bluetooth/latest/general/adv-and-scanning/bluetooth-adv-data-basics


ble = STM32_BLE("STM32BLE")

def BLEloop():
    global ble_msg
    global connected

    main.oled.fill(0)
    main.oled.text('BLE testing', 0, 5)
    main.oled.text('Name is :', 0, 15)
    main.oled.text(ble.name, 0, 25)
    main.oled.show()

    if not connected:
        return

    if ble_msg == '':
        print('sending test')
        ble_msg = ''
        ble.send('test')
    elif ble_msg == 'test':
        print(ble_msg)
        ble_msg = ''
        ble.send('received_msg')
    elif ble_msg == 'received_msg':
        print('received msg confirmation of reception')
        ble_msg = ''
    else:
        print(ble_msg)
        ble_msg = ''
    
    time.sleep(0.1)