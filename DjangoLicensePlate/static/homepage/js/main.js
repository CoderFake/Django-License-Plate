function formatNumber(num) {
    return num < 10 ? "0" + num : num;
}
function updateCurrentTime() {
    var now = new Date();
    var hours = formatNumber(now.getHours());
    var minutes = formatNumber(now.getMinutes());
    var dayOfWeek = ["Chủ nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"][now.getDay()];
    var day = now.getDate();
    var month = now.getMonth() + 1;
    var year = now.getFullYear();

    var currentTimeString = hours + ":" + minutes + " | " + dayOfWeek + ", ngày " + day + " tháng " + month + " năm " + year;

    $("#current-time").text(currentTimeString);
}
setInterval(updateCurrentTime, 60000);
updateCurrentTime();