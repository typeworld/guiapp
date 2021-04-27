from flask import Flask, request, abort, Response
import threading
import socket
import urllib.parse
import typeworld.client

app = Flask(__name__)


@app.route("/file", methods=["GET"])
def file():
    url = urllib.parse.unquote(request.values.get("url"))
    success, response, responseObject = typeworld.client.request(url, method="GET")
    if success:
        content = responseObject.content
        return Response(content, mimetype=responseObject.headers["content-type"])
    else:
        return abort(500)


def port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


PORT = port()

server = threading.Thread(
    target=app.run,
    kwargs={"host": "0.0.0.0", "port": PORT, "debug": True, "use_reloader": False},
    daemon=True,
)
server.start()
