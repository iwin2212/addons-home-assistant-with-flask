temperature_int = '25';
temp_string = ' độ';
humidity_int = '25';
humidity_string = 'gam trên mét khối';
illuminance_lux_int = '200';
illuminance_lux_string = ' lux';
occupancy_non_detected = 'không phát hiện chuyển động';
occupancy_detected = 'có chuyển động';
contact_open = 'đang mở';
contact_close = 'đã đóng';
dev_on = 'đang bật';
dev_off = 'đã tắt';
other_off = 'tắt';
other_on = 'bật';
other_null = 'không có trạng thái';


function get_text_to_example() {
    string = document.getElementById('template').value;
    list_replace_text = [];
    for (var i = 0; i < string.length; i++) {
        if (string[i] == "{") {
            start = i;
        }
        if (string[i] == "}") {
            end = i;
            if (string.substring(start, end).search('_temperature') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                list_replace_text.push(temperature_int);
            }
            else if (string.substring(start, end).search('_humidity') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                list_replace_text.push(humidity_int);
            }
            else if (string.substring(start, end).search('_illuminance_lux') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                list_replace_text.push(humidity_int);
            }
            else if (string.substring(start, end).search('_occupancy') != -1) {
                entity = string.substring(start, end + 67);
                list_replace_text.push(entity);
                list_replace_text.push('<' + occupancy_detected + '/' + occupancy_non_detected + '>');
            }
            else if (string.substring(start, end).search('_contact') != -1) {
                entity = string.substring(start, end + 32);
                list_replace_text.push(entity);
                list_replace_text.push('<' + contact_open + '/' + contact_close + '>');
            }
            else if ((string.substring(start, end).search('switch.') != -1) || (string.substring(start, end).search('light.') != -1) || (string.substring(start, end).search('climate.') != -1)) {
                if ((string.substring(start, end).search("else") == -1) && (string.substring(start, end).search("endif") == -1) && (string.substring(start, end).search("elif") == -1)) {
                    entity = string.substring(start + 14, end - 13);
                    entity = "\{\% if states('" + entity + "') == 'off' \%\} " + dev_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + dev_on + " \{\% else \%\} states('" + entity + "') \{\% endif \%\}";
                    list_replace_text.push(entity);
                    list_replace_text.push("<" + dev_on + "/" + dev_off + ">");
                }
            }
            else {
                if ((string.substring(start, end).search("else") == -1) && (string.substring(start, end).search("endif") == -1) && (string.substring(start, end).search("elif") == -1)) {
                    entity = string.substring(start + 14, end - 13);
                    list_entitys.forEach(function (k) {
                        if (k.search(entity) != -1) {
                            name_entity = k.split(" (")[0];
                        }
                    });
                    entity = "\{\% if states('" + entity + "') == 'off' \%\} " + other_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + other_on + " \{\% else \%\} " + other_null + " \{\% endif \%\}";
                    list_replace_text.push(entity);
                    list_replace_text.push("<" + name_entity + ">");
                }
            }
        }
    }
    for (var i = 0; i < list_replace_text.length; i += 2) {
        string = string.replace(list_replace_text[i], list_replace_text[i + 1]);
    }
    document.getElementById('example').value = string;
}

function get_dev2text(entity) {
    close_modal();
    entity_id = entity.value.split(' (')[1].split(')')[0];
    message = $('#message').val();
    string = message.substring(0, message.lastIndexOf('#'));
    string = string + '\<' + entity_id + '\>';
    document.getElementById('message').value = string;
    document.getElementById('message').focus();
    get_text_to_template();
}

function get_text_to_template() {
    string = document.getElementById('message').value;
    list_replace_text = [];
    for (var i = 0; i < string.length; i++) {
        if (string[i] == '<') {
            start = i + 1;
        }
        if (string[i] == '>') {
            end = i;
            entity = string.substring(start, end);
            list_replace_text.push("<" + entity + '>');
            list_replace_text.push(specific_entity(entity));
        }
    }
    for (var i = 0; i < list_replace_text.length; i += 2) {
        string = string.replace(list_replace_text[i], list_replace_text[i + 1]);
    }
    document.getElementById('template').value = string;
    get_text_to_example();
}

