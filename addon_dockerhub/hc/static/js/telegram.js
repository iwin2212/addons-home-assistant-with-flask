function save_telegram() {
    api_key = document.getElementById("api_key").value;
    chat_id = document.getElementById("chat_id").value;
    user = document.getElementById("user").value;
    rpt =  document.getElementById("rpt").value;
    if (api_key != '' && chat_id != '' && user != '' && rpt != '' ){
        data = "?api_key="+api_key+"&chat_id=" +chat_id+"&user=" +user +"&rpt=" + rpt;
        $.post('./save_telegram' + data, function (data, status) {
            $("#restart").show();
        });
    }
    else{
        alert('Bạn cần điền đầy đủ thông tin vào các ô trống trước khi bấm lưu lại.')
    }
}
