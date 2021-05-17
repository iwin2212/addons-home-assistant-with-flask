
function key_search(key) {
    text_search = key.value;
    string = $('#message').val();
    var select_section = document.getElementById("selected_dev");
    var select_section_value = select_section.value;
    if (string.lastIndexOf('->') == string.length - 2) {
        string = string.substring(string.lastIndexOf('#') + 1, string.lastIndexOf('->'));
    }
    switch (string) {
        case 'sensor':
            dev = 'Cảm biến';
            break;
        case 'tv':
            dev = 'TV';
            break;
        case 'climate':
            dev = 'Điều hoà';
            break;
        case 'curtain':
            dev = 'Rèm';
            break;
        case 'switch':
            dev = 'Công tắc';
            break;
        case 'light':
            dev = 'Đèn';
            break;
        case 'lock':
            dev = 'Khoá';
            break;
    }
    entities = add_option(dev);
    var list_search_result = [];
    if (text_search != '') {
        entities.forEach(function (i) {
            if (i.search(text_search.toLowerCase()) != -1) {
                list_search_result.push(i);
            }
        });
        if (list_search_result.length != 0) {
            $(select_section).find('option').remove().end().append('<option disabled selected value="whatever"> -- Chọn 1 thiết bị -- </option>').val('whatever');
            for (var i = 0; i < list_search_result.length; i++) {
                if (select_section_value != list_search_result[i]) {
                    var
                        custom_option = document.createElement("option"); var t = document.createTextNode(list_search_result[i]);
                    custom_option.appendChild(t); select_section.appendChild(custom_option);
                }
            }
        }
        else {
            $(select_section).find('option').remove().end().append('<option selected disabled> Không tìm thấy thiết bị </option>').val('whatever');
        }
    }
    else {
        if (entities.length != 0) {
            $(select_section).find('option')
                .remove().end().append('<option disabled selected value="whatever"> -- Chọn 1 thiết bị -- </option>')
                .val('whatever')
                ;
            for (var i = 0; i < entities.length; i++) {
                if (select_section_value != entities[i]) {
                    var
                        custom_option = document.createElement("option"); var t = document.createTextNode(entities[i]);
                    custom_option.appendChild(t); select_section.appendChild(custom_option);
                }
            }
        }
    }
    var se = $("#selected_dev");
    se.show();
    se[0].size = 20;
}

function on_keyup(event, key) {
    var KeyID = event.keyCode;
    switch (KeyID) {
        case 8:
            key_search(key);
            break;
        case 46:
            key_search(key);
            break;
        default:
            break;
    }
}