function specific_entity(entity) {
    if ((entity.search('_temperature') != -1)) {
        entity = "\{\{ states('" + entity + "' | int ) \}\}" + temp_string;
    }
    else if (entity.search('_humidity') != -1) {
        entity = "\{\{ states('" + entity + "' | int ) \}\}" + humidity_string;
    }
    else if (entity.search('_illuminance_lux') != -1) {
        entity = "\{\{ states('" + entity + "' | int ) \}\}" + illuminance_lux_string;
    }
    else if (entity.search('_occupancy') != -1) {
        entity = "\{\% if states('" + entity + "') == 'off' \%\} " + occupancy_non_detected + " \{\% else \%\} " + occupancy_detected + " \{\% endif \%\}";
    }
    else if (entity.search('_contact') != -1) {
        entity = "\{\% if states('" + entity + "') == 'off' \%\} " + contact_close + " \{\% else \%\} " + contact_open + " \{\% endif \%\}";
    }
    else if (entity.search('switch.') != -1) {
        entity = "\{\% if states('" + entity + "') == 'off' \%\} " + dev_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + dev_on + " \{\% else \%\} states('" + entity + "') \{\% endif \%\}";
    }
    else {
        entity = "\{\% if states('" + entity + "') == 'off' \%\} " + other_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + other_on + " \{\% else \%\} " + other_null + " \{\% endif \%\}";
    }
    return entity;
}

function get_text_2_message() {
    string = document.getElementById('template').value;
    list_replace_text = [];
    for (var i = 0; i < string.length; i++) {
        if (string[i] == "{") {
            start = i;
        }
        if (string[i] == "}") {
            end = i;
            i++;
            if (string.substring(start, end).search('_temperature') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                entity = entity.split("('")[1].split("' ")[0];
                list_entitys.forEach(function (k) {
                    if (k.search(entity) != -1) {
                        name_entity = k.split(" (")[0];
                    }
                });
                list_replace_text.push("<" + name_entity + ">");
            }
            else if (string.substring(start, end).search('_humidity') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                entity = entity.split("('")[1].split("' ")[0];
                list_entitys.forEach(function (k) {
                    if (k.search(entity) != -1) {
                        name_entity = k.split(" (")[0];
                    }
                });
                list_replace_text.push("<" + name_entity + ">");
            }
            else if (string.substring(start, end).search('_illuminance_lux') != -1) {
                entity = string.substring(start - 1, end + 2);
                list_replace_text.push(entity);
                entity = entity.split("('")[1].split("' ")[0];
                list_entitys.forEach(function (k) {
                    if (k.search(entity) != -1) {
                        name_entity = k.split(" (")[0];
                    }
                });
                list_replace_text.push("<" + name_entity + ">");
            }
            else if (string.substring(start, end).search('_occupancy') != -1) {
                entity = string.substring(start, end + 67);
                list_replace_text.push(entity);
                entity = entity.split("('")[1].split("')")[0];
                list_entitys.forEach(function (k) {
                    if (k.search(entity) != -1) {
                        name_entity = k.split(" (")[0];
                    }
                });
                list_replace_text.push("<" + name_entity + ">");
            }
            else if (string.substring(start, end).search('_contact') != -1) {
                entity = string.substring(start, end + 32);
                list_replace_text.push(entity);
                entity = entity.split("('")[1].split("')")[0];
                list_entitys.forEach(function (k) {
                    if (k.search(entity) != -1) {
                        name_entity = k.split(" (")[0];
                    }
                });
                list_replace_text.push("<" + name_entity + ">");
            }
            else if ((string.substring(start, end).search('switch.') != -1) || (string.substring(start, end).search('light.') != -1) || (string.substring(start, end).search('climate.') != -1)) {
                if ((string.substring(start, end).search("else") == -1) && (string.substring(start, end).search("endif") == -1) && (string.substring(start, end).search("elif") == -1)) {
                    entity = string.substring(start + 14, end - 13);
                    list_entitys.forEach(function (k) {
                        if (k.search(entity) != -1) {
                            name_entity = k.split(" (")[0];
                        }
                    });
                    entity = "\{\% if states('" + entity + "') == 'off' \%\} " + dev_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + dev_on + " \{\% else \%\} states('" + entity + "') \{\% endif \%\}";
                    list_replace_text.push(entity);
                    list_replace_text.push("<" + name_entity + ">");
                }
            }
            else {
                if ((string.substring(start, end).search("else") == -1) && (string.substring(start, end).search("endif") == -1) && (string.substring(start, end).search("elif") == -1)) {
                    entity = string.substring(start + 14, end - 13);
                    list_entitys.forEach(function (k) {
                        if (k.search(entity) != -1) {
                            name_entity = k.split(" (")[0];
                        }
                    });
                    entity = "\{\% if states('" + entity + "') == 'off' \%\} " + other_off + " \{\% elif states('" + entity + "') == 'on' \%\} " + other_on + " \{\% else \%\} " + other_null + " \{\% endif \%\}";
                    list_replace_text.push(entity);
                    list_replace_text.push("<" + name_entity + ">");
                }
            }
        }
    }
    for (var i = 0; i < list_replace_text.length; i += 2) {
        string = string.replace(list_replace_text[i], list_replace_text[i + 1]);
    }
    document.getElementById('message').value = string;
}