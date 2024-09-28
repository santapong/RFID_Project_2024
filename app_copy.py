from flask import Flask, render_template, jsonify, request, send_file
import datetime
import logging
import pandas as pd
import os
import threading
from threading import Lock
import time

# สร้างแอป Flask
app = Flask(__name__)

# เปิดใช้งานระบบบันทึกข้อมูล (Logging)
logging.basicConfig(level=logging.DEBUG)

# ฟังก์ชันนำเข้า
from function_RFID import Function_RFID
from function_BAR1 import Function_BAR1
from function_BAR2 import Function_BAR2

# สร้างโปรเจคต่างๆ
rfid_project = Function_RFID()
BAR1_project = Function_BAR1()
BAR2_project = Function_BAR2()

# เส้นทางไฟล์ Excel
excel_path = "/home/pi/Desktop/RFID_Project_2024/store.xlsx"

# สร้างอ็อบเจกต์ล็อก
excel_lock = Lock()

# ตัวแปรเก็บสถานะล่าสุด
last_status = {
    "RFID Load": None,
    "Barcode#1 Load": None,
    "Barcode#2 Load": None,
    "RFID Unload": None,
    "Barcode#1 Unload": None,
    "Barcode#2 Unload": None,
}

# ตัวแปรตั้งค่าของระบบ
settings = {
    "rfidData": [
        {"name": "Carrier ID", "command": "CARRIER_ID"},
        {"name": "Carrier Status", "command": "CARRIER_STATUS"},
        {"name": "Last cleaning date", "command": "LAST_CLEAN_DATE"},
        {"name": "Next cleaning date", "command": "NEXT_CLEAN_DATE"},
    ],
    "lotData": [
        {"name": "Batch ID", "command": "BATCH_ID"},
        {"name": "Product Desc.", "command": "PRODUCT_DESC"},
        {"name": "Lot ID", "command": "LOT_ID"},
        {"name": "Machine ID", "command": "MID"},
        {"name": "Lot Status", "command": "LOT_STATUS"},
        {"name": "Stage/Process Step", "command": "STEP"},
    ]
}

# เส้นทางหน้าแรกของแอป
@app.route('/')
def home():
    # นำวันที่และเวลาในปัจจุบันมาใช้
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template('dashboard.html', current_date=current_date, current_time=current_time)

# เส้นทางสำหรับหน้าแดชบอร์ด
@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

# เส้นทางสำหรับหน้าประวัติ
@app.route("/history")
def history():
    return render_template('history.html')

# เส้นทางสำหรับหน้าเกี่ยวกับ
@app.route("/about")
def about():
    return render_template('about.html')

# เส้นทางสำหรับหน้าตั้งค่า
@app.route("/settings")
def setting():
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template('settings.html', current_date=current_date, current_time=current_time)

# เส้นทางสำหรับดึงข้อมูลทั้งหมดจากอุปกรณ์
@app.route('/get_all_data')
def get_all_data():
    # ดึงข้อมูลจากทุกอุปกรณ์
    rfid_data = rfid_project.rfid_data
    barcode1_data = BAR1_project.barcode1_data
    barcode2_data = BAR2_project.barcode2_data
    
    # ดึงสถานะของเซ็นเซอร์
    rfid_status = "ON" if rfid_project.is_device_connected() else "OFF"
    barcode1_status = "ON" if BAR1_project.is_device_connected() else "OFF"
    barcode2_status = "ON" if BAR2_project.is_device_connected() else "OFF"
    
    # รวมข้อมูลทั้งหมด
    all_data = {
        "rfid_data": rfid_data,
        "barcode1_data": barcode1_data,
        "barcode2_data": barcode2_data,
        "sensor_status": {
            "rfid": rfid_status,
            "barcode1": barcode1_status,
            "barcode2": barcode2_status
        }
    }
    return jsonify(all_data)

# เส้นทางสำหรับดึงประวัติ RFID
@app.route("/get_history_RFID")
def get_history_rfid():
    load_history, unload_history = rfid_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

