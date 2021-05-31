function save_data() {
    client_id = document.getElementById("client_id").value;
    client_secret = document.getElementById("client_secret").value;
    sp_dc = document.getElementById("sp_dc").value;
    sp_key = document.getElementById("sp_key").value;

    if (client_id != '' && client_secret != '' && sp_dc != '' && sp_key != '') {
        data = "?client_id=" + client_id + "&client_secret=" + client_secret + "&sp_dc=" + sp_dc + "&sp_key=" + sp_key;
        $.post('./save_spotify_acc' + data, function (data, status) {
            $("#restart").show();
        });
    }
    else {
        alert('Bạn cần điền đầy đủ thông tin vào các ô trống trước khi bấm lưu lại.');
    }
}
