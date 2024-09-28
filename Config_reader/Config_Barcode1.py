import usb.core
import usb.util
import time
import logging
import subprocess

# Setup logging
# ตั้งค่าระบบบันทึกข้อความ (logging)
logging.basicConfig(level=logging.INFO)

class RFIDReader:
    def __init__(self, serial_number, device_path):
        self.serial_number = serial_number  # กำหนดหมายเลขซีเรียลของอุปกรณ์
        self.device_path = device_path  # กำหนดตำแหน่งของอุปกรณ์
        self.dev = None  # ตัวแปรสำหรับจัดเก็บอุปกรณ์ USB ที่พบ

    def unbind_usb_device(self):
        try:
            # คำสั่งสำหรับยกเลิกการเชื่อมต่อ USB device
            cmd = f'echo -n "{self.device_path}" | sudo tee /sys/bus/usb/drivers/usb/unbind'
            subprocess.run(cmd, shell=True, check=True)  # รันคำสั่งใน shell
            logging.info(f"Successfully unbound device {self.device_path}")  # บันทึกข้อความว่าการยกเลิกสำเร็จ
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to unbind device {self.device_path}: {e}")  # บันทึกข้อผิดพลาด
            raise  # โยนข้อผิดพลาดขึ้นไป

    def bind_usb_device(self):
        try:
            # คำสั่งสำหรับเชื่อมต่อ USB device
            cmd = f'echo -n "{self.device_path}" | sudo tee /sys/bus/usb/drivers/usb/bind'
            subprocess.run(cmd, shell=True, check=True)  # รันคำสั่งใน shell
            logging.info(f"Successfully bound device {self.device_path}")  # บันทึกข้อความว่าการเชื่อมต่อสำเร็จ
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to bind device {self.device_path}: {e}")  # บันทึกข้อผิดพลาด
            raise  # โยนข้อผิดพลาดขึ้นไป

    def find_rfid_reader(self):
        try:
            # ค้นหาอุปกรณ์ USB ที่มี Vendor ID และ Product ID ตรงกับ RFID reader
            devices = usb.core.find(find_all=True, idVendor=0x0c2e, idProduct=0x1001)
            for dev in devices:
                try:
                    # ตรวจสอบว่าอุปกรณ์ที่พบมีหมายเลขซีเรียลตรงกันหรือไม่
                    if usb.util.get_string(dev, dev.iSerialNumber) == self.serial_number:
                        return dev  # ถ้าตรงกัน ให้ส่งคืนอุปกรณ์นั้น
                except usb.core.USBError as e:
                    logging.error(f"Error finding RFID reader: {e}")  # บันทึกข้อผิดพลาด
                    return None
            return None  # ถ้าไม่พบอุปกรณ์ที่ตรงกัน ให้ส่งคืนค่า None
        except Exception as e:
            logging.error(f"Error finding RFID reader: {e}")  # บันทึกข้อผิดพลาด
            raise  # โยนข้อผิดพลาดขึ้นไป

    def detach_and_claim_interfaces(self):
        try:
            self.dev.set_configuration()  # ตั้งค่า configuration สำหรับอุปกรณ์
            for cfg in self.dev:
                for intf in cfg:
                    # ตรวจสอบว่า interface ใดใช้งานอยู่กับ kernel driver หรือไม่
                    if self.dev.is_kernel_driver_active(intf.bInterfaceNumber):
                        try:
                            self.dev.detach_kernel_driver(intf.bInterfaceNumber)  # ยกเลิก kernel driver ที่เชื่อมต่อ
                            logging.info(f"Kernel driver detached from interface {intf.bInterfaceNumber}.")  # บันทึกข้อความว่าการยกเลิกสำเร็จ
                        except usb.core.USBError as e:
                            logging.error(f"Could not detach kernel driver: {e}")  # บันทึกข้อผิดพลาด
                            raise  # โยนข้อผิดพลาดขึ้นไป

                    try:
                        usb.util.claim_interface(self.dev, intf.bInterfaceNumber)  # อ้างสิทธิ์ interface เพื่อใช้งาน
                        logging.info(f"Interface {intf.bInterfaceNumber} claimed.")  # บันทึกข้อความว่าการอ้างสิทธิ์สำเร็จ
                    except usb.core.USBError as e:
                        logging.error(f"Could not claim interface {intf.bInterfaceNumber}: {e}")  # บันทึกข้อผิดพลาด
                        raise  # โยนข้อผิดพลาดขึ้นไป
        except Exception as e:
            logging.error(f"Error detaching and claiming interfaces: {e}")  # บันทึกข้อผิดพลาด
            raise  # โยนข้อผิดพลาดขึ้นไป

    def read_rfid_data(self):
        try:
            # อ่านข้อมูลจาก RFID reader
            cfg = self.dev.get_active_configuration()  # ดึง configuration ปัจจุบันของอุปกรณ์
            intf = cfg[(0, 0)]  # ดึง interface ที่ใช้
            ep = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )  # หาจุดสิ้นสุด (endpoint) สำหรับอ่านข้อมูล
            if ep is None:
                raise ValueError("Endpoint not found")  # ถ้าไม่พบ endpoint ให้โยนข้อผิดพลาด
            data = ep.read(ep.wMaxPacketSize)  # อ่านข้อมูลจาก endpoint
            return data  # ส่งคืนข้อมูลที่อ่านได้
        except usb.core.USBError as e:
            logging.warning(f"USB Error: {e}")  # บันทึกข้อผิดพลาดของ USB
            return None  # ส่งคืนค่า None เมื่อเกิดข้อผิดพลาด

    def format_to_kbw(self, data):
        # แผนที่สำหรับแปลงข้อมูลจากรหัสคีย์บอร์ด (KBW) เป็นตัวอักษร
        kbw_map = {
            0x04: 'a', 0x05: 'b', 0x06: 'c', 0x07: 'd', 0x08: 'e',
            0x09: 'f', 0x0A: 'g', 0x0B: 'h', 0x0C: 'i', 0x0D: 'j',
            0x0E: 'k', 0x0F: 'l', 0x10: 'm', 0x11: 'n', 0x12: 'o',
            0x13: 'p', 0x14: 'q', 0x15: 'r', 0x16: 's', 0x17: 't',
            0x18: 'u', 0x19: 'v', 0x1A: 'w', 0x1B: 'x', 0x1C: 'y',
            0x1D: 'z', 0x1E: '1', 0x1F: '2', 0x20: '3', 0x21: '4',
            0x22: '5', 0x23: '6', 0x24: '7', 0x25: '8', 0x26: '9',
            0x27: '0', 0x28: '\n', 0x29: '\x1b', 0x2A: '\b', 0x2B: '\t',
            0x2C: ' ', 0x2D: '-', 0x2E: '=', 0x2F: '[', 0x30: ']',
            0x31: '\\', 0x32: '#', 0x33: ';', 0x34: '\'', 0x35: '`',
            0x36: ',', 0x37: '.', 0x38: '/'
        }
        # แปลงข้อมูลเป็นตัวอักษรตามแผนที่ที่กำหนด
        kbw_data = [kbw_map.get(byte, '') for byte in data if byte in kbw_map]
        return kbw_data  # ส่งคืนข้อมูลที่แปลงแล้ว

    def run(self):
        while True:
            try:
                # Unbind USB device initially
                # ยกเลิกการเชื่อมต่อ USB device ในตอนแรก
                self.unbind_usb_device()
                self.dev = self.find_rfid_reader()  # ค้นหาอุปกรณ์ RFID reader
                if self.dev is None:
                    logging.error(f"Device with serial number {self.serial_number} not found")  # ถ้าไม่พบอุปกรณ์ ให้บันทึกข้อผิดพลาด
                    time.sleep(5)  # รอ 5 วินาทีก่อนลองใหม่
                    continue

                logging.info(f"RFID Reader with serial number {self.serial_number} found")  # บันทึกข้อความว่าเจออุปกรณ์แล้ว
                self.detach_and_claim_interfaces()  # ยกเลิกและอ้างสิทธิ์ interface

                tag_id = []  # เก็บข้อมูล Tag ID ที่อ่านได้
                start_time = None  # เวลาที่เริ่มอ่านข้อมูล
                timer_running = False  # ตัวแปรสถานะของตัวจับเวลา

                while True:
                    data = self.read_rfid_data()  # อ่านข้อมูลจาก RFID reader
                    if data:
                        logging.info(f"Raw data: {data}")  # บันทึกข้อมูลดิบที่อ่านได้
                        kbw_data = self.format_to_kbw(data)  # แปลงข้อมูลเป็นรูปแบบคีย์บอร์ด
                        logging.info(f"KBW data: {kbw_data}")  # บันทึกข้อมูลที่แปลงแล้ว
                        if kbw_data:
                            tag_id.extend(kbw_data)  # เพิ่มข้อมูลใน tag_id
                            if not timer_running:
                                start_time = time.time()  # เริ่มจับเวลา
                                timer_running = True
                        time.sleep(0.01)  # หยุดพักชั่วคราว

                    if timer_running and (time.time() - start_time >= 2):  # ถ้าผ่านไป 2 วินาที
                        if len(tag_id) > 25:  # ถ้าข้อมูล tag_id มีมากกว่า 25 ตัวอักษร
                            tag_id = []  # ล้างข้อมูล tag_id
                        else:
                            logging.info(f"Tag ID: {''.join(tag_id)}")  # บันทึกข้อมูล Tag ID ที่อ่านได้
                        tag_id = []  # ล้างข้อมูล tag_id
                        timer_running = False  # หยุดจับเวลา

                    # ตรวจสอบว่าอุปกรณ์ยังคงเชื่อมต่ออยู่หรือไม่
                    if self.find_rfid_reader() is None:
                        logging.warning("Device disconnected")  # บันทึกข้อความว่าอุปกรณ์ถูกถอดออก
                        break  # ออกจากลูป

            except KeyboardInterrupt:
                logging.info("Exiting program")  # บันทึกข้อความเมื่อออกจากโปรแกรม
                self.bind_usb_device()  # เชื่อมต่อ USB device ใหม่
                break  # ออกจากลูป
            except Exception as e:
                logging.error(f"An error occurred: {e}")  # บันทึกข้อผิดพลาด
                self.bind_usb_device()  # เชื่อมต่อ USB device ใหม่

if __name__ == "__main__":
    serial_number = "21148B0941"  # หมายเลขซีเรียลของอุปกรณ์
    device_path = "1-1.4"  # ปรับให้ตรงกับตำแหน่งอุปกรณ์
    rfid_reader = RFIDReader(serial_number, device_path)  # สร้างอ็อบเจกต์ RFIDReader
    rfid_reader.run()  # เริ่มการทำงานของ RFIDReader