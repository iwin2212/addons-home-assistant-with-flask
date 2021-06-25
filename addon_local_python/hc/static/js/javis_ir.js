function show_info_table() {
    $("#info_table").show();
    $("#add_device").hide();
}

function connect_javis_ir(en) {
    $("#error").hide();
    ip_addr = en.parentNode.parentNode.children[1].children[0].value;
    if (checkIsIPV4(ip_addr)) {
        $("#pending").show();
        $("#" + en.id).hide();
        $.post('./add_javis_ir?ip=' + ip_addr, function (data, status) {
            if (!(data.result['error'] == undefined)){
                if (data.result.error.search("Failed to establish a new connection")!=-1)
                    $("#error_text")[0].innerText = "Không thể kết nối đến địa chỉ IP này."
                else
                    $("#error_text")[0].innerText = "Đã có lỗi xảy ra. Vui lòng thử lại sau.";
                $("#error").show();
                $("#pending").hide();
                $("#" + en.id).show();
            }
            else{
                window.location.reload();
                $("#pending").hide();
                $("#" + en.id).show();
                $("#info_table").hide();
                $("#add_device").show();
            }
        });
    }
    else{
        $("#error_text")[0].innerText = "Địa chỉ IP được nhập bị sai cú pháp.";
        $("#error").show();
    }
}

function hide_error(){
    $("#error").hide();
}

function delete_dev(en){
    $.post('./delete_javis_ir?netid=' + en, function (data, status) {
        console.log(data.error)
        if (data.error == true){
            $('#delete_error').show();
        }
        else {
            window.location.reload();
        }
    });
}
