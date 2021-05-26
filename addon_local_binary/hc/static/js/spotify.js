function save_data() {
    data = "?client_id="+document.getElementById("client_id").value+"&client_secret=" +document.getElementById("client_secret").value+"&sp_dc=" +document.getElementById("sp_dc").value +"&sp_key=" + document.getElementById("sp_key").value;
    $.post('./save_spotify_acc' + data, function (data, status) {
        $("#restart").show();
    });
}
