function fetchAllData() {
    // ดึงข้อมูลทั้งหมดจากเซิร์ฟเวอร์
    fetch('/get_all_data')
        .then(response => response.json())  // แปลงการตอบกลับเป็น JSON
        .then(data => {
            // อัปเดตข้อมูล RFID
            document.getElementById('rfid-load').innerText = data.rfid_data.loaded_tag_id || '';
            document.getElementById('timestamp-load').innerText = `${data.rfid_data.loaded_timestamp[0] || ''} ${data.rfid_data.loaded_timestamp[1] || ''}`;
            document.getElementById('rfid-unload').innerText = data.rfid_data.unloaded_tag_id || '';
            document.getElementById('timestamp-unload').innerText = `${data.rfid_data.unloaded_timestamp[0] || ''} ${data.rfid_data.unloaded_timestamp[1] || ''}`;

            // อัปเดตข้อมูล Barcode1
            document.getElementById('barcode1-load').innerText = data.barcode1_data.loaded_tag_id || '';
            document.getElementById('barcode1-timestamp-load').innerText = `${data.barcode1_data.loaded_timestamp[0] || ''} ${data.barcode1_data.loaded_timestamp[1] || ''}`;
            document.getElementById('barcode1-unload').innerText = data.barcode1_data.unloaded_tag_id || '';
            document.getElementById('barcode1-timestamp-unload').innerText = `${data.barcode1_data.unloaded_timestamp[0] || ''} ${data.barcode1_data.unloaded_timestamp[1] || ''}`;

            // อัปเดตข้อมูล Barcode2
            document.getElementById('barcode2-load').innerText = data.barcode2_data.loaded_tag_id || '';
            document.getElementById('barcode2-timestamp-load').innerText = `${data.barcode2_data.loaded_timestamp[0] || ''} ${data.barcode2_data.loaded_timestamp[1] || ''}`;
            document.getElementById('barcode2-unload').innerText = data.barcode2_data.unloaded_tag_id || '';
            document.getElementById('barcode2-timestamp-unload').innerText = `${data.barcode2_data.unloaded_timestamp[0] || ''} ${data.barcode2_data.unloaded_timestamp[1] || ''}`;

            // อัปเดตสถานะของเซ็นเซอร์
            const rfidStatus = data.sensor_status.rfid === "ON" ? '<span style="color: green;">ON</span>' : '<span style="color: red;">OFF</span>';
            const barcode1Status = data.sensor_status.barcode1 === "ON" ? '<span style="color: green;">ON</span>' : '<span style="color: red;">OFF</span>';
            const barcode2Status = data.sensor_status.barcode2 === "ON" ? '<span style="color: green;">ON</span>' : '<span style="color: red;">OFF</span>';

            document.getElementById('rfid-sensor-status').innerHTML = `สถานะ RFID: ${rfidStatus}`;
            document.getElementById('barcode1-sensor-status').innerHTML = `สถานะ Barcode#1: ${barcode1Status}`;
            document.getElementById('barcode2-sensor-status').innerHTML = `สถานะ Barcode#2: ${barcode2Status}`;
        });
}

function updateDateTime() {
    // อัปเดตวันที่และเวลา
    document.getElementById('date').innerText = new Date().toLocaleDateString();
    document.getElementById('time').innerText = new Date().toLocaleTimeString();
}

function updateDashboard() {
    // ดึงข้อมูลการตั้งค่าจากแดชบอร์ด
    fetch('/update_dashboard')
        .then(response => response.json())  // แปลงการตอบกลับเป็น JSON
        .then(data => {
            const rfidData = data.rfidData;
            const lotData = data.lotData;
            
            // อัปเดตการแสดงผลข้อมูล RFID
            document.getElementById('carrier-id').innerText = rfidData.find(item => item.name === 'Carrier ID')?.command || '';
            document.getElementById('carrier-status').innerText = rfidData.find(item => item.name === 'Carrier Status')?.command || '';
            document.getElementById('last-cleaning').innerText = rfidData.find(item => item.name === 'Last cleaning date')?.command || '';
            document.getElementById('next-cleaning').innerText = rfidData.find(item => item.name === 'Next cleaning date')?.command || '';

            // อัปเดตการแสดงผลข้อมูล LOT
            document.getElementById('batch-id').innerText = lotData.find(item => item.name === 'Batch ID')?.command || '';
            document.getElementById('product-desc').innerText = lotData.find(item => item.name === 'Product Desc.')?.command || '';
            document.getElementById('lot-id').innerText = lotData.find(item => item.name === 'Lot ID')?.command || '';
            document.getElementById('machine-id').innerText = lotData.find(item => item.name === 'Machine ID')?.command || '';
            document.getElementById('lot-status').innerText = lotData.find(item => item.name === 'Lot Status')?.command || '';
            document.getElementById('process-step').innerText = lotData.find(item => item.name === 'Stage/Process Step')?.command || '';
        });
}

document.addEventListener('DOMContentLoaded', function() {
    // ตั้งค่าให้เรียกฟังก์ชัน fetchAllData ทุกๆ 1 วินาที
    setInterval(fetchAllData, 1000);
    // ตั้งค่าให้เรียกฟังก์ชัน updateDateTime ทุกๆ 1 วินาที
    setInterval(updateDateTime, 1000);
    // ตั้งค่าให้เรียกฟังก์ชัน updateDashboard ทุกๆ 1 วินาที
    setInterval(updateDashboard, 1000);
});
