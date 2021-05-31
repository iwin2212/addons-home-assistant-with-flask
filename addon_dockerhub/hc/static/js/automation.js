
// -----------------------------------------------------------------------------------------------------------------------------------
// di chuyển các cụm của action, trigger, condition
// -----------------------------------------------------------------------------------------------------------------------------------
// trigger
function show_trigger_pos(dem) {
    position = $('#entity_trigger_' + dem).index() - 1;
    $('#entity_trigger_' + dem).css("background-color", "#A4E8D0");
}
function hide_trigger_pos(dem) {
    $('#entity_trigger_' + dem).css("background-color", "transparent");
}
// condition
function show_condition_pos(dem_condition) {
    position = $('#entity_condition_' + dem_condition).index() - 4;
    position = position - count_trigger_row;
    $('#entity_condition_' + dem_condition).css("background-color", "#A4E8D0");
}
function hide_condition_pos(dem_condition) {
    $('#entity_condition_' + dem_condition).css("background-color", "transparent");
}
// action
function show_action_pos(position, dem_action) {
    if (position > 0) {
        string = ``;
        string1 = `<tr id='add_change_pos_btn${dem_action}'><td><img src="/static/icon/up.png" onclick='moveUp(` + dem_action + `)' onclick='hide_change_pos_btn(` + dem_action + `)' class="img-fluid" alt="up" height="25" width="25"></td></tr>`;
        string2 = `<tr id='add_change_pos_btn${dem_action}'><td><img src="/static/icon/down.png" onclick='moveDown(` + dem_action + `)' onclick='hide_change_pos_btn(` + dem_action + `)' class="img-fluid" alt="down" height="25" width="25"></td></tr>`;
        head_tail_position(position, dem_action);
    }
}
function show_script_pos(position, dem_action) {
    string = `<tr id='add_change_pos_btn${dem_action}'><td>`;
    string1 = `<img src="/static/icon/up.png" onclick='moveUp(` + dem_action + `)' onclick='hide_change_pos_btn(` + dem_action + `)' class="img-fluid" alt="up" height="25" width="25">`;
    string2 = `<img src="/static/icon/down.png" onclick='moveDown(` + dem_action + `)' onclick='hide_change_pos_btn(` + dem_action + `)' class="img-fluid" alt="down" height="25" width="25">`;
    head_tail_position(position, dem_action);
}
function head_tail_position(position, dem_action) {
    if (position != 1) {
        string += string1;
    }

    if (position != max_action) {
        string += string2;
    }

    string = string + '</td></tr>';
    $('#add_change_pos_btn' + dem_action).replaceWith(string);
    $('#entity_action_id_' + dem_action).css("background-color", "#A4E8D0");
}
function hide_change_pos_btn(dem_action) {
    string = `<td id='func_${dem_action}'>
            <table>
                <tr>
                    <td>
                        <button id = 'delete_action_${dem_action}' type = "button" value = "Xóa" class = "btn btn-primary active" onclick = "deleteAction(${dem_action})">Xoá</button>
                    </td>
                </tr>
                <tr id='add_change_pos_btn${dem_action}'></tr>
            </table>
        </td>`;
    $('#func_' + dem_action).replaceWith(string);
    $('#entity_action_id_' + dem_action).css("background-color", "transparent");
}
// moved block
function moveUp(dem_action) {
    var row = $('#entity_action_id_' + dem_action).closest('tr');
    if ($('#entity_action_id_' + dem_action).index() != 1)
        row.prev().insertAfter(row);
}
function moveDown(dem_action) {
    var row = $('#entity_action_id_' + dem_action).closest('tr');
    if ($('#entity_action_id_' + dem_action).index() != max_action)
        row.next().insertBefore(row);
}
// -----------------------------------------------------------------------------------------------------------------------------------
// -----------------------------------------------------------------------------------------------------------------------------------


// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// trigger
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// add_trigger --------------> add_new_alarm_automation, add_alarm_automation
function add_trigger_alarm_automation(dem) {
    string = `
        <tr id='trigger_block_${dem}'>
            <td colspan="2">
                <table class='container-fluid table-borderless'>
                    <tr class= "entity_trigger_id_${dem}">
                        <td width="30%" id = "trigger_id_${dem}">Cảm biến</td>
                        <td width="70%">
                            <select name = 'trigger' class = 'form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id="trigger_${dem}" onchange = "loadTriggerContent(${dem})" required>
                                <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                                {%for i in list_entity_id%}
                                    {%if i.split(".")[0] not in ["automation", "alarm_control_panel"]%}
                                        {% if i.split(".")[0] in ["binary_sensor", "sensor"]%}
                                            <option>{{list_entity_name[loop.index - 1]}} ({{i}})</option>
                                        {%endif%}
                                    {%endif%}
                                {%endfor%}
                            </select>
                        </td>
                    </tr>
                    <tr id = 'tr_content_${dem}' class = "trigger"></tr>
                </table>
            </td>
            <td><button id = 'delete_${dem}' type = "button" class = "btn btn-primary active" onclick = "deleteTrigger(${dem})">Xoá</button></td>
        </tr>
        <tr class="add_trigger"></tr>
        `;
    return string;
}
// add_trigger --------------> edit_automation_tongquat, new_automation
function add_trigger_automation_tongquat(dem) {
    string = `
        <tr id='entity_trigger_${dem}' onmouseenter='show_trigger_pos(${dem})' onmouseleave='hide_trigger_pos(${dem})'>
            <td colspan='2'>
                <table class='container-fluid table-borderless'>
                    <tr id='selection_trigger${dem}'>
                        <td width="30%">Chọn loại thiết bị</td>
                        <td width="70%"><select class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id="device_trigger_${dem}" onchange ='filter_trigger(${dem})'>
                                        <option disabled selected value> -- Chọn loại thiết bị -- </option>
                                        <option value='sensor'>Cảm biến</option>
                                        <option value='switch'>Công tắc</option>
                                        <option value='light'>Đèn</option>
                                        <option value='climate'>Điều hoà</option>
                                        <option value='lock'>Khoá</option>
                                        <option value='fan'>Quạt</option>
                                        <option value='cover'>Rèm</option>
                                        <option value='media_player'>TV</option>
                        </select></td>
                    </tr>
                    <tr id = 'block_trigger_${dem}'>
                        <td id = "trigger_id_${dem}">Chọn thiết bị kích hoạt</td>
                        <td>
                            <select name = 'trigger' class = 'form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id="trigger_${dem}" onchange = "loadTriggerContent(${dem})">
                                <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                            </select>
                        </td>
                    </tr>
                    <tr id = 'tr_content_${dem}' class = "trigger"></tr>
                </table>
            </td>
            <td>
                <table>
                    <tr>
                        <td><button id = 'delete_${dem}' type = "button" value = "Xóa" class = "btn btn-primary" onclick = "deleteTrigger(${dem})">Xoá</button></td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr class = 'add_trigger'></tr>
        `;
    return string;
}
// filter_trigger --------------> edit_automation_tongquat, new_automation
function filter_trigger(dem) {
    $('#trigger_' + dem)
        .find('option')
        .remove()
        .end()
        .append('<option disabled selected value="whatever"> -- Chọn 1 thiết bị -- </option>')
        .val('whatever')
        ;
    var select_section = document.getElementById('trigger_' + dem);
    device = document.getElementById('device_trigger_' + dem);
    var device_selected = device.value;
    var entities = [];
    // edit_automation
    if (list_entitys[0].indexOf("(") != -1) {
        switch (device_selected) {
            case 'sensor':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'sensor' || list_entitys[i].split('.')[0].split('(')[1] == 'binary_sensor') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'media_player':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'media_player') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'climate':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'climate') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'cover':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'cover') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'switch':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'switch') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'light':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'light') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'lock':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].search('_lock') != -1 || list_entitys[i].search('_action') != -1) {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            default:
                $(select_section).selectpicker("refresh");
        }
    }
    // new_automation
    else {
        switch (device_selected) {
            case 'sensor':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'sensor' || list_entitys[i].split('.')[0] == 'binary_sensor') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'media_player':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'media_player') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'climate':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'climate') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'cover':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'cover') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'switch':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'switch') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'light':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'light') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'lock':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].search('_lock') != -1 || list_entitys[i].search('_action') != -1) {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            default:
                $(select_section).selectpicker("refresh");
        }
    }
    for (var i = 0; i < entities.length; i++) {
        var custom_option = document.createElement("option");
        var t = document.createTextNode(entities[i]);
        custom_option.appendChild(t);
        select_section.appendChild(custom_option);
        $(select_section).selectpicker("refresh");
    }
}
// loadTriggerContent --------------> edit_automation_tongquat, new_automation
function load_entity_id_type_automation(dem) {
    if (entity_id.split(".")[0] == "sensor") {
        if (entity_id.search('_action_user') != -1) {
            string = `
            <tr class = "trigger_content_${dem}" style="display: none;">
                <td>Chọn kiểu</td>
                <td>
                    <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                        <option value="Trạng thái">Trạng thái</option>
                    </select>
                </td>
            </tr >
            <tr class = "trigger_content_${dem}" style="display: none;">
                <td>Từ trạng thái</td>
                <td>
                    <select name = 'trigger_fromstate' class = 'form-control'>
                        <option disabled selected value> -- Chọn trạng thái -- </option>
                    </select>
                </td>
            </tr >
            <tr class = "trigger_content_${dem}">
                <td>Mã người dùng</td>
                <td>
                    <input type = "number" class = "form-control" name = 'trigger_tostate' required>
                </td>
            </tr>
            <tr class = "trigger_content_${dem}">
                <td>Thời gian chờ</td>
                <td><input type = "text" name = "trigger_time" class = "datepicker form-control" placeholder="00:00:00" value="00:00:00"></td>
            </tr>
            <tr id = 'tr_content_${dem}' class = "trigger"></tr>
            `;
        }
        else if (entity_id.search('_lock_action') != -1) {
            string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
                <tr class = "trigger_content_${dem}" style="display: none;">
                    <td>Từ trạng thái</td>
                    <td>
                        <select name = 'trigger_fromstate' class = 'form-control'>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                        </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Phương thức mở khoá</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='pairing'>Pairing</option>
                            <option value='password_unlock'>Password Unlock</option>
                            <option value='rfid_card_unlock'>RFID Card Unlock</option>
                            <option value='touch_unlock'>Touch Unlock</option>
                        </select>
                    </td>    
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ (giờ:phút:giây)</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
        }
        else {
            string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái" selected>Trạng thái</option>
                                <option value="So sánh">So sánh</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                        <select id="fromstate_${dem}" name = 'trigger_fromstate' onchange='show_reset_state(this)' class = 'form-control'>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option>On</option>
                            <option>Off</option>
                            <option>arm_partial_zones</option>
                            <option>emergency</option>
                            <option>arm_all_zones</option>
                            <option>disarm</option>
                            <option>left_single</option>
                            <option>middle_single</option>   
                            <option>right_single</option>
                            <option>left_double</option>  
                            <option>middle_double</option>
                            <option>right_double</option>
                            <option>single</option>   
                            <option>double</option>
                            <option>triple</option>  
                            <option>quadruple</option>
                            <option>long_release</option>
                            <option>click</option>
                            <option>1_single</option>
                            <option>2_single</option>
                            <option>3_single</option>
                            <option>1_double</option>
                            <option>2_double</option>
                            <option>3_double</option>
                        </select>
                    </td>
                    <td><input type="image" src="/static/icon/return.png" alt="return" id="return_fromstate_${dem}" onclick="reset_state(this)" style="display: none;" height="20" width="20"></td>                    
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select id="tostate_${dem}" name = 'trigger_tostate'  onchange='show_reset_state(this)' class = 'form-control'>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option>On</option>
                            <option>Off</option>
                            <option>arm_partial_zones</option>
                            <option>emergency</option>
                            <option>arm_all_zones</option>
                            <option>disarm</option>
                            <option>left_single</option>
                            <option>middle_single</option>   
                            <option>right_single</option>
                            <option>left_double</option>  
                            <option>middle_double</option>
                            <option>right_double</option>
                            <option>single</option>   
                            <option>double</option>
                            <option>triple</option>  
                            <option>quadruple</option>
                            <option>long_release</option>
                            <option>click</option>
                            <option>1_single</option>
                            <option>2_single</option>
                            <option>3_single</option>
                            <option>1_double</option>
                            <option>2_double</option>
                            <option>3_double</option>
                        </select>
                    </td>
                    <td><input type="image" src="/static/icon/return.png" alt="return" id="return_tostate_${dem}" onclick="reset_state(this)" style="display: none;" height="20" width="20"></td>                   
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ (giờ:phút:giây)</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
        }
    }
    else if (entity_id.split(".")[0] == "cover") {
        string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                        <select name = 'trigger_fromstate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='close_cover'>Đóng</option>
                            <option value='open_cover'>Mở</option>
                            <option value='stop_cover'>Dừng</option>
                        </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='close_cover'>Đóng</option>
                            <option value='open_cover'>Mở</option>
                            <option value='stop_cover'>Dừng</option>
                        </select>
                    </td>    
                    
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" placeholder="00:00:00" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
    }
    else if (entity_id.split(".")[0] == "lock") {
        string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = 'form-control' required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='lock'>Đóng</option>
                                <option value='unlock'>Mở</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='lock'>Đóng</option>
                            <option value='unlock'>Mở</option>
                        </select>
                    </td>
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" placeholder="00:00:00" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
    }
    else if (entity_id.search('door') != -1 || entity_id.search('contact') != -1) {
        string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái" selected>Trạng thái</option>
                                <option value="So sánh">So sánh</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = 'form-control' required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='On'>Mở</option>
                                <option value='Off'>Đóng</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='On'>Mở</option>
                            <option value='Off'>Đóng</option>
                        </select>
                    </td>   
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ (giờ:phút:giây)</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
    }
    else if (entity_id.split(".")[0] == "binary_sensor") {
        string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = "form-control">
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='on'>Có</option>
                                <option value='off'>Không</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control'>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='on'>Có</option>
                            <option value='off'>Không</option>
                        </select>
                    </td>    
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" placeholder="00:00:00" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
    }
    else {
        string = `
                <tr  class = "trigger_content_${dem}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = "form-control" required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='on'>Bật</option>
                                <option value='off'>Tắt</option>
                            </select>
                    </td>
                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='on'>Bật</option>
                            <option value='off'>Tắt</option>
                        </select>
                    </td>   
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" placeholder="00:00:00" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
    }
    return string;
}
// loadTriggerContent --------------> add_new_alarm_automation, add_alarm_automation
function load_entity_id_type_alarm(dem) {
    if (entityID.split("(")[1].split(".")[0] == "sensor") {
        string = `
            <tr  class = "trigger_content_${dem}">
                <td>Đến trạng thái</td>
                <td>
                    <select name = 'trigger_tostate' class = 'form-control' required>
                        <option disabled selected value> -- Chọn trạng thái -- </option>
                        <option>On</option>
                        <option>Off</option>
                    </select>
                </td>    
            </tr>
            <tr class = "trigger"></tr>
            `;
    } else {
        string = `
            <tr  class = "trigger_content_${dem}">
                <td>Đến trạng thái</td>
                <td>
                    <select name = 'trigger_tostate' class = 'form-control' required>
                        <option disabled selected value> -- Chọn trạng thái -- </option>
                        <option>On</option>
                        <option>Off</option>
                    </select>
                </td>    
            </tr>
            <tr class = "trigger"></tr>`;
    }
    return string;
}
// change_State ------------------> edit_automation_tongquat, new_automation
function change_State(obj, dem) {
    var state = obj.value;
    entity_id = $('#trigger_' + dem).val();
    entity_id = entity_id.split("(")[1].replace(")", "");
    if (state == "So sánh") {
        string = `
                    <tr  class = "trigger_content_${dem}">
                                
                        <td>Chọn kiểu</td>
                        <td>
                                <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                    <option value="So sánh" selected>So sánh</option>
                                    <option value="Trạng thái">Trạng thái</option>
                                    
                                </select>
                        </td>


                    </tr >
                    <tr class = "trigger_content_${dem}">
                        <td>Lớn hơn</td>
                        <td>
                            <input type = "number" class = "form-control" name = 'trigger_above'>
                        </td>

                    </tr>
                    <tr  class = "trigger_content_${dem}">
                        <td>Nhỏ hơn</td>
                        <td>
                            <input type = "number" class = "form-control" name = 'trigger_below'>
                        </td>

                    </tr>
                    <tr  class = "trigger_content_${dem}">
                        <td>Thời gian chờ (giờ:phút:giây)</td>
                        <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                    </tr>
                    <tr id = 'tr_content_${dem}' class = "trigger"></tr>
                `;
    } else {
        if (entity_id.search('door') != -1 || entity_id.search('contact') != -1) {
            string = `
                <tr  class = "trigger_content_${dem}">
                    
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái" selected>Trạng thái</option>
                                <option value="So sánh">So sánh</option>
                            </select>
                    </td>


                </tr >
        
                <tr  class = "trigger_content_${dem}">
            
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = 'form-control' required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='On'>Mở</option>
                                <option value='Off'>Đóng</option>
                            </select>
                    </td>


                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option value='On'>Mở</option>
                            <option value='Off'>Đóng</option>
                        </select>
                    </td>    
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ (giờ:phút:giây)</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
        }
        else {
            string = `
                <tr  class = "trigger_content_${dem}">
                    
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'trigger_state' class = 'form-control' onchange="change_State(this, ${dem})">
                                <option value="Trạng thái" selected>Trạng thái</option>
                                <option value="So sánh">So sánh</option>
                            </select>
                    </td>
                </tr >
        
                <tr  class = "trigger_content_${dem}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'trigger_fromstate' class = 'form-control' required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option>On</option>
                                <option>Off</option>
                                <option>arm_partial_zones</option>
                                <option>emergency</option>
                                <option>arm_all_zones</option>
                                <option>disarm</option>
                                <option>left_single</option>
                                <option>middle_single</option>   
                                <option>right_single</option>
                                <option>left_double</option>  
                                <option>middle_double</option>
                                <option>right_double</option>
                                <option>single</option>   
                                <option>double</option>
                                <option>triple</option>  
                                <option>quadruple</option>
                                <option>long_release</option>
                            </select>
                    </td>

                </tr >
                <tr  class = "trigger_content_${dem}">
                    <td>Đến trạng thái</td>
                    <td>
                        <select  name = 'trigger_tostate' class = 'form-control' required>
                            <option disabled selected value> -- Chọn trạng thái -- </option>
                            <option>On</option>
                            <option>Off</option>
                            <option>arm_partial_zones</option>
                            <option>emergency</option>
                            <option>arm_all_zones</option>
                            <option>disarm</option>
                            <option>left_single</option>
                            <option>middle_single</option>   
                            <option>right_single</option>
                            <option>left_double</option>  
                            <option>middle_double</option>
                            <option>right_double</option>
                            <option>single</option>   
                            <option>double</option>
                            <option>triple</option>  
                            <option>quadruple</option>
                            <option>long_release</option>
                        </select>
                    </td>    
                </tr>
                <tr  class = "trigger_content_${dem}">
                    <td>Thời gian chờ (giờ:phút:giây)</td>
                    <td><input type = "text" name = "trigger_time" class = "datepicker form-control" value="00:00:00"></td>
                </tr>
                <tr id = 'tr_content_${dem}' class = "trigger"></tr>`;
        }
    }
    $('.trigger_content_' + dem).remove();
    $(`#tr_content_${dem}`).replaceWith(string);
    formatTime();
}
// deleteTrigger ------------------> edit_automation_tongquat, new_automation
function delete_trigger_automation(dem) {
    count_trigger_row -= 1;
    $('#block_trigger_' + dem).remove();
    $('#trigger_' + dem).remove();
    $(`tr[class = 'trigger_content_${dem}']`).remove();
    $(`#trigger_id_` + dem).remove();
    $('#delete_' + dem).remove();
    $('#selection_trigger' + dem).remove();
    $('#entity_trigger_' + dem).remove();
}
// deleteTrigger ------------------> add_new_alarm_automation, add_alarm_automation
function delete_trigger_alarm(dem) {
    var res = confirm("Bạn chắc chắn muốn xóa ?");
    if (res == true) {
        $('#trigger_' + dem).remove();
        $('.trigger_id_' + dem).remove();
        $('.entity_trigger_id_' + dem).remove();
        $('.trigger_content_' + dem).remove();
        $('#trigger_block_' + dem).remove();
    }
}
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


