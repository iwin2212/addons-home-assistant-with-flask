function update() {
    $("#pending").show();
    $("#update_btn").hide();
    $.post('./get_update_ir', function (data, status) {
        response = data['response'];
        $("#pending").hide();
        if (response.search("Successfully updated") != -1) {
            note_div = `
            <div class="alert alert-success alert-dismissible fade show" id="note" role="alert" style="display: none;">
                Đã cập nhật phiên bản SmartIR `
                + response.split("to ")[1].split(". Please")[0] +
                ` đã sẵn sàng.
                Bạn vui lòng check config và khởi động lại hệ thống tại <a href="./homeassistant">đây</a>.
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            `;
            $("#note").replaceWith(note_div);
            $("#note").show();
            $("#update_div").hide();
            $("#update_btn").hide();
        }
        else {
            note_div = `
            <div class="alert alert-danger alert-dismissible fade show" id="note" role="alert" style="display: none;">
                Đã có lỗi xảy ra. vui lòng kiểm tra lại.<br>
                `+ data['response'] + `
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
            `;
            $("#note").replaceWith(note_div);
            $("#note").show();
            $("#update_div").hide();
            $("#update_btn").hide();
        }
    });
}
