
$(document).ready(function () {
    const Input = $('.form-control');
    const messagesContainer = $('.messages');
    const resultDiv = $("#result");
    if (messagesContainer.text().trim() === "") {
        messagesContainer.hide();
    }
    Input.on('click', function () {
        messagesContainer.hide();
        resultDiv.html("");
    });
});
$(document).ready(function() {
    var inputs = [
        {
            inputId: 'month_price_range',
            outputId: 'month_price_rangeV',
            formControlId: 'month_price_input'
        },
        {
            inputId: 'day_price1_range',
            outputId: 'day_price1_rangeV',
            formControlId: 'day_price1_input'
        },
        {
            inputId: 'day_price2_range',
            outputId: 'day_price2_rangeV',
            formControlId: 'day_price2_input'
        },
        {
            inputId: 'time_day1_range',
            outputId: 'time_day1_rangeV',
            formControlId: 'time_day1_input'
        },
        {
            inputId: 'time_day2_range',
            outputId: 'time_day2_rangeV',
            formControlId: 'time_day2_input'
        }
    ];
    function formatValue(value, formControlId) {
        if (formControlId.startsWith('month_price')) {
            return value.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' VNĐ';
        } else if (formControlId.startsWith('day_price')) {
            return value.replace(/\B(?=(\d{3})+(?!\d))/g, '.') + ' VNĐ';
        } else if (formControlId.startsWith('time_day')) {
            return value + ' Giờ';
        }
        return value;
    }

    $.each(inputs, function(index, item) {
        var range = document.getElementById(item.inputId);
        var rangeV = document.getElementById(item.outputId);
        var formControl = document.getElementById(item.formControlId);
        if(range) {
            var setValue = function () {
                var newValue = Number((range.value - range.min) * 100 / (range.max - range.min));
                var newPosition = 10 - (newValue * 0.2);
                rangeV.innerHTML = '<span>' + range.value + '</span>';
                rangeV.style.left = 'calc(' + newValue + '% + (' + newPosition + 'px))';
                formControl.value = formatValue(range.value, item.formControlId);
            };

            $(document).ready(setValue);
            $(range).on('input', setValue);
        }
    });
});


// $(document).ready(function() {
//     // Array containing information about input, range, and rangeV
//     var inputs = [
//         {
//             inputId: 'month_price_range',
//             outputId: 'month_price_rangeV',
//             formControlId: 'month_price_input'
//         },
//         {
//             inputId: 'day_price1_range',
//             outputId: 'day_price1_rangeV',
//             formControlId: 'day_price1_input'
//         },
//         {
//             inputId: 'day_price2_range',
//             outputId: 'day_price2_rangeV',
//             formControlId: 'day_price2_input'
//         },
//         {
//             inputId: 'time_day1_range',
//             outputId: 'time_day1_rangeV',
//             formControlId: 'time_day1_input'
//         },
//         {
//             inputId: 'time_day2_range',
//             outputId: 'time_day2_rangeV',
//             formControlId: 'time_day2_input'
//         }
//     ];
//
//     $.each(inputs, function(index, item) {
//         var range = document.getElementById(item.inputId);
//         var rangeV = document.getElementById(item.outputId);
//         var formControl = document.getElementById(item.formControlId);
//
//         var setValue = function() {
//             var newValue = Number((range.value - range.min) * 100 / (range.max - range.min));
//             var newPosition = 10 - (newValue * 0.2);
//             rangeV.innerHTML = '<span>' + range.value + '</span>';
//             rangeV.style.left = 'calc(' + newValue + '% + (' + newPosition + 'px))';
//
//             formControl.value = range.value;
//         };
//
//         $(document).ready(setValue);
//
//         $(range).on('input', setValue);
//     });
// });