function updateDateTime() {
    document.getElementById('date').innerText = new Date().toLocaleDateString();
    document.getElementById('time').innerText = new Date().toLocaleTimeString();
}
setInterval(updateDateTime, 1000);
