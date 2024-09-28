function updateDateTime() {
    // อัปเดตวันที่และเวลา
    document.getElementById('date').innerText = new Date().toLocaleDateString();
    document.getElementById('time').innerText = new Date().toLocaleTimeString();
}
setInterval(updateDateTime, 1000);  // เรียกฟังก์ชัน updateDateTime ทุกๆ 1 วินาที

function addRow(tableId) {
    // เพิ่มแถวใหม่ในตาราง
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    const newRow = table.insertRow();

    // สร้างเซลล์สำหรับชื่อและคำสั่ง
    const nameCell = newRow.insertCell(0);
    const commandCell = newRow.insertCell(1);

    // ใส่ช่องกรอกข้อมูลในแต่ละเซลล์
    nameCell.innerHTML = '<input type="text" placeholder="Enter name">';
    commandCell.innerHTML = '<input type="text" placeholder="Enter command">';
}

function restoreTable(tableId) {
    // กู้คืนข้อมูลตาราง
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    table.innerHTML = ''; // ล้างตาราง

    // เพิ่มแถวข้อมูลเริ่มต้น
    const initialData = tableId === 'rfid-table' ? rfidData : lotData;
    initialData.forEach(row => {
        const newRow = table.insertRow();

        // สร้างเซลล์สำหรับชื่อและคำสั่ง
        const nameCell = newRow.insertCell(0);
        const commandCell = newRow.insertCell(1);

        // ใส่ค่าเริ่มต้นในช่องกรอกข้อมูล
        nameCell.innerHTML = `<input type="text" value="${row.name}">`;
        commandCell.innerHTML = `<input type="text" value="${row.command}">`;
    });
}

// ข้อมูลเริ่มต้นสำหรับตาราง RFID
const rfidData = [
    {name: 'Carrier ID', command: 'CARRIER_ID'},
    {name: 'Carrier Status', command: 'CARRIER_STATUS'},
    {name: 'Last cleaning date', command: 'LAST_CLEAN_DATE'},
    {name: 'Next cleaning date', command: 'NEXT_CLEAN_DATE'}
];

// ข้อมูลเริ่มต้นสำหรับตาราง LOT
const lotData = [
    {name: 'Batch ID', command: 'BATCH_ID'},
    {name: 'Product Desc.', command: 'PRODUCT_DESC'},
    {name: 'Lot ID', command: 'LOT_ID'},
    {name: 'Machine ID', command: 'MID'},
    {name: 'Lot Status', command: 'LOT_STATUS'},
    {name: 'Stage/Process Step', command: 'STEP'}
];

document.addEventListener('DOMContentLoaded', function() {
    // กู้คืนตาราง RFID และ LOT เมื่อเอกสารโหลดเสร็จ
    restoreTable('rfid-table');
    restoreTable('lot-table');

    // เพิ่มการฟังเหตุการณ์คลิกให้กับปุ่มบันทึก
    document.getElementById('save-btn').addEventListener('click', saveSettings);
});

function saveSettings() {
    // บันทึกการตั้งค่าจากตาราง RFID และ LOT
    const rfidTable = document.getElementById('rfid-table').getElementsByTagName('tbody')[0];
    const lotTable = document.getElementById('lot-table').getElementsByTagName('tbody')[0];

    const rfidData = [];
    const lotData = [];

    // วนลูปผ่านแถวในตาราง RFID เพื่อเก็บข้อมูล
    for (let row of rfidTable.rows) {
        rfidData.push({
            name: row.cells[0].getElementsByTagName('input')[0].value,
            command: row.cells[1].getElementsByTagName('input')[0].value
        });
    }

    // วนลูปผ่านแถวในตาราง LOT เพื่อเก็บข้อมูล
    for (let row of lotTable.rows) {
        lotData.push({
            name: row.cells[0].getElementsByTagName('input')[0].value,
            command: row.cells[1].getElementsByTagName('input')[0].value
        });
    }

    // ส่งข้อมูลที่บันทึกไปยังเซิร์ฟเวอร์
    fetch('/save_settings', {
        method: 'POST',  // ใช้วิธี POST
        headers: {
            'Content-Type': 'application/json'  // กำหนดหัวข้อเป็น JSON
        },
        body: JSON.stringify({rfidData, lotData})  // แปลงข้อมูลเป็น JSON
    }).then(response => response.json())
    .then(data => {
        // ตรวจสอบว่าการบันทึกสำเร็จหรือไม่
        if (data.success) {
            alert('บันทึกการตั้งค่าสำเร็จ!');
        } else {
            alert('การบันทึกการตั้งค่าล้มเหลว.');
        }
    });
}
