function check_mxapi(){
    $.post('./check_mxapi', function (data, status) {
        if (data['logging'] == "Đã fix lỗi MXAPI")
            status = `<div id="status_div" class='text-success'>` + data['logging'] + `</div>`;
        else if (data['logging'] == "Lỗi token Home Assistant. Vui lòng kiểm tra lại!")
            status = `<div id="status_div" class='text-danger'>` + data['logging'] + `</div>`;
        else if (data['logging'] == "JAVIS HC hoạt động bình thường.")
            status = `<div id="status_div" class='text-danger'>` + data['logging'] + `</div>`;
        else if (data['logging'] == "Vui lòng đợi Home Assistant khởi động xong!")
            status = `<div id="status_div" class='text-danger'>` + data['logging'] + `</div>`;
        $("#status_div").replaceWith(status);
    });
}

function check_mxha(){
    $.post('./check_mxha', function (data, status) {
        if (data.logging == 'restart mxha')
            status = `<div id="status_div" class='text-success'>Đang khởi động lại dịch vụ kết nối đến cloud...</div>`;
        else
            status = `<div id="status_div" class='text-danger'>Đã có lỗi xảy ra. Vui lòng thử lại sau.</div>`;
        $("#status_div").replaceWith(status);
    });
}

function check_log(){
    $.post('./release_log', function (data, status) {
        status = `<div id="status_div" class='text-success'>Đã xoá log và giải phóng dung lượng</div>`;
        $("#status_div").replaceWith(status);
    });
}
