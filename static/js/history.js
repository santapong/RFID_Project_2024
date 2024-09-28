function fetchHistoryData(url, loadTableId, unloadTableId) {
    // ดึงข้อมูลประวัติการโหลดและปลดจากเซิร์ฟเวอร์
    fetch(url)
        .then(response => response.json())  // แปลงการตอบกลับเป็น JSON
        .then(data => {
            const loadHistoryTable = document.getElementById(loadTableId);  // ตารางประวัติการโหลด
            const unloadHistoryTable = document.getElementById(unloadTableId);  // ตารางประวัติการปลด
            loadHistoryTable.innerHTML = '';  // ล้างเนื้อหาของตารางการโหลด
            unloadHistoryTable.innerHTML = '';  // ล้างเนื้อหาของตารางการปลด

            // วนลูปเพิ่มข้อมูลการโหลดลงในตาราง
            data.load_history.forEach(entry => {
                const row = document.createElement('tr');  // สร้างแถวใหม่ในตาราง
                const tagIdCell = document.createElement('td');  // สร้างเซลล์สำหรับ tag ID
                const dateCell = document.createElement('td');  // สร้างเซลล์สำหรับวันที่
                const timeCell = document.createElement('td');  // สร้างเซลล์สำหรับเวลา

                tagIdCell.innerText = entry[0];  // กำหนดค่า tag ID
                tagIdCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ
                dateCell.innerText = entry[1];  // กำหนดค่าวันที่
                dateCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ
                timeCell.innerText = entry[2];  // กำหนดค่าเวลา
                timeCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ

                row.appendChild(tagIdCell);  // เพิ่มเซลล์ tag ID ลงในแถว
                row.appendChild(dateCell);  // เพิ่มเซลล์วันที่ลงในแถว
                row.appendChild(timeCell);  // เพิ่มเซลล์เวลาลงในแถว

                loadHistoryTable.appendChild(row);  // เพิ่มแถวลงในตารางประวัติการโหลด
            });

            // วนลูปเพิ่มข้อมูลการปลดลงในตาราง
            data.unload_history.forEach(entry => {
                const row = document.createElement('tr');  // สร้างแถวใหม่ในตาราง
                const tagIdCell = document.createElement('td');  // สร้างเซลล์สำหรับ tag ID
                const dateCell = document.createElement('td');  // สร้างเซลล์สำหรับวันที่
                const timeCell = document.createElement('td');  // สร้างเซลล์สำหรับเวลา

                tagIdCell.innerText = entry[0];  // กำหนดค่า tag ID
                tagIdCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ
                dateCell.innerText = entry[1];  // กำหนดค่าวันที่
                dateCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ
                timeCell.innerText = entry[2];  // กำหนดค่าเวลา
                timeCell.classList.add('cell_color');  // เพิ่มคลาสสำหรับการจัดรูปแบบ

                row.appendChild(tagIdCell);  // เพิ่มเซลล์ tag ID ลงในแถว
                row.appendChild(dateCell);  // เพิ่มเซลล์วันที่ลงในแถว
                row.appendChild(timeCell);  // เพิ่มเซลล์เวลาลงในแถว

                unloadHistoryTable.appendChild(row);  // เพิ่มแถวลงในตารางประวัติการปลด
            });
        });
}

function synchronizeScroll(element1, element2) {
    // ฟังก์ชันสำหรับซิงโครไนซ์การเลื่อนของสองตาราง
    element1.addEventListener('scroll', function() {
        element2.scrollTop = element1.scrollTop;  // ตั้งค่าให้ตารางที่สองเลื่อนตามตารางแรก
    });
    element2.addEventListener('scroll', function() {
        element1.scrollTop = element2.scrollTop;  // ตั้งค่าให้ตารางแรกเลื่อนตามตารางที่สอง
    });
}

function updateDateTime() {
    // อัปเดตวันที่และเวลา
    document.getElementById('date').innerText = new Date().toLocaleDateString();  // แสดงวันที่
    document.getElementById('time').innerText = new Date().toLocaleTimeString();  // แสดงเวลา
}

document.addEventListener('DOMContentLoaded', function() {
    const loadContainerRFID = document.querySelector('.load-container-rfid');  // ค้นหาองค์ประกอบการโหลด RFID
    const unloadContainerRFID = document.querySelector('.unload-container-rfid');  // ค้นหาองค์ประกอบการปลด RFID
    synchronizeScroll(loadContainerRFID, unloadContainerRFID);  // ซิงโครไนซ์การเลื่อนของการโหลดและการปลด RFID

    const loadContainerBarcode1 = document.querySelector('.load-container-barcode1');  // ค้นหาองค์ประกอบการโหลด Barcode1
    const unloadContainerBarcode1 = document.querySelector('.unload-container-barcode1');  // ค้นหาองค์ประกอบการปลด Barcode1
    synchronizeScroll(loadContainerBarcode1, unloadContainerBarcode1);  // ซิงโครไนซ์การเลื่อนของการโหลดและการปลด Barcode1

    const loadContainerBarcode2 = document.querySelector('.load-container-barcode2');  // ค้นหาองค์ประกอบการโหลด Barcode2
    const unloadContainerBarcode2 = document.querySelector('.unload-container-barcode2');  // ค้นหาองค์ประกอบการปลด Barcode2
    synchronizeScroll(loadContainerBarcode2, unloadContainerBarcode2);  // ซิงโครไนซ์การเลื่อนของการโหลดและการปลด Barcode2

    // ตั้งค่าให้ดึงข้อมูลประวัติ RFID ทุกๆ 1 วินาที
    setInterval(() => fetchHistoryData('/get_history_RFID', 'load-history-table-rfid', 'unload-history-table-rfid'), 1000);
    // ตั้งค่าให้ดึงข้อมูลประวัติ Barcode1 ทุกๆ 1 วินาที
    setInterval(() => fetchHistoryData('/get_history_BAR1', 'load-history-table-barcode1', 'unload-history-table-barcode1'), 1000);
    // ตั้งค่าให้ดึงข้อมูลประวัติ Barcode2 ทุกๆ 1 วินาที
    setInterval(() => fetchHistoryData('/get_history_BAR2', 'load-history-table-barcode2', 'unload-history-table-barcode2'), 1000);
    // ตั้งค่าให้อัปเดตวันที่และเวลา ทุกๆ 1 วินาที
    setInterval(updateDateTime, 1000);
});
