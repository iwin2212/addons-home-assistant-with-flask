
// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks on the button, open the modal
function open_modal() {
    $('#myModal').show();
};

// When the user clicks on <span> (x), close the modal
function close_modal() {
    $('#myModal').hide();
};

// When the user clicks anywhere outside of the modal, close it
// window.onclick = function (event) {
//     if (event.target == modal) {
//         modal.style.display = "none";
//     }
// };