// ...............................................................................................................
// condition
// ...............................................................................................................

// addCondition ------------------> edit_automation_tongquat, new_automation
function addCondition() {
    count_condition_rows += 1;
    string = `
    <tr id='entity_condition_${dem_condition}' onmouseenter='show_condition_pos(${dem_condition})' onmouseleave='hide_condition_pos(${dem_condition})'>
        <td colspan='2'>
            <table class='container-fluid table-borderless'>
                <tr id='selection_condition${dem_condition}'>
                    <td width="30%">Chọn loại thiết bị</td>
                    <td width="70%"><select class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id="device_condition_${dem_condition}" onchange ='filter_condition(${dem_condition})'>
                                    <option disabled selected value> -- Chọn loại thiết bị -- </option>
                                    <option value='sensor'>Cảm biến</option>
                                    <option value='switch'>Công tắc</option>
                                    <option value='light'>Đèn</option>
                                    <option value='climate'>Điều hoà</option>
                                    <option value='lock'>Khoá</option>
                                    <option value='fan'>Quạt</option>
                                    <option value='cover'>Rèm</option>
                                    <option value='media_player'>TV</option>
                    </select></td>
                </tr>
                <tr id = 'block_condition_${dem_condition}'>
                    <td id = "condition_id_${dem_condition}" >Chọn thiết bị</td>
                    <td>
                        <select name = 'condition' class = 'form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id = 'condition_${dem_condition}' onchange = 'loadConditionContent(${dem_condition})'>
                            <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                        </select>
                    </td>
                </tr>
                <tr id = "co_content_${dem_condition}" class = "condition"></tr>
            </table>
        </td>
        <td>
            <table>
                <tr>
                    <td><button id = 'delete_condition_${dem_condition}' type = "button" value = "Xóa" class = "btn btn-primary active" onclick = "deleteCondition(${dem_condition})">Xoá</button></td>
                </tr>
            </table>
        </td>
    </tr>
    <tr class = "add_condition"></tr>
    `;
    $('.add_condition').replaceWith(string);
    dem_condition++;
    $(function () {
        $('.selectpicker').selectpicker();
    });
}
// filter_condition ------------------> edit_automation_tongquat, new_automation
function filter_condition(dem_condition) {
    $('#condition_' + dem_condition)
        .find('option')
        .remove()
        .end()
        .append('<option disabled selected value="whatever"> -- Chọn 1 thiết bị -- </option>')
        .val('whatever')
        ;
    var select_section = document.getElementById('condition_' + dem_condition);
    device = document.getElementById('device_condition_' + dem_condition);
    var device_selected = device.value;
    var entities = [];
    // edit_automation
    if (list_entitys[0].indexOf('(') != -1) {
        switch (device_selected) {
            case 'sensor':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'sensor' || list_entitys[i].split('.')[0].split('(')[1] == 'binary_sensor') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'media_player':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'media_player') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'climate':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'climate') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'cover':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'cover') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'switch':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'switch') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'light':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'light') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            case 'lock':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0].split('(')[1] == 'lock') {
                        e = list_entitys[i];
                        entities.push(e);
                    }
                }
                break;
            default:
                $(select_section).selectpicker("refresh");
        }
    }
    // new_automation
    else {
        switch (device_selected) {
            case 'sensor':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'sensor' || list_entitys[i].split('.')[0] == 'binary_sensor') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'media_player':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'media_player') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'climate':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'climate') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'cover':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'cover') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'switch':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'switch') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'light':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'light') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            case 'lock':
                for (var i = 0; i < list_entitys.length; i++) {
                    if (list_entitys[i].split('.')[0] == 'lock') {
                        e = list_entity_name[i] + '(' + list_entitys[i] + ')';
                        entities.push(e);
                    }
                }
                break;
            default:
                $(select_section).selectpicker("refresh");
        }
    }
    for (var i = 0; i < entities.length; i++) {
        var custom_option = document.createElement("option");
        var t = document.createTextNode(entities[i]);
        custom_option.appendChild(t);
        select_section.appendChild(custom_option);
        $(select_section).selectpicker("refresh");
    }
}
// loadConditionContent ------------------> edit_automation_tongquat, new_automation
function loadConditionContent(dem_condition) {
    formatTime();
    entity_id = $('#condition_' + dem_condition).val();
    entity_id = entity_id.split("(")[1].replace(")", "");
    if (entity_id.split(".")[0] === 'sensor') {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                    <select name="chose_condition_state" class = 'form-control' onchange="change_State_Condition(this, ${dem_condition})">
                        <option value="Trạng thái" selected>Trạng thái</option>
                        <option value="So sánh">So sánh</option>
                        
                    </select>
            </td>
        </tr >
        <tr class = "condition_content_${dem_condition}">
            <td>Trạng thái</td>
            <td>
                <select name = 'condition_state' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option>On</option>
                    <option>Off</option>
                    <option>arm_partial_zones</option>
                    <option>emergency</option>
                    <option>arm_all_zones</option>
                    <option>disarm</option>
                    <option>left_single</option>
                    <option>middle_single</option>   
                    <option>right_single</option>
                    <option>left_double</option>  
                    <option>middle_double</option>
                    <option>right_double</option>
                    <option>single</option>   
                    <option>double</option>
                    <option>triple</option>  
                    <option>quadruple</option>
                    <option>long_release</option>
                </select>
            </td>    
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    }
    else if (entity_id.split(".")[0] === 'cover') {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                    <select name = 'chose_condition_state' class = 'form-control'>
                        <option value="Trạng thái">Trạng thái</option>
                    </select>
            </td>
        <tr class = "condition_content_${dem_condition}">
            <td>Trạng thái</td>
            <td>
                <select name = 'condition_state' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option value="open_cover">Mở rèm</option>
                    <option value="close_cover">Đóng rèm</option>
                    <option value="stop_cover">Dừng rèm</option>
                </select>
            </td>    
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    }
    else if (entity_id.split(".")[0] === 'lock') {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                    <select name = 'chose_condition_state' class = 'form-control'>
                        <option value="Trạng thái">Trạng thái</option>
                    </select>
            </td>
        <tr class = "condition_content_${dem_condition}">
            <td>Trạng thái</td>
            <td>
                <select name = 'condition_state' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option value="lock">Khoá</option>
                    <option value="unlock">Mở khoá</option>
                </select>
            </td>    
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    }
    else if (entity_id.search('door') != -1 || entity_id.search('contact') != -1) {
        string = `
                <tr  class = "chose_condition_state${dem_condition}">
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'chose_condition_state' class = 'form-control' onchange="change_State(this, ${dem_condition})">
                                <option value="Trạng thái" selected>Trạng thái</option>
                                <option value="So sánh">So sánh</option>
                            </select>
                    </td>
                </tr >
        
                <tr  class = "chose_condition_state${dem_condition}">
                    <td>Từ trạng thái</td>
                    <td>
                            <select name = 'condition_state' class = 'form-control' required>
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='On'>Mở</option>
                                <option value='Off'>Đóng</option>
                            </select>
                    </td>
                </tr >
                <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    }
    else if (entity_id.split(".")[0] == "binary_sensor") {
        string = `
                <tr class = "condition_content_${dem_condition}">
                    
                    <td>Chọn kiểu</td>
                    <td>
                            <select name = 'chose_condition_state' class = 'form-control' onchange="change_State(this, ${dem_condition})">
                                <option value="Trạng thái">Trạng thái</option>
                            </select>
                    </td>
                </tr >
        
                <tr  class = "condition_content_${dem_condition}">
                    <td>Trạng thái</td>
                    <td>
                            <select name = 'condition_state' class = "form-control">
                                <option disabled selected value> -- Chọn trạng thái -- </option>
                                <option value='on'>Có</option>
                                <option value='off'>Không</option>
                            </select>
                    </td>
                </tr >
                <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    }
    else {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                    <select name = 'chose_condition_state' class = 'form-control'>
                        <option value="Trạng thái">Trạng thái</option>
                    </select>
            </td>
        <tr class = "condition_content_${dem_condition}">
            <td>Trạng thái</td>
            <td>
                <select name = 'condition_state' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option>on</option>
                    <option>off</option>
                </select>
            </td>    
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;

    }
    $(`.condition_content_${dem_condition}`).remove();
    $(`#co_content_${dem_condition}`).replaceWith(string);
}
// change_State_Condition ------------------> edit_automation_tongquat, new_automation
function change_State_Condition(obj, dem_condition) {
    formatTime();
    var state = obj.value;
    entity_id = $('#condition_' + dem_condition).val();
    entity_id = entity_id.split("(")[1].replace(")", "");
    formatTime();
    if (state == "Trạng thái") {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                    <select name="chose_condition_state" class = 'form-control' onchange="change_State_Condition(this, ${dem_condition})">
                        <option value="Trạng thái" selected>Trạng thái</option>
                        <option value="So sánh">So sánh</option>
                        
                    </select>
            </td>
        </tr >
        <tr class = "condition_content_${dem_condition}">
            <td>Trạng thái</td>
            <td>
                <select name = 'condition_state' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option>on</option>
                    <option>off</option>
                    <option>arm_partial_zones</option>
                    <option>emergency</option>
                    <option>arm_all_zones</option>
                    <option>disarm</option>
                    <option>left_single</option>
                    <option>middle_single</option>   
                    <option>right_single</option>
                    <option>left_double</option>  
                    <option>middle_double</option>
                    <option>right_double</option>
                    <option>single</option>   
                    <option>double</option>
                    <option>triple</option>  
                    <option>quadruple</option>
                    <option>long_release</option>
                </select>
            </td>    
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;
    } else {
        string = `
        <tr  class = "condition_content_${dem_condition}">
                                
            <td>Chọn kiểu</td>
            <td>
                <select name = 'chose_condition_state' class = 'form-control' onchange="change_State_Condition(this, ${dem_condition})">
                    <option value="So sánh" selected>So sánh</option>
                    <option value="Trạng thái">Trạng thái</option>
                    
                </select>
            </td>


        </tr >        
        <tr class = "condition_content_${dem_condition}">
            <td>Lớn hơn</td>
            <td>
                <input type = "text" class = "form-control" name = 'above_condition'>
            </td>

        </tr>
        <tr  class = "condition_content_${dem_condition}">
            <td>Nhỏ hơn</td>
            <td>
                <input type = "text" class = "form-control" name = 'below_condition'>
            </td>
        </tr>
        <tr id = "co_content_${dem_condition}" class = "condition"></tr>`;

    }
    $(`.condition_content_${dem_condition}`).remove();
    $(`#co_content_${dem_condition}`).replaceWith(string);
}
// deleteCondition ------------------> edit_automation_tongquat, new_automation
function deleteCondition(dem_condition) {
    count_trigger_row -= 1;
    $('#block_condition_' + dem_condition).remove();
    $('#condition_' + dem_condition).remove();
    $(`tr[class = 'condition_content_${dem_condition}']`).remove();
    $(`#condition_id_` + dem_condition).remove();
    $('#delete_condition_' + dem_condition).remove();
    $('#selection_condition' + dem_condition).remove();
    $('#entity_condition_' + dem_condition).remove();
}
// ...............................................................................................................
// ...............................................................................................................


