function updateDateTime() {
    document.getElementById('date').innerText = new Date().toLocaleDateString();
    document.getElementById('time').innerText = new Date().toLocaleTimeString();
}
setInterval(updateDateTime, 1000);

function addRow(tableId) {
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    const newRow = table.insertRow();

    const nameCell = newRow.insertCell(0);
    const commandCell = newRow.insertCell(1);
    const showCell = newRow.insertCell(2);
    const deleteCell = newRow.insertCell(3);

    nameCell.innerHTML = '<input type="text" placeholder="Enter name">';
    commandCell.innerHTML = '<input type="text" placeholder="Enter command">';
    showCell.innerHTML = '<input type="checkbox">';
    deleteCell.innerHTML = '&#x1F5D1;';
    deleteCell.className = 'delete-icon';
    deleteCell.onclick = function() {
        table.deleteRow(newRow.rowIndex - 1);
    };
}

function restoreTable(tableId) {
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    table.innerHTML = ''; // Clear table

    // Add initial rows
    const initialData = tableId === 'rfid-table' ? rfidData : lotData;
    initialData.forEach(row => {
        const newRow = table.insertRow();

        const nameCell = newRow.insertCell(0);
        const commandCell = newRow.insertCell(1);
        const showCell = newRow.insertCell(2);
        const deleteCell = newRow.insertCell(3);

        nameCell.innerHTML = `<input type="text" value="${row.name}">`;
        commandCell.innerHTML = `<input type="text" value="${row.command}">`;
        showCell.innerHTML = `<input type="checkbox" ${row.show ? 'checked' : ''}>`;
        deleteCell.innerHTML = '&#x1F5D1;';
        deleteCell.className = 'delete-icon';
        deleteCell.onclick = function() {
            table.deleteRow(newRow.rowIndex - 1);
        };
    });
}

const rfidData = [
    {name: 'Carrier ID', command: 'CARRIER_ID', show: true},
    {name: 'Carrier Status', command: 'CARRIER_STATUS', show: true},
    {name: 'Last cleaning date', command: 'LAST_CLEAN_DATE', show: false},
    {name: 'Next cleaning date', command: 'NEXT_CLEAN_DATE', show: false}
];

const lotData = [
    {name: 'Batch ID', command: 'BATCH_ID', show: true},
    {name: 'Product Desc.', command: 'PRODUCT_DESC', show: true},
    {name: 'Lot ID', command: 'LOT_ID', show: true},
    {name: 'Machine ID', command: 'MID', show: false},
    {name: 'Lot Status', command: 'LOT_STATUS', show: false},
    {name: 'Stage/Process Step', command: 'STEP', show: false}
];

document.addEventListener('DOMContentLoaded', function() {
    restoreTable('rfid-table');
    restoreTable('lot-table');
    document.getElementById('save-btn').addEventListener('click', saveSettings);
});

function saveSettings() {
    const rfidTable = document.getElementById('rfid-table').getElementsByTagName('tbody')[0];
    const lotTable = document.getElementById('lot-table').getElementsByTagName('tbody')[0];

    const rfidData = [];
    const lotData = [];

    for (let row of rfidTable.rows) {
        rfidData.push({
            name: row.cells[0].getElementsByTagName('input')[0].value,
            command: row.cells[1].getElementsByTagName('input')[0].value,
            show: row.cells[2].getElementsByTagName('input')[0].checked
        });
    }

    for (let row of lotTable.rows) {
        lotData.push({
            name: row.cells[0].getElementsByTagName('input')[0].value,
            command: row.cells[1].getElementsByTagName('input')[0].value,
            show: row.cells[2].getElementsByTagName('input')[0].checked
        });
    }

    fetch('/save_settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({rfidData, lotData})
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Settings saved successfully!');
        } else {
            alert('Failed to save settings.');
        }
    });
}