# เส้นทางสำหรับดึงประวัติ Barcode#1
@app.route("/get_history_BAR1")
def get_history_BAR1():
    load_history, unload_history = BAR1_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

# เส้นทางสำหรับดึงประวัติ Barcode#2
@app.route("/get_history_BAR2")
def get_history_BAR2():
    load_history, unload_history = BAR2_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

# เส้นทางสำหรับบันทึกการตั้งค่า
@app.route('/save_settings', methods=['POST'])
def save_settings():
    global settings
    settings = request.json
    app.logger.debug(f"Settings received: {settings}")
    return jsonify({"success": True})

# เส้นทางสำหรับอัปเดตแดชบอร์ด
@app.route('/update_dashboard')
def update_dashboard():
    global settings
    return jsonify(settings)

# ฟังก์ชันสำหรับอัปเดตไฟล์ Excel
def update_excel():
    global last_status
    
    try:
        # ใช้ล็อกก่อนเข้าถึงไฟล์ Excel
        with excel_lock:
            # สร้าง timestamp ปัจจุบัน
            current_timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            current_date = datetime.datetime.now().strftime("%d-%m-%Y")

            # รวบรวมข้อมูล
            rfid_data = rfid_project.rfid_data
            barcode1_data = BAR1_project.barcode1_data
            barcode2_data = BAR2_project.barcode2_data

            # ดึงข้อมูลจากการตั้งค่า
            carrier_id = next((item['command'] for item in settings['rfidData'] if item['name'] == 'Carrier ID'), '')
            carrier_status = next((item['command'] for item in settings['rfidData'] if item['name'] == 'Carrier Status'), '')
            lot_id = next((item['command'] for item in settings['lotData'] if item['name'] == 'Lot ID'), '')
            batch_id = next((item['command'] for item in settings['lotData'] if item['name'] == 'Batch ID'), '')
            product_desc = next((item['command'] for item in settings['lotData'] if item['name'] == 'Product Desc.'), '')
            machine_id = next((item['command'] for item in settings['lotData'] if item['name'] == 'Machine ID'), '')
            lot_status = next((item['command'] for item in settings['lotData'] if item['name'] == 'Lot Status'), '')
            step = next((item['command'] for item in settings['lotData'] if item['name'] == 'Stage/Process Step'), '')

            # ตรวจสอบว่ามีข้อมูลโหลดใหม่หรือไม่
            new_load = (
                rfid_data.get('loaded_tag_id') and
                barcode1_data.get('loaded_tag_id') and
                barcode2_data.get('loaded_tag_id')
            )

            # ตรวจสอบว่ามีข้อมูลปลดใหม่หรือไม่
            new_unload = (
                rfid_data.get('unloaded_tag_id') and
                barcode1_data.get('unloaded_tag_id') and
                barcode2_data.get('unloaded_tag_id')
            )

            # เตรียมข้อมูลสำหรับไฟล์ Excel
            combined_data = {
                "Timestamp": current_timestamp,
                "RFID Load": rfid_data.get('loaded_tag_id', '') if new_load else '',
                "Barcode#1 Load": barcode1_data.get('loaded_tag_id', '') if new_load else '',
                "Barcode#2 Load": barcode2_data.get('loaded_tag_id', '') if new_load else '',
                "RFID Unload": rfid_data.get('unloaded_tag_id', '') if new_unload and not new_load else '',
                "Barcode#1 Unload": barcode1_data.get('unloaded_tag_id', '') if new_unload and not new_load else '',
                "Barcode#2 Unload": barcode2_data.get('unloaded_tag_id', '') if new_unload and not new_load else '',
                "Carrier ID": carrier_id,
                "Carrier Status": carrier_status,
                "Last Cleaning Date": rfid_data.get('loaded_timestamp', ['', ''])[0], 
                "Next Cleaning Date": rfid_data.get('unloaded_timestamp', ['', ''])[0], 
                "Batch ID": batch_id,
                "Product Desc.": product_desc,
                "Lot ID": lot_id,
                "Machine ID": machine_id,
                "Lot Status": lot_status,
                "Stage/Process Step": step,
                "Date": current_date,
                "Total Lot": "1"
            }

            if new_load:
                # ตรวจสอบว่ามีการเปลี่ยนแปลงสถานะการโหลดหรือไม่
                if combined_data["RFID Load"] != last_status["RFID Load"] or \
                   combined_data["Barcode#1 Load"] != last_status["Barcode#1 Load"] or \
                   combined_data["Barcode#2 Load"] != last_status["Barcode#2 Load"]:
                    last_status["RFID Load"] = combined_data["RFID Load"]
                    last_status["Barcode#1 Load"] = combined_data["Barcode#1 Load"]
                    last_status["Barcode#2 Load"] = combined_data["Barcode#2 Load"]
                    last_status["RFID Unload"] = None  # ล้างสถานะการปลด
                    last_status["Barcode#1 Unload"] = None  # ล้างสถานะการปลด
                    last_status["Barcode#2 Unload"] = None  # ล้างสถานะการปลด

                    # เขียนข้อมูลลงใน Excel
                    app.logger.debug(f"Data to be written to Excel: {combined_data}")

                    if not os.path.isfile(excel_path):
                        df = pd.DataFrame([combined_data])
                        df.to_excel(excel_path, index=False, sheet_name='RFID_Barcode_Data', engine='openpyxl')
                        app.logger.info(f"Excel file created at {excel_path}")
                    else:
                        df = pd.read_excel(excel_path, engine='openpyxl')
                        new_df = pd.DataFrame([combined_data])
                        df = pd.concat([df, new_df], ignore_index=True)
                        df = df[list(combined_data.keys())]  # ทำให้แน่ใจว่าลำดับคอลัมน์ถูกต้อง
                        df.to_excel(excel_path, index=False, sheet_name='RFID_Barcode_Data', engine='openpyxl')
                        app.logger.info(f"Data appended to Excel file at {excel_path}")

            elif new_unload and not new_load:
                # ตรวจสอบว่ามีการเปลี่ยนแปลงสถานะการปลดหรือไม่
                if combined_data["RFID Unload"] != last_status["RFID Unload"] or \
                   combined_data["Barcode#1 Unload"] != last_status["Barcode#1 Unload"] or \
                   combined_data["Barcode#2 Unload"] != last_status["Barcode#2 Unload"]:
                    last_status["RFID Unload"] = combined_data["RFID Unload"]
                    last_status["Barcode#1 Unload"] = combined_data["Barcode#1 Unload"]
                    last_status["Barcode#2 Unload"] = combined_data["Barcode#2 Unload"]

                    # เขียนข้อมูลลงใน Excel
                    app.logger.debug(f"Data to be written to Excel: {combined_data}")

                    if not os.path.isfile(excel_path):
                        df = pd.DataFrame([combined_data])
                        df.to_excel(excel_path, index=False, sheet_name='RFID_Barcode_Data', engine='openpyxl')
                        app.logger.info(f"Excel file created at {excel_path}")
                    else:
                        df = pd.read_excel(excel_path, engine='openpyxl')
                        new_df = pd.DataFrame([combined_data])
                        df = pd.concat([df, new_df], ignore_index=True)
                        df = df[list(combined_data.keys())]  # ทำให้แน่ใจว่าลำดับคอลัมน์ถูกต้อง
                        df.to_excel(excel_path, index=False, sheet_name='RFID_Barcode_Data', engine='openpyxl')
                        app.logger.info(f"Data appended to Excel file at {excel_path}")

    except Exception as e:
        # บันทึกข้อผิดพลาดที่เกิดขึ้นระหว่างการอัปเดต Excel
        app.logger.error(f"Error in update_excel: {e}")
        return {"success": False, "error": str(e)}

    return {"success": True}

# ฟังก์ชันสำหรับการทำงานในเบื้องหลัง
def background_task():
    while True:
        update_excel()
        time.sleep(1)

# เริ่มต้นการทำงานใน Thread เบื้องหลัง
thread = threading.Thread(target=background_task)
thread.daemon = True
thread.start()

# เริ่มต้นแอป Flask
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
