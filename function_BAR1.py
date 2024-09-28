# นำเข้าโมดูลที่จำเป็น
import datetime
import time
import RPi.GPIO as GPIO
import threading
import usb.core
import usb.util

# คลาสสำหรับการทำงานของ Barcode1
class Function_BAR1:
    def __init__(self):
        # ตั้งค่าโหมด GPIO
        GPIO.setmode(GPIO.BCM)
        self.IR_PIN_2 = 15  # กำหนดพินสำหรับเซ็นเซอร์ IR
        GPIO.setup(self.IR_PIN_2, GPIO.IN)
        self.input_sensor = True  # ตัวแปรเก็บสถานะเซ็นเซอร์
        self.running = True  # ตัวแปรสำหรับการทำงานของ Thread
        self.condition = True  # ตัวแปรเงื่อนไขสำหรับการทำงาน
        self.is_loaded = False  # ตัวแปรเก็บสถานะการโหลด
        self.tag_id = []  # ตัวแปรสำหรับเก็บข้อมูล tag_id
        self.timer_running = False  # ตัวแปรสำหรับการทำงานของ Timer
        self.start_time = None  # ตัวแปรสำหรับเก็บเวลาเริ่มต้น
        self.vendor_id = 0x0c2e  # กำหนด Vendor ID ของอุปกรณ์
        self.product_id = 0x1001  # กำหนด Product ID ของอุปกรณ์
        self.serial_number = "21148B0941"  # กำหนด Serial Number ของอุปกรณ์
        self.device_connected = False  # ตัวแปรเก็บสถานะการเชื่อมต่ออุปกรณ์
        self.dev = self.find_device(self.vendor_id, self.product_id, self.serial_number)  # ค้นหาอุปกรณ์ตาม Vendor ID, Product ID และ Serial Number

        # ประวัติการโหลดและปลด
        self.history_load = []
        self.history_unload = []

        # เก็บข้อมูลการโหลดและปลด
        self.barcode1_data = {
            'loaded_tag_id': '',
            'loaded_timestamp': ['', ''],
            'unloaded_tag_id': '',
            'unloaded_timestamp': ['', '']
        }

        # เริ่มต้น Thread การทำงาน
        self.start_thread()

    # ฟังก์ชันสำหรับค้นหาอุปกรณ์
    def find_device(self, vendor_id, product_id, serial_number):
        devices = usb.core.find(find_all=True, idVendor=vendor_id, idProduct=product_id)
        for dev in devices:
            if usb.util.get_string(dev, dev.iSerialNumber) == serial_number:
                self.device_connected = True
                print("พบอุปกรณ์ Barcode1")
                return dev
        self.device_connected = False
        print("ไม่พบอุปกรณ์")
        return None

    # ฟังก์ชันสำหรับเริ่มต้น Thread
    def start_thread(self):
        self.thread = threading.Thread(target=self.sensor)
        self.thread.start()

    # ฟังก์ชันสำหรับการตรวจสอบเซ็นเซอร์
    def sensor(self):
        while self.running:
            self.input_sensor = GPIO.input(self.IR_PIN_2)  # อ่านค่าจากเซ็นเซอร์
            time.sleep(0.5)  # หน่วงเวลา 0.5 วินาที
            if self.input_sensor == 0 and not self.is_loaded:
                print('LOAD')
                self.load()  # ถ้าเซ็นเซอร์ตรวจจับได้และยังไม่โหลด ให้ทำการโหลด
            if self.input_sensor == 1 and self.is_loaded:
                print('UNLOAD')
                self.unload()  # ถ้าเซ็นเซอร์ไม่ตรวจจับและมีการโหลดแล้ว ให้ทำการปลด
            self.find_device(self.vendor_id, self.product_id, self.serial_number)  # ค้นหาอุปกรณ์ใหม่ทุกครั้ง

    # ฟังก์ชันสำหรับสร้างข้อมูลจากอุปกรณ์
    def generate(self):
        self.detach_and_claim_interfaces()  # ทำการเชื่อมต่อกับอินเทอร์เฟซ
        while True:
            data = self.read_rfid_data()  # อ่านข้อมูลจาก RFID
            if data:
                kbw_data = self.format_to_kbw(data)  # แปลงข้อมูลให้อยู่ในรูปแบบที่เข้าใจได้
                if kbw_data:
                    self.tag_id.extend(kbw_data)  # เพิ่มข้อมูล tag_id ลงในรายการ
                    time.sleep(0.01)  # หน่วงเวลา 0.01 วินาที
                    if not self.timer_running:
                        self.start_time = time.time()  # เก็บเวลาปัจจุบัน
                        self.timer_running = True  # เริ่มต้น Timer
                        break
            else:
                return

    # ฟังก์ชันสำหรับการโหลด
    def load(self):
        if not self.is_loaded:
            self.generate()  # เรียกใช้ฟังก์ชันสร้างข้อมูล
            if self.timer_running and (time.time() - self.start_time >= 0.1):
                if len(self.tag_id) > 5:  # ตรวจสอบว่ามีข้อมูล tag_id ไหม
                    timestamp_date, timestamp_time = self.timestamp()  # ดึงเวลาปัจจุบัน
                    self.barcode1_data['loaded_tag_id'] = ''.join(self.tag_id)  # บันทึกข้อมูล tag_id
                    self.barcode1_data['loaded_timestamp'] = (timestamp_date, timestamp_time)  # บันทึกเวลาที่โหลด
                    print(f"Loaded Tag ID: {self.barcode1_data['loaded_tag_id']}, Date: {timestamp_date}, Time: {timestamp_time}")
                    self.update_load_history(self.barcode1_data['loaded_tag_id'], timestamp_date, timestamp_time)  # อัปเดตประวัติการโหลด
                    self.timer_running = False  # หยุด Timer
                    self.is_loaded = True  # ตั้งค่าสถานะว่าโหลดแล้ว
                else:
                    self.barcode1_data['unloaded_tag_id'] = ''
                    self.barcode1_data['unloaded_timestamp'] = ('', '')  # ถ้าไม่มีข้อมูล ให้ล้างข้อมูล
                    self.tag_id.clear()

    # ฟังก์ชันสำหรับการปลด
    def unload(self):
        if self.is_loaded:
            timestamp_date, timestamp_time = self.timestamp()  # ดึงเวลาปัจจุบัน
            self.barcode1_data['unloaded_tag_id'] = ''.join(self.tag_id)  # บันทึกข้อมูล tag_id ที่ปลด
            self.barcode1_data['unloaded_timestamp'] = (timestamp_date, timestamp_time)  # บันทึกเวลาที่ปลด
            print(f"Unloaded Tag ID: {self.barcode1_data['unloaded_tag_id']}, Date: {timestamp_date}, Time: {timestamp_time}")
            self.update_unload_history(self.barcode1_data['unloaded_tag_id'], timestamp_date, timestamp_time)  # อัปเดตประวัติการปลด
            self.is_loaded = False  # ตั้งค่าสถานะว่ายังไม่ได้โหลด
            if self.condition:
                self.barcode1_data['loaded_tag_id'] = ''
                self.barcode1_data['loaded_timestamp'] = ('', '')  # ล้างข้อมูลที่โหลด
                self.tag_id.clear()

    # ฟังก์ชันสำหรับการดึงเวลาปัจจุบัน
    def timestamp(self):
        current_time = datetime.datetime.now()  # เวลาปัจจุบัน
        formatted_time = current_time.strftime("%H:%M:%S")  # จัดรูปแบบเวลา
        formatted_date = current_time.strftime("%d-%m-%Y")  # จัดรูปแบบวันที่
        return formatted_date, formatted_time

    # ฟังก์ชันสำหรับจัดการอินเทอร์เฟซ USB
    def detach_and_claim_interfaces(self):
        retries = 0  # จำนวนครั้งที่พยายาม
        delay = 0   # ความล่าช้าระหว่างการพยายาม
        for attempt in range(retries):
            try:
                self.dev.set_configuration()  # ตั้งค่าการเชื่อมต่ออุปกรณ์
                for cfg in self.dev:
                    for intf in cfg:
                        if self.dev.is_kernel_driver_active(intf.bInterfaceNumber):
                            try:
                                self.dev.detach_kernel_driver(intf.bInterfaceNumber)  # ถอด Kernel Driver
                                print(f"Kernel driver detached from interface {intf.bInterfaceNumber}.")
                            except usb.core.USBError as e:
                                if e.errno == 16:
                                    print(f"Attempt {attempt + 1}: Resource busy while detaching kernel driver for interface {intf.bInterfaceNumber}. Retrying after {delay} seconds...")
                                    time.sleep(delay)
                                    continue
                                raise ValueError(f"ไม่สามารถถอด Kernel driver: {str(e)}")

                        try:
                            usb.util.claim_interface(self.dev, intf.bInterfaceNumber)  # เชื่อมต่อกับอินเทอร์เฟซ
                            print(f"Interface {intf.bInterfaceNumber} claimed.")
                        except usb.core.USBError as e:
                            if e.errno == 16:
                                print(f"Attempt {attempt + 1}: Resource busy while claiming interface {intf.bInterfaceNumber}. Retrying after {delay} seconds...")
                                time.sleep(delay)
                                continue
                            raise ValueError(f"ไม่สามารถเชื่อมต่อกับอินเทอร์เฟซ: {str(e)}")
                return True
            except usb.core.USBError as e:
                if e.errno == 16:
                    print(f"Attempt {attempt + 1}: Resource busy while setting configuration. Retrying after {delay} seconds...")
                    time.sleep(delay)
                    continue
                raise ValueError(f"เกิดข้อผิดพลาดในการจัดการอินเทอร์เฟซ: {str(e)}")
            except Exception as e:
                print(f"ข้อผิดพลาดที่ไม่คาดคิด: {str(e)}")
                return False

        return False

    # ฟังก์ชันสำหรับอ่านข้อมูลจาก RFID
    def read_rfid_data(self):
        if self.dev is None:
            print("ไม่สามารถอ่านข้อมูล RFID: ไม่พบอุปกรณ์")
            return None

        try:
            cfg = self.dev.get_active_configuration()  # ดึงการตั้งค่าปัจจุบัน
            intf = cfg[(0, 0)]

            ep = usb.util.find_descriptor(
                intf,
                custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )

            if ep is None:
                print("ไม่พบ Endpoint")
                return None

            data = ep.read(16)  # อ่านข้อมูล 16 ไบต์จาก Endpoint
            return data

        except usb.core.USBError as e:
            return None

    # ฟังก์ชันสำหรับแปลงข้อมูลให้อยู่ในรูปแบบที่เข้าใจได้
    def format_to_kbw(self, data):
        kbw_map = {
            # ตัวอย่างการแมปข้อมูล ปรับให้เหมาะสมกับอุปกรณ์
            0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e',
            0x09: 'f', 0x0A: 'g', 0x0B: 'h', 0x0C: 'i', 0x0D: 'j',
            0x0E: 'k', 0x0F: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o',
            0x13: 'p', 0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
            0x18: 'u', 0x19: 'v', 0x1A: 'w', 0x1B: 'x', 0x1C: 'y',
            0x1D: 'z', 0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4',
            0x22: '5', 0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9',
            0x27: '0', 0x29: '\x1b', 0x2A: '\b', 0x2B: '\t',
            0x2C: ' ', 0x2D: '-', 0x2E: '=', 0x2F: '[', 0x30: ']',
            0x31: '\\', 0x32: '#', 0x33: ';', 0x34: '\'', 0x35: '',
            0x36: ',', 0x37: '.', 0x38: '/'
        }
        kbw_data = ''.join(kbw_map.get(byte, '') for byte in data if byte in kbw_map)  # แปลงข้อมูลแต่ละไบต์
        return kbw_data

    # ฟังก์ชันสำหรับอัปเดตประวัติการโหลด
    def update_load_history(self, tag_id, timestamp_date, timestamp_time):
        print(f"อัปเดตประวัติการโหลดด้วย tag_id: {tag_id}, วันที่: {timestamp_date}, เวลา: {timestamp_time}")
        self.history_load.append((tag_id, timestamp_date, timestamp_time))  # เพิ่มข้อมูลลงในประวัติ
        if len(self.history_load) > 10:
            self.history_load.pop(0)  # ลบข้อมูลเก่าที่สุดถ้าเกิน 10 รายการ
        print('ประวัติการโหลด:', self.history_load)

    # ฟังก์ชันสำหรับอัปเดตประวัติการปลด
    def update_unload_history(self, tag_id, timestamp_date, timestamp_time):
        print(f"อัปเดตประวัติการปลดด้วย tag_id: {tag_id}, วันที่: {timestamp_date}, เวลา: {timestamp_time}")
        self.history_unload.append((tag_id, timestamp_date, timestamp_time))  # เพิ่มข้อมูลลงในประวัติ
        if len(self.history_unload) > 10:
            self.history_unload.pop(0)  # ลบข้อมูลเก่าที่สุดถ้าเกิน 10 รายการ
        print('ประวัติการปลด:', self.history_unload)

    # ฟังก์ชันสำหรับดึงประวัติทั้งหมด
    def get_history(self):
        return self.history_load, self.history_unload

    # ฟังก์ชันสำหรับดึงรายการประวัติล่าสุด
    def get_last_history_entry(self):
        if self.history_load and self.history_unload:
            return self.history_load[-1], self.history_unload[-1]
        return None

    # ฟังก์ชันสำหรับตรวจสอบสถานะการเชื่อมต่อของอุปกรณ์
    def is_device_connected(self):
        return self.device_connected

# การใช้งานตัวอย่าง
if __name__ == "__main__":
    BAR1_project = Function_BAR1()  # สร้างอ็อบเจกต์จากคลาส
    try:
        while True:
            time.sleep(1)  # หน่วงเวลา 1 วินาที
    except KeyboardInterrupt:
        BAR1_project.running = False  # หยุดการทำงานเมื่อกด Ctrl+C
        BAR1_project.thread.join()  # รอให้ Thread สิ้นสุด
