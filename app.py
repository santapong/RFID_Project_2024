from flask import Flask, render_template, jsonify, request
import datetime
import logging


app = Flask(__name__)

# Enable logging
logging.basicConfig(level=logging.DEBUG)

# Function imports
from function_RFID import Function_RFID
from function_BAR1 import Function_BAR1
from function_BAR2 import Function_BAR2

rfid_project = Function_RFID()
BAR1_project = Function_BAR1()
BAR2_project = Function_BAR2()

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

@app.route('/')
def home():
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template('dashboard.html', current_date=current_date, current_time=current_time)

@app.route("/dashboard")
def dashboard():
    return render_template('dashboard.html')

@app.route("/history")
def history():
    return render_template('history.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/settings")
def setting():
    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return render_template('settings.html', current_date=current_date, current_time=current_time)

#dashboard
@app.route('/get_all_data')
def get_all_data():
    # Fetch data from all devices
    rfid_data = rfid_project.rfid_data
    barcode1_data = BAR1_project.barcode1_data
    barcode2_data = BAR2_project.barcode2_data
    
    # Fetch sensor statuses
    rfid_status = "ON" if rfid_project.is_device_connected() else "OFF"
    barcode1_status = "ON" if BAR1_project.is_device_connected() else "OFF"
    barcode2_status = "ON" if BAR2_project.is_device_connected() else "OFF"
    
    # Combine all data
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

#history
@app.route("/get_history_RFID")
def get_history_rfid():
    load_history, unload_history = rfid_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

@app.route("/get_history_BAR1")
def get_history_BAR1():
    load_history, unload_history = BAR1_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

@app.route("/get_history_BAR2")
def get_history_BAR2():
    load_history, unload_history = BAR2_project.get_history()
    data = {
        'load_history': load_history,
        'unload_history': unload_history
    }
    return jsonify(data)

#setting
@app.route('/save_settings', methods=['POST'])
def save_settings():
    global settings
    settings = request.json
    app.logger.debug(f"Settings received: {settings}")
    return jsonify({"success": True})

@app.route('/update_dashboard')
def update_dashboard():
    global settings
    return jsonify(settings)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
