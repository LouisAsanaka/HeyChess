let socket = io.connect('http://' + document.domain + ':' + location.port);
let username = null;
let sid = null;

socket.on('connect', function() {
    console.log("Connected!");
    sid = socket.id;
});

socket.on('set_username', function(data) {
    username = data;
    document.getElementById("username").childNodes[0].textContent = username;
});
