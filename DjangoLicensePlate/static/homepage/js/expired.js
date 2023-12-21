$(document).ready(function () {
    const LpInput = $('input[name="license_plate"]');
    const messagesContainer = $('.messages');
    const table = $('.table-container');
    const pagination = $('.mt-4');
    const prev_page = $('.fa-angle-double-left');
    const next_page = $('.fa-angle-double-right');
    LpInput.on('click', function () {
        messagesContainer.hide();
        table.hide();
        pagination.hide();
    });
});
