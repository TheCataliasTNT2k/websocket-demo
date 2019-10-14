from flask import Flask, send_from_directory, render_template, session, request, url_for
from flask_session import Session
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "SECRET"
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
sock = SocketIO(app, manage_session=False)


client_dict = {
    "1": "W",
    "2": "Ich BinEinAnderesPasswort"
}

socket_dict = {}


@sock.on("relay_message")
def relay_message(msg):
    if "client_id" in msg:
        client_id = msg["client_id"]
        if client_id in socket_dict:
            sid = socket_dict[client_id]
            sock.emit("relayed_message", msg, room=sid)
        else:
            sock.emit("relayed_message", {"Error": "Client offline"})
    elif "broadcast" in msg:
        sock.emit("relayed_message", msg, broadcast=True)
    else:
        sock.emit("relayed_message", {"Error": "No client ID"})


@sock.on("logout")
def logout():
    print(dict(session))
    if "client_id" in session:
        if session["client_id"] in socket_dict:
            del socket_dict["client_id"]
    session.clear()
    print(dict(session))
    sock.emit("response", {"logout": {"success": True, "url": url_for("get_login")}})


@sock.on("login")
def login(msg):
    print(dict(session))
    return_data: dict = {}
    client_id = msg.get("id")
    password = msg.get("password")
    if client_id in ["", None] or password in ["", None]:
        return_data = {"Error": "Missing credentials"}
    else:
        if client_id in client_dict:
            if client_id in socket_dict:
                return_data = {"Error": "Already logged in"}
            elif client_dict[client_id] == password:
                return_data = {"success": True, "url": url_for("client")}
                session["client_id"] = client_id
                socket_dict.update({client_id: request.sid})
                session.modified = True
            else:
                return_data = {"Error": "Invalid credentials"}
    print(dict(session))
    sock.emit("response", {"login": return_data})


@app.route("/login")
def get_login():
    print(dict(session))
    return render_template("client_login.html")


@app.route('/')
def hello_world():
    return render_template("index.html")


@app.route("/client")
def client():
    print(session.modified)
    print(dict(session))
    if "client_id" in session:
        client_id = session["client_id"]
        return render_template("client.html", client_id=client_id)
    else:
        return "You must login first: <a href='/login'>Login</a>"


@app.route("/admin")
def get_admin_page():
    return render_template("admin.html", client_dict=client_dict)


@app.route("/static/<string:filename>")
def get_static_file(filename):
    return send_from_directory('static', filename)


if __name__ == '__main__':
    #sock.async_mode = True
    sock.run(app=app, debug=True)
