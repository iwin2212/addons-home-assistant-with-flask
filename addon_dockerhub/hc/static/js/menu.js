var i = document.getElementById("menu_right_click").style;

function show_menu() {
    if (document.addEventListener) {
        document.addEventListener('contextmenu', function (e) {
            var posX = e.clientX;
            var posY = e.clientY;
            menu(posX, posY);
            e.preventDefault();
        }, false);
    }
}

function click_menu() {
    document.addEventListener('click', function (e) {
        var posX = e.clientX;
        var posY = e.clientY;
        menu(posX, posY);
        e.preventDefault();
    }, false);
}

function close_menu() {
    document.addEventListener('click', function (e) {
        i.opacity = "0";
        i.visibility = "hidden";
        document.oncontextmenu = null;
    }, false);
}

function menu(x, y) {
    i.top = y + "px";
    i.left = x + "px";
    i.visibility = "visible";
    i.opacity = "1";
}
