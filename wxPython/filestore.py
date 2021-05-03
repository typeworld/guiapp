from flask import Flask, request, abort, Response
import threading
import socket
import urllib.parse
import typeworld.client
import os
import uuid
import time
import copy
import logging

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

from config import *

if WIN:
    prefFile = os.path.join(PREFDIR, "filestore.json")
    preferences = typeworld.client.JSON(prefFile)
elif MAC:
    preferences = typeworld.client.AppKitNSUserDefaults(
        "world.type.guiapp.filestore" if RUNTIME else "world.type.clientapp.filestore"
    )

app = Flask(__name__)

# Memory cache
memory_filestore = {}


def deleteFiles(urls):
    if urls:
        for url in urls:
            # Memory cache
            if url in memory_filestore:
                del memory_filestore[url]

            # File system
            fileDict = preferences.get(url) or {}
            if fileDict:
                filename = fileDict["filename"]
                path = os.path.join(FILEDIR, filename)
                if os.path.exists(path):
                    os.remove(path)
                preferences.remove(url)


@app.route("/file", methods=["GET"])
def file():
    url = urllib.parse.unquote(request.values.get("url"))

    fileDict = preferences.get(url) or {}

    # serve from memory
    if url in memory_filestore:
        print("serve from memory")
        return Response(
            memory_filestore[url]["content"],
            mimetype=memory_filestore[url]["content-type"],
        )

    # serve from file system
    elif fileDict:
        print("serve from file system")
        try:
            content = open(os.path.join(FILEDIR, fileDict["filename"]), "rb").read()
            # Memory cache
            memory_filestore[url] = copy.copy(fileDict)
            memory_filestore[url]["content"] = content
            return Response(content, mimetype=fileDict["content-type"])
        except FileNotFoundError:
            print("FileNotFoundError")
            pass  # Conintue below (fetch new)

    print("fetch from internet")
    success, response, responseObject = typeworld.client.request(url, method="GET")
    if success:

        # save into DB
        filename = str(uuid.uuid1())
        fileDict = {
            "filename": filename,
            "content-type": responseObject.headers["content-type"],
            "fetched": time.time(),
        }
        file = open(os.path.join(FILEDIR, filename), "wb")
        file.write(responseObject.content)
        file.close()
        preferences.set(url, fileDict)

        # Memory cache
        memory_filestore[url] = copy.copy(fileDict)
        memory_filestore[url]["content"] = responseObject.content

        return Response(
            responseObject.content, mimetype=responseObject.headers["content-type"]
        )
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
    kwargs={"host": "127.0.0.1", "port": PORT, "debug": False, "use_reloader": False},
    daemon=True,
)
server.start()
