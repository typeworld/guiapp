from flask import Flask, request, abort, Response
import threading
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


PORT = 8099


server = threading.Thread(
    target=app.run,
    kwargs={"host": "0.0.0.0", "port": PORT, "debug": True, "use_reloader": False},
    daemon=True,
)
server.start()
