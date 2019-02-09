// Variables that are accessible in any script
let socket = null;
let username = null;
let sid = null;

function setupConnection() {
    socket = io.connect(document.domain + ':' + location.port);

    socket.on('connect', function() {
        console.log("Connected!");
        sid = socket.id;
    });

    socket.on('set_username', function(data) {
        username = data;
        document.getElementById("username").childNodes[0].textContent = username;
    });
}

$(document).ready(setupConnection);
