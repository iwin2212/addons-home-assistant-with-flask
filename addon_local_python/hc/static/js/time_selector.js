function get_number_of_days_on_janury() {
    try {
        year = new Date().getFullYear();
        select_section = document.getElementById('Date');
        select_section_value = select_section.value;
        if ((year - 2021) % 3 == 0) {
            entities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29];
            $(select_section)
                .find('option')
                .remove()
                .end();
            for (var i = 0; i < entities.length; i++) {
                if (select_section_value != entities[i]) {
                    var custom_option = document.createElement("option");
                    var t = document.createTextNode(entities[i]);
                    custom_option.appendChild(t);
                    select_section.appendChild(custom_option);
                }
            }
        }
        else {
            entities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28];
            $(select_section)
                .find('option')
                .remove()
                .end();
            for (var i = 0; i < entities.length; i++) {
                if (select_section_value != entities[i]) {
                    var custom_option = document.createElement("option");
                    var t = document.createTextNode(entities[i]);
                    custom_option.appendChild(t);
                    select_section.appendChild(custom_option);
                }
            }
        }
    }
    catch { }
}

function get_number_of_days(date) {
    try {
        year = new Date().getFullYear();
        select_section = document.getElementById('Date');
        select_section_value = select_section.value;
        if ((year - 2021) % 3 == 0) {
            entities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29];
            $(select_section)
                .find('option')
                .remove()
                .end();
            for (var i = 0; i < entities.length; i++) {
                if (select_section_value != entities[i]) {
                    var custom_option = document.createElement("option");
                    var t = document.createTextNode(entities[i]);
                    custom_option.appendChild(t);
                    select_section.appendChild(custom_option);
                }
            }
        }
        else {
            entities = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28];
            $(select_section)
                .find('option')
                .remove()
                .end();
            for (var i = 0; i < entities.length; i++) {
                if (select_section_value != entities[i]) {
                    var custom_option = document.createElement("option");
                    var t = document.createTextNode(entities[i]);
                    custom_option.appendChild(t);
                    select_section.appendChild(custom_option);
                }
            }
        }
        $('#Date').val(date);
    }
    catch { }
}

function month_onchange(field) {
    selected_option = field.value;
    switch (selected_option) {
        case 'January':
            get_number_of_days_on_janury();
            break;
        case 'February':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'March':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'April':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'May':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'Jun':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'July':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'August':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'September':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'October':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'November':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
        case 'December':
            number_of_days = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31];
            get_number_of_day_on_the_others(number_of_days);
            break;
    }
}

function get_number_of_day_on_the_others(number_of_days) {
    select_section = document.getElementById('Date');
    select_section_value = select_section.value;
    for (var i = 0; i < number_of_days.length; i++) {
        if (select_section_value != number_of_days[i]) {
            var custom_option = document.createElement("option");
            var t = document.createTextNode(number_of_days[i]);
            custom_option.appendChild(t);
            select_section.appendChild(custom_option);
        }
    }

}
