var socket = io.connect('http://localhost:5000');

function login() {
    id = $("#id").val();
    password = $("#password").val();
    socket.emit('login', {"id": id, "password": password})
}

socket.on('response', function (msg) {
    console.log(msg);
    if ("login" in msg) {
        if ("success" in msg["login"] && msg["login"]["success"] === true) {
            if ("url" in msg["login"]) {
                document.location = msg["login"]["url"];
            }
        }
    }
    if ("logout" in msg) {
        if ("success" in msg["logout"] && msg["logout"]["success"] === true) {
            if ("url" in msg["logout"]) {
                document.location = msg["logout"]["url"];
            }
        }
    }
});


function logout() {
    socket.emit("logout");
}