//===============================================================================================================
// action
//===============================================================================================================

// addAction ------------------> automation
function add_action_type_automation(dem_action) {
    string = `
        <tr id= "entity_action_id_${dem_action}" onmouseenter='show_change_pos_btn(${dem_action})' onmouseleave='hide_change_pos_btn(${dem_action})'>
            <td colspan='2'>
            <table class='container-fluid table-borderless'>
                <tr id = "block_action_${dem_action}">
                    <td>
                        Độ trễ (giờ:phút:giây)
                    </td>
                    <td>
                        <input type="text" value="00:00:00" name="delay" class="datepicker form-control"
                            autocomplete="off">
                    </td>
                </tr>
                <tr><td width="30%">Chọn hành động</td>
                    <td width="70%">
                        <select name='action' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" onchange ='addActionContent(${dem_action}, this)' id="hanhdong_${dem_action}">
                            <option disabled selected value> -- Chọn hành động -- </option>
                            <option value='alarm_control_panel.alarm_arm_away'>An ninh: Chế độ Vắng nhà</option>
                            <option value='alarm_control_panel.alarm_arm_home'>An ninh: Chế độ Ở nhà</option>
                            <option value='alarm_control_panel.alarm_arm_night'>An ninh: Chế độ Ban đêm</option>
                            <option value='alarm_control_panel.alarm_disarm'>An ninh: Tắt</option>
                            <option value='camera.snapshot'>Camera: Chụp ảnh</option>
                            <option value='camera.record'>Camera: Quay video</option>
                            <option value='switch.turn_on'>Công tắc: Bật</option>
                            <option value='switch.turn_off'>Công tắc: Tắt</option>
                            <option value='climate.turn_off'>Điều hoà: Tắt điều hoà</option>
                            <option value='climate.set_temperature'>Điều hoà: Bật nhiệt độ</option>
                            <option value='climate.set_fan_mode'>Điều hoà: Bật chế độ gió</option>
                            <option value='media_player.media_play_pause'>Điều khiển nhạc: Tạm dừng</option>
                            <option value='media_player.media_play'>Điều khiển nhạc: Tiếp tục</option>
                            <option value='media_player.media_stop'>Điều khiển nhạc: Dừng</option>
                            <option value='media_player.media_pause'>Điều khiển nhạc: Chơi tiếp</option>
                            <option value='media_player.volume_mute'>Điều khiển nhạc: Tắt tiếng</option>
                            <option value='media_player.volume_set'>Điều khiển nhạc: Thiết lập âm lượng</option>
                            <option value='media_player.volume_up'>Điều khiển nhạc: Tăng âm lượng</option>
                            <option value='media_player.volume_down'>Điều khiển nhạc: Giảm âm lượng</option>
                            <option value='light.turn_on'>Đèn: Bật</option>
                            <option value='light.turn_off'>Đèn: Tắt</option>
                            <option value='light.turn_on'>Đèn: Thiết lập độ sáng</option>
                            <option value='light.turn_on'>Đèn: Thiết lập màu</option>
                            <option value='light.turn_on'>Đèn: Thiết lập chế độ</option>
                            <option value='lock.unlock'>Khoá: Mở</option>
                            <option value='lock.lock'>Khoá: Đóng</option>
                            <option value='script.turn_on'>Kịch bản: Kích hoạt</option>
                            <option value='media_player.speak'>Phát giọng nói: Nhập nội dung Tiếng Việt</option>
                            <option value='fan.turn_on'>Quạt: Bật</option>
                            <option value='fan.turn_off'>Quạt: Tắt</option>
                            <option value='cover.open_cover'>Rèm: Mở</option>
                            <option value='cover.close_cover'>Rèm: Đóng</option>
                            <option value='cover.set_cover_position'>Rèm: Mở một phần</option>
                            <option value='cover.stop_cover'>Rèm: Tạm dừng</option>
                            <option value='media_player.turn_on'>TV: Bật</option>
                            <option value='media_player.turn_off'>TV: Tắt</option>
                            <option value='media_player.select_source'>TV: Chọn đầu vào</option>
                        </select>
                    </td>
                </tr>
                <tr id = "action${dem_action}"></tr>
                <tr id = "block_action_${dem_action}">
                    <td id='action_id_${dem_action}'>Chọn thiết bị thực hiện</td>
                    <td>
                        <select name='entity' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id='action_${dem_action}' required>
                            <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                        </select>
                    </td>
                </tr>
            </table></td>
            <td id='func_${dem_action}'>
                <table>
                    <tr>
                        <td>
                            <button id = 'delete_action_${dem_action}' type = "button" value = "Xóa" class = "btn btn-primary active" onclick = "deleteAction(${dem_action})">Xoá</button>
                        </td>
                    </tr>
                    <tr id='add_change_pos_btn${dem_action}'></tr>
                </table>
            </td>
        </tr>
        <tr class = "add_action"></tr>`;
    return string;
}
// addAction ------------------> alarm
function add_action_type_alarm(dem_action) {
    string = `<tr class= "entity_action_id_${dem_action}">
                    <td colspan='2'>
                    <table class='container-fluid table-borderless'><tr><td width="30%">Chọn hành động</td>
                    <td width="70%">
                        <select name='action' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" onchange ='addActionContent(${dem_action}, this)' id="hanhdong_${dem_action}">
                            <option disabled selected value> -- Chọn hành động -- </option>
                            <option value='switch.turn_on'>Công tắc: Bật</option>
                            <option value='switch.turn_off'>Công tắc: Tắt</option>
                            <option value='climate.turn_off'>Điều hoà: Tắt điều hoà</option>
                            <option value='climate.set_temperature'>Điều hoà: Bật nhiệt độ</option>
                            <option value='climate.set_fan_mode'>Điều hoà: Bật chế độ gió</option>
                            <option value='media_player.media_play_pause'>Điều khiển nhạc: Tạm dừng</option>
                            <option value='media_player.media_play'>Điều khiển nhạc: Tiếp tục</option>
                            <option value='media_player.media_stop'>Điều khiển nhạc: Dừng</option>
                            <option value='media_player.media_pause'>Điều khiển nhạc: Chơi tiếp</option>
                            <option value='media_player.volume_mute'>Điều khiển nhạc: Tắt tiếng</option>
                            <option value='media_player.volume_set'>Điều khiển nhạc: Thiết lập âm lượng</option>
                            <option value='media_player.volume_up'>Điều khiển nhạc: Tăng âm lượng</option>
                            <option value='media_player.volume_down'>Điều khiển nhạc: Giảm âm lượng</option>
                            <option value='light.turn_on'>Đèn: Bật</option>
                            <option value='light.turn_off'>Đèn: Tắt</option>
                            <option value='light.turn_on'>Đèn: Thiết lập độ sáng</option>
                            <option value='light.turn_on'>Đèn: Thiết lập màu</option>
                            <option value='light.turn_on'>Đèn: Thiết lập chế độ</option>
                            <option value='lock.unlock'>Khoá: Mở</option>
                            <option value='lock.lock'>Khoá: Đóng</option>
                            <option value='media_player.speak'>Phát giọng nói: Nhập nội dung Tiếng Việt</option>
                            <option value='fan.turn_on'>Quạt: Bật</option>
                            <option value='fan.turn_off'>Quạt: Tắt</option>
                            <option value='cover.open_cover'>Rèm: Mở</option>
                            <option value='cover.close_cover'>Rèm: Đóng</option>
                            <option value='cover.set_cover_position'>Rèm: Mở một phần</option>
                            <option value='cover.stop_cover'>Rèm: Tạm dừng</option>
                            <option value='media_player.turn_on'>TV: Bật</option>
                            <option value='media_player.turn_off'>TV: Tắt</option>
                            <option value='media_player.select_source'>TV: Chọn đầu vào</option>
                        </select>
                    </td>
                </tr>
                <tr class = "action${dem_action}"></tr>
                <tr id = "block_action_${dem_action}">
                    <td id='action_id_${dem_action}'>Chọn thiết bị thực hiện</td>
                    <td>
                        <select name='entity' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id='action_${dem_action}' required>
                            <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                        </select>
                    </td>
                </tr></table></td>
                <td><button id = 'delete_action_${dem_action}' type = "button" value = "Xóa" class = "btn btn-primary active" onclick = "deleteAction(${dem_action})">Xoá</button></td>
                </tr>
                <tr class = "add_action"></tr>`;
    return string;
}
// addAction ------------------> script
function add_action_type_script(dem_action) {
    string = `<tr id= "entity_action_id_${dem_action}" onmouseenter='show_change_pos_btn(${dem_action})' onmouseleave='hide_change_pos_btn(${dem_action})'>
            <td colspan='2'>
                <table id='block_${dem_action}' class='container-fluid table-borderless'>
                    <tr><td width="30%">Chọn hành động</td>
                        <td width="70%">
                            <select name='action' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" onchange ='addActionContent(${dem_action}, this)' id="hanhdong_${dem_action}">
                                <option disabled selected value> -- Chọn hành động -- </option>
                                <option value='switch.turn_on'>Công tắc: Bật</option>
                                <option value='switch.turn_off'>Công tắc: Tắt</option>
                                <option value='climate.turn_off'>Điều hoà: Tắt điều hoà</option>
                                <option value='climate.set_temperature'>Điều hoà: Bật nhiệt độ</option>
                                <option value='climate.set_fan_mode'>Điều hoà: Bật chế độ gió</option>
                                <option value='media_player.media_play_pause'>Điều khiển nhạc: Tạm dừng</option>
                                <option value='media_player.media_play'>Điều khiển nhạc: Tiếp tục</option>
                                <option value='media_player.media_stop'>Điều khiển nhạc: Dừng</option>
                                <option value='media_player.media_pause'>Điều khiển nhạc: Chơi tiếp</option>
                                <option value='media_player.volume_mute'>Điều khiển nhạc: Tắt tiếng</option>
                                <option value='media_player.volume_set'>Điều khiển nhạc: Thiết lập âm lượng</option>
                                <option value='media_player.volume_up'>Điều khiển nhạc: Tăng âm lượng</option>
                                <option value='media_player.volume_down'>Điều khiển nhạc: Giảm âm lượng</option>
                                <option value='light.turn_on'>Đèn: Bật</option>
                                <option value='light.turn_off'>Đèn: Tắt</option>
                                <option value='light.turn_on'>Đèn: Thiết lập độ sáng</option>
                                <option value='light.turn_on'>Đèn: Thiết lập màu</option>
                                <option value='light.turn_on'>Đèn: Thiết lập chế độ</option>
                                <option value='lock.unlock'>Khoá: Mở</option>
                                <option value='lock.lock'>Khoá: Đóng</option>
                                <option value='media_player.speak'>Phát giọng nói: Nhập nội dung Tiếng Việt</option>
                                <option value='fan.turn_on'>Quạt: Bật</option>
                                <option value='fan.turn_off'>Quạt: Tắt</option>
                                <option value='cover.open_cover'>Rèm: Mở</option>
                                <option value='cover.close_cover'>Rèm: Đóng</option>
                                <option value='cover.set_cover_position'>Rèm: Mở một phần</option>
                                <option value='cover.stop_cover'>Rèm: Tạm dừng</option>
                                <option value='media_player.turn_on'>TV: Bật</option>
                                <option value='media_player.turn_off'>TV: Tắt</option>
                                <option value='media_player.select_source'>TV: Chọn đầu vào</option>
                                <option value='delay'>Thời gian chờ</option>
                            </select>
                        </td>
                    </tr>
                    <tr id = "action${dem_action}"></tr>
                    <tr id = "block_action_${dem_action}">
                        <td id='action_id_${dem_action}'>Chọn thiết bị thực hiện</td>
                        <td>
                            <select name='entity' class='form-control selectpicker' data-dropup-auto="false" data-size="7" data-live-search="true" id='action_${dem_action}' onchange="changeService(${dem_action})" required>
                                <option disabled selected value> -- Chọn 1 thiết bị -- </option>
                            </select>
                        </td>
                    </tr>
                </table>
            </td>
            <td id='func_${dem_action}'>
                <table>
                    <tr>
                        <td>
                            <button id = 'delete_action_${dem_action}' type = "button" value = "Xóa" class = "btn btn-primary active" onclick = "deleteAction(${dem_action})">Xoá</button>
                        </td>
                    </tr>
                    <tr id='add_change_pos_btn${dem_action}'></tr>
                </table>
            </td>
        </tr>
        <tr class = "add_action"></tr>`;
    return string;
}
// addActionContent ------------------> automation, alarm, script, lock
function addActionContent_hanhdongValue_typeAutomation(dem_action, text_of_option) {
    if (hanhdong.value == 'climate.set_temperature') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td></td><td><table class='container-fluid '>
                    <tr><td>Chế độ</td>
                        <td name="mode"><select name = "mode" class='form-control'>
                            <option >cool</option>
                            <option >heat</option>
                        </td>
                    </tr>
                    <tr>
                        <td>Nhiệt độ</td>
                        <td name="temperature">
                            <select name = "temperature" class='form-control'>
                            <option >18</option>
                            <option >19</option>
                            <option >20</option>
                            <option >21</option>
                            <option >22</option>
                            <option >23</option>
                            <option selected>24</option>
                            <option >25</option>
                            <option >26</option>
                            <option >27</option>
                            <option >28</option>
                            <option >29</option>
                            <option >30</option>
                        </td>
                    </tr>
                </table></td>
            </tr>`;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'climate.set_fan_mode') {
        string2 = "<tr id = 'action" + dem_action + `'>
                    <td>Chế độ</td>
                    <td name="fan_mode"><select name = "fan_mode" class='form-control'>
                        <option >low</option>
                        <option >medium</option>
                        <option >high</option>
                        <option >auto</option>
                    </td>
                </tr>`;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.select_source') {
        string2 = "<tr id = 'action" + dem_action + `'>
            <td>Tên kênh</td>
            <td><input type = "text" class = 'form-control' name = 'source' value = "" placeholder = "Ví dụ: VTV1" requied></td>
        </tr>
        `;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.speak') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td >Lời nói</td>
                <td>
                    <input type = "text" value = "" name = "message" id = "speak_${dem_action}" class = "form-control" required/>    
                </td>    
            </tr>
            `;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.volume_set') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td >Chọn mức âm lượng</td>
                <td>
                    <input type = "number" name = "volume" id ="volume" min="0" max="100" placeholder='ví dụ: 50' class = "form-control"/>    
                </td>    
            </tr>
            `;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'light.turn_on') {
        if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập độ sáng') {
            string2 = "<tr id = 'action" + dem_action + `'>
                <td>Chọn độ sáng (%)</td>
                <td><input type = "number" name = "brightness_pct" min="0" max="100" placeholder="ví dụ: 35" id = "brightness_pct" class = "form-control"/></td>
                <td><input name = "brightness_pct_order" value='`+ dem_action + `' style="display: none;"/></td>
                </tr>`;
            $('#action' + dem_action).replaceWith(string2);
        }
        else if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập màu') {
            string2 = "<tr id = 'action" + dem_action + `'>
                <td>Chọn màu</td>
                <td><select name = "color" class = "form-control">
                <option value='white'>Màu trắng</option>
                <option value='red'>Màu đỏ</option>
                <option value='purple'>Màu tím</option>
                <option value='green'>Màu xanh lá cây</option>
                <option value='yellow'>Màu vàng</option>
                <option value='blue'>Màu xanh dương</option>
                <option value='aqua'>Màu xanh nước biển</option></select></td>
                <td><input name = "color_order" value='`+ dem_action + `' style="display: none;"/></td></tr>`;
            $('#action' + dem_action).replaceWith(string2);
        }
        else if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập chế độ') {
            string2 = "<tr id = 'action" + dem_action + `'>
                <td>Chọn chế độ</td>
                <td><select name = "profile" class = "form-control">
                <option value='energize'>Chế độ sinh nhật</option>
                <option value='relax'>Chế độ nghỉ ngơi</option>
                <option value='reading'>Chế độ nghe nhạc</option>
                <option value='concentrate'>Chế độ vui nhộn</option></select></td>
                <td><input name = "profile_order" value='`+ dem_action + `' style="display: none;"/></td></tr>`;
            $('#action' + dem_action).replaceWith(string2);
        }
        else {
            string2 = "<tr id = 'action" + dem_action + `'>`;
            $('#action' + dem_action).replaceWith(string2);
        }
    }
    else if ((hanhdong.value == 'lock.lock') || (hanhdong.value == 'lock.unlock')) {
        string2 = "<tr id = 'action" + dem_action + `'>
            <td>Mật khẩu</td>
            <td><input type = "text" class = 'form-control' name = 'lock_code' placeholder = "Ví dụ: 1234" requied></td>
        </tr>
        `;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'cover.set_cover_position') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td >Chọn % mở</td>
                <td>
                    <input type = "number" name = "pct_open" id ="pct_open" min="0" max="100" placeholder='ví dụ: 50' class = "form-control"/>    
                </td>    
            </tr>
            `;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value.split('.')[0] == 'alarm_control_panel') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td>Mã code</td>
                <td>
                    <input type = "text" class = 'form-control' name = 'alarm_code' placeholder = "Ví dụ: 1234" requied>
                </td>
            </tr>`;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'delay') {
        $('#action_' + dem_action).find('option').remove().end().append('<option selected value="whatever">delay</option>').val('whatever');
        $('#block_action_' + dem_action).hide();
        string2 = "<tr class = 'action" + dem_action + `'>
            <td >Chọn khoảng thời gian</td>
            <td>
                <input type="text" value="00:00:00" name="delay" class="datepicker form-control" autocomplete="off">
            </td>    
        </tr>
        `;
        $('.action' + dem_action).replaceWith(string2);
        $(submit).show();
        $('.datepicker').timepicker({
            controlType: 'select',
            oneLine: true,
            timeFormat: 'HH:mm:ss'
        });
    }
    else if (hanhdong.value == 'camera.record') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td>Thời lượng (giây)</td>
                <td>
                    <select class='form-control' id='duration_' ame='record_duration' requied>
                        <option >5</option>
                        <option >10</option>
                        <option >15</option>
                        <option >20</option>
                        <option >25</option>
                        <option >30</option>
                    </td>
                </td>
            </tr>`;
        $(function () {
            $("#duration_").change(function () {
                var max = parseInt($(this).attr('max'));
                var min = parseInt($(this).attr('min'));
                if ($(this).val() > max) {
                    $(this).val(max);
                }
                else if ($(this).val() < min) {
                    $(this).val(min);
                }
            });
        });
        $('#action' + dem_action).replaceWith(string2);
    }
    else {
        string2 = "<tr id = 'action" + dem_action + `'>`;
        $('#action' + dem_action).replaceWith(string2);
    }
}
function addActionContent_option_typeAutomation(entities, action_selected, select_section, exec_selected) {
    switch (action_selected) {
        case 'media_player':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'media_player') {
                    if (exec_selected == 'speak') {
                        if (list_entity_name[i].search('TV: ') == -1) {
                            entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                        }
                    }
                    else {
                        if (list_entity_name[i].search('TV: ') != -1) {
                            entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                        }
                    }
                }
            }
            break;
        case 'climate':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'climate') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'cover':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'cover') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'switch':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'switch') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'light':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'light') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'lock':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'lock') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'script':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'script') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'alarm_control_panel':
            entities.push('Home Alarm (alarm_control_panel.home_alarm)');
            break;
        case 'camera':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0] == 'camera') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        default:
            $(select_section).selectpicker("refresh");
    }
    return entities;
}
function addActionContent_option_typeAutomation2(entities, action_selected, select_section, exec_selected) {
    switch (action_selected) {
        case 'vacuum':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'vacuum') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'media_player':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'media_player') {
                    if (exec_selected == 'speak') {
                        if (list_entitys[i].search('TV: ') == -1) {
                            entities.push(list_entitys[i]);
                        }
                    }
                    else {
                        if (list_entitys[i].search('TV: ') != -1) {
                            entities.push(list_entitys[i]);
                        }
                    }
                }
            }
            break;
        case 'climate':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'climate') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'cover':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'cover') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'switch':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'switch') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'light':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'light') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'lock':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'lock') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'script':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'script') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'alarm_control_panel':
            entities.push('Home Alarm (alarm_control_panel.home_alarm)');
            break;
        case 'camera':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'camera') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        default:
            $(select_section).selectpicker("refresh");
    }
    return entities;
}
// deleteAction ------------------> automation, alarm, script, lock
function delete_action(dem_action) {
    var res = confirm("Bạn chắc chắn muốn xóa ?");
    if (res == true) {
        $('#delete_action_' + dem_action).remove();
        $('#action_' + dem_action).remove();
        $('#action' + dem_action).remove();
        $('#action' + dem_action).remove();
        $('#action_id_' + dem_action).remove();
        $(`.entity_action_id_` + dem_action).remove();
        $(`#entity_action_id_` + dem_action).remove();
        $(`#hanhdong_` + dem_action).remove();
        del_action = document.getElementById('del_act');
        del_action.value = del_action.value + dem_action;
    }
}
// change_device ------------------> automation, alarm, script, lock
function change_device(dem_action) {
    hanhdong = document.getElementById('hanhdong_' + dem_action);
    var action_selected = hanhdong.value.split('.')[0];
    var entities = [];
    var select_section = document.getElementById('action_' + dem_action);
    var select_section_value = select_section.value;
    switch (action_selected) {
        case 'media_player':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'media_player') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'climate':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'climate') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'cover':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'cover') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'switch':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'switch') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'light':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'light') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'lock':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'lock') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'script':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'script') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        case 'alarm_control_panel':
            entities.push('Home Alarm (alarm_control_panel.home_alarm)');
            break;
        case 'camera':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'camera') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        default:
            $(select_section).selectpicker("refresh");
    }

    if (entities.length != 0) {
        $(select_section)
            .find('option')
            .remove()
            .end()
            .append('<option selected value="' + select_section_value + '">' + select_section_value + '</option>')
            .val('whatever')
            ;
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
// changeActionContent ------------------> automation, alarm, script, lock
function changeActionContent(dem_action, text_of_option) {
    $('#block_action_' + dem_action).show();
    hanhdong = document.getElementById('hanhdong_' + dem_action);
    var idx_action = 'entity_action_id_' + dem_action;
    var action_selected = hanhdong.value.split('.')[0];
    var select_section = document.getElementById('action_' + dem_action);
    $('#action_' + (dem_action))
        .find('option')
        .remove()
        .end()
        .append('<option disabled selected value="whatever"> -- Chọn 1 thiết bị -- </option>')
        .val('whatever')
        ;
    var entities = [];

    if (hanhdong.value == 'climate.set_temperature') {
        string2 = "<tr class = 'action" + dem_action + `'>
                <td></td><td><table class='container-fluid '>
                    <tr><td>Chế độ</td>
                        <td name="mode"><select name = "mode" class='form-control'>
                            <option >cool</option>
                            <option >heat</option>
                        </td>
                    </tr>
                    <tr>
                        <td>Nhiệt độ</td>
                        <td name="temperature">
                            <select name = "temperature" class='form-control'>
                            <option >18</option>
                            <option >19</option>
                            <option >20</option>
                            <option >21</option>
                            <option >22</option>
                            <option >23</option>
                            <option selected>24</option>
                            <option >25</option>
                            <option >26</option>
                            <option >27</option>
                            <option >28</option>
                            <option >29</option>
                            <option >30</option>
                        </td>
                    </tr>
                </table></td>
            </tr>`;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'climate.set_fan_mode') {
        string2 = "<tr class = 'action" + dem_action + `'>
                    <td>Chế độ</td>
                    <td name="fan_mode"><select name = "fan_mode" class='form-control'>
                        <option >low</option>
                        <option >medium</option>
                        <option >high</option>
                        <option >auto</option>
                    </td>
                </tr>`;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.select_source') {
        string2 = "<tr class = 'action" + dem_action + `'>
            <td>Tên kênh</td>
            <td><input type = "text" class = 'form-control' name = 'source' value = "" placeholder = "Ví dụ: VTV1" requied></td>
        </tr>
        `;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.speak') {
        string2 = "<tr class = 'action" + dem_action + `'>
                <td >Lời nói</td>
                <td>
                    <input type = "text" value = "" name = "message" id = "speak_${dem_action}" class = "form-control" required/>    
                </td>    
            </tr>
            `;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'media_player.volume_set') {
        string2 = "<tr class = 'action" + dem_action + `'>
                <td >Chọn mức âm lượng</td>
                <td>
                    <input type = "number" name = "volume" id ="volume" min="0" max="100" placeholder='ví dụ: 50' class = "form-control"/>    
                </td>    
            </tr>
            `;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'light.turn_on') {
        if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập độ sáng') {
            string2 = "<tr class = 'action" + dem_action + `'>
                <td>Chọn độ sáng (%)</td>
                <td><input type = "number" name = "brightness_pct" min="0" max="100" placeholder="ví dụ: 35" id = "brightness_pct" class = "form-control"/></td>
                <td><input name = "brightness_pct_order" value='`+ dem_action + `' style="display: none;"/></td>
                </tr>`;
            $('.action' + dem_action).replaceWith(string2);
        }
        else if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập màu') {
            string2 = "<tr class = 'action" + dem_action + `'>
                <td>Chọn màu</td>
                <td><select name = "color" class = "form-control">
                <option value='white'>Màu trắng</option>
                <option value='red'>Màu đỏ</option>
                <option value='purple'>Màu tím</option>
                <option value='green'>Màu xanh lá cây</option>
                <option value='yellow'>Màu vàng</option>
                <option value='blue'>Màu xanh dương</option>
                <option value='aqua'>Màu xanh nước biển</option></td>
                <td><input name = "color_order" value='`+ dem_action + `' style="display: none;"/></td></tr>`;
            $('.action' + dem_action).replaceWith(string2);
        }
        else if (text_of_option.options[text_of_option.selectedIndex].text == 'Đèn: Thiết lập chế độ') {
            string2 = "<tr class = 'action" + dem_action + `'>
                <td>Chọn chế độ</td>
                <td><select name = "profile" class = "form-control">
                <option value='energize'>Chế độ sinh nhật</option>
                <option value='relax'>Chế độ nghỉ ngơi</option>
                <option value='reading'>Chế độ nghe nhạc</option>
                <option value='concentrate'>Chế độ vui nhộn</option></td>
                <td><input name = "profile_order" value='`+ dem_action + `' style="display: none;"/></td></tr>`;
            $('.action' + dem_action).replaceWith(string2);
        }
        else {
            string2 = "<tr class = 'action" + dem_action + `'>`;
            $('.action' + dem_action).replaceWith(string2);
        }
    }
    else if ((hanhdong.value == 'lock.lock') || (hanhdong.value == 'lock.unlock')) {
        string2 = "<tr class = 'action" + dem_action + `'>
            <td>Mật khẩu</td>
            <td><input type = "text" class = 'form-control' name = 'lock_code' placeholder = "Ví dụ: 1234" requied></td>
        </tr>
        `;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'cover.set_cover_position') {
        string2 = "<tr class = 'action" + dem_action + `'>
                <td >Chọn % mở</td>
                <td>
                    <input type = "number" name = "pct_open" id ="pct_open" min="0" max="100" placeholder='ví dụ: 50' class = "form-control"/>    
                </td>    
            </tr>
            `;
        $('.action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'delay') {
        $('#action_' + dem_action).find('option').remove().end().append('<option selected value="whatever">delay</option>').val('whatever');
        $('#block_action_' + dem_action).hide();
        string2 = "<tr class = 'action" + dem_action + `'>
                <td >Chọn khoảng thời gian</td>
                <td>
                    <input type="text" value="00:00:00" name="delay" class="datepicker form-control" autocomplete="off">
                </td>    
            </tr>
            `;
        $('.action' + dem_action).replaceWith(string2);
        $(submit).show();
        $('.datepicker').timepicker({
            controlType: 'select',
            oneLine: true,
            timeFormat: 'HH:mm:ss'
        });
    }
    else if (hanhdong.value.split('.')[0] == 'alarm_control_panel') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td>Mã code</td>
                <td>
                    <input type = "text" class = 'form-control' name = 'alarm_code' placeholder = "Ví dụ: 1234" requied>
                </td>
            </tr>`;
        $('#action' + dem_action).replaceWith(string2);
    }
    else if (hanhdong.value == 'camera.record') {
        string2 = "<tr id = 'action" + dem_action + `'>
                <td>Thời lượng (giây)</td>
                <td>
                    <input type="text" class='form-control' name='record_duration' placeholder="Ví dụ: 15" requied>
                </td>
            </tr>`;
        $('#action' + dem_action).replaceWith(string2);
    }
    else {
        string2 = "<tr class = 'action" + dem_action + `'>`;
        $('.action' + dem_action).replaceWith(string2);
    }
    switch (action_selected) {
        case 'media_player':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'media_player') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'climate':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'climate') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'cover':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'cover') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'switch':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'switch') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'light':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'light') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'lock':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('(')[1].split('.')[0] == 'lock') {
                    entities.push(list_entitys[i]);
                }
            }
            break;
        case 'alarm_control_panel':
            entities.push('Home Alarm (alarm_control_panel.home_alarm)');
            break;
        case 'camera':
            for (var i = 0; i < list_entitys.length; i++) {
                if (list_entitys[i].split('.')[0].split('(')[1] == 'camera') {
                    entities.push(list_entity_name[i] + ' (' + list_entitys[i] + ')');
                }
            }
            break;
        default:
            $(select_section).selectpicker("refresh");
    }
    for (var i = 0; i < entities.length; i++) {
        var custom_option = document.createElement("option");
        var t = document.createTextNode(entities[i]);
        custom_option.appendChild(t);
        select_section.appendChild(custom_option);
        $(select_section).selectpicker("refresh");
    }
}
//===============================================================================================================
//===============================================================================================================

