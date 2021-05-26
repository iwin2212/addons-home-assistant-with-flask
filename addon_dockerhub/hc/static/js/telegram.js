function save_telegram() {
    data = "?api_key="+document.getElementById("api_key").value+"&chat_id=" +document.getElementById("chat_id").value+"&user=" +document.getElementById("user").value +"&rpt=" + document.getElementById("rpt").value;
    $.post('./save_telegram' + data, function (data, status) {
        $("#restart").show();
    });
}