function show_reset_state(entity) {
    state = entity.id.split('_')[0];
    idx = entity.id.split('_')[1];
    if (state == 'fromstate') {
        $('#return_fromstate_' + idx).show();
    }
    else if (state == 'tostate') {
        $('#return_tostate_' + idx).show();
    }
}


function reset_state(entity) {
    state = entity.id.split('_')[1];
    idx = entity.id.split('_')[2];
    if (state == 'fromstate') {
        $('#return_fromstate_' + idx).hide();
        string = `
                <select id="fromstate_`+ idx + `" name = 'trigger_fromstate' onchange='show_reset_state(this)' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option>On</option>
                    <option>Off</option>
                    <option>arm_partial_zones</option>
                    <option>emergency</option>
                    <option>arm_all_zones</option>
                    <option>disarm</option>
                    <option>left_single</option>
                    <option>middle_single</option>   
                    <option>right_single</option>
                    <option>left_double</option>  
                    <option>middle_double</option>
                    <option>right_double</option>
                    <option>single</option>   
                    <option>double</option>
                    <option>triple</option>  
                    <option>quadruple</option>
                    <option>long_release</option>
                    <option>click</option>
                    <option>1_single</option>
                    <option>2_single</option>
                    <option>3_single</option>
                    <option>1_double</option>
                    <option>2_double</option>
                    <option>3_double</option>
                </select>`;
        $('#fromstate_' + idx).replaceWith(string);
    }
    else if (state == 'tostate') {
        $('#return_tostate_' + idx).hide();
        string = `
                <select id="tostate_`+ idx + `" name = 'trigger_tostate' onchange='show_reset_state(this)' class = 'form-control'>
                    <option disabled selected value> -- Chọn trạng thái -- </option>
                    <option>On</option>
                    <option>Off</option>
                    <option>arm_partial_zones</option>
                    <option>emergency</option>
                    <option>arm_all_zones</option>
                    <option>disarm</option>
                    <option>left_single</option>
                    <option>middle_single</option>   
                    <option>right_single</option>
                    <option>left_double</option>  
                    <option>middle_double</option>
                    <option>right_double</option>
                    <option>single</option>   
                    <option>double</option>
                    <option>triple</option>  
                    <option>quadruple</option>
                    <option>long_release</option>
                    <option>click</option>
                    <option>1_single</option>
                    <option>2_single</option>
                    <option>3_single</option>
                    <option>1_double</option>
                    <option>2_double</option>
                    <option>3_double</option>
                </select>`;
        $('#tostate_' + idx).replaceWith(string);
    }
}