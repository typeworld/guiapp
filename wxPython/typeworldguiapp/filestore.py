from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

import threading
import socket
import urllib.parse
import typeworld.client
import os
import uuid
import time
import copy
import logging
import base64

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

from .config import *

if WIN:
    prefFile = os.path.join(PREFDIR, "filestore.json")
    preferences = typeworld.client.JSON(prefFile)
elif MAC:
    preferences = typeworld.client.AppKitNSUserDefaults(
        "world.type.guiapp.filestore" if RUNTIME else "world.type.clientapp.filestore"
    )


# Memory cache
memory_filestore = {}


def base64URL(url):
    fileDict = preferences.get(url) or {}

    # serve from memory
    if url in memory_filestore:
        content = memory_filestore[url]["content"]
        contentType = memory_filestore[url]["content-type"]
        b64 = "data:" + contentType + ";base64," + base64.b64encode(content).decode()
        return b64

    # serve from file system
    elif fileDict:
        content = open(os.path.join(FILEDIR, fileDict["filename"]), "rb").read()
        # Memory cache
        memory_filestore[url] = copy.copy(fileDict)
        memory_filestore[url]["content"] = content
        b64 = (
            "data:"
            + fileDict["content-type"]
            + ";base64,"
            + base64.b64encode(content).decode()
        )
        return b64

    return f"http://127.0.0.1:{PORT}/file?url={urllib.parse.quote_plus(url)}"


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


class S(BaseHTTPRequestHandler):
    def do_GET(self):

        query = urlparse(self.path).query
        query_components = dict(qc.split("=") for qc in query.split("&"))

        url = urllib.parse.unquote(query_components["url"])
        fileDict = preferences.get(url) or {}

        # serve from memory
        if url in memory_filestore:
            # print("serve from memory")
            self.send_response(200)
            self.send_header("Content-type", memory_filestore[url]["content-type"])
            self.end_headers()
            self.wfile.write(memory_filestore[url]["content"])

        # serve from file system
        elif fileDict:
            # print("serve from file system")
            try:
                content = open(os.path.join(FILEDIR, fileDict["filename"]), "rb").read()
                # Memory cache
                memory_filestore[url] = copy.copy(fileDict)
                memory_filestore[url]["content"] = content

                self.send_response(200)
                self.send_header("Content-type", fileDict["content-type"])
                self.end_headers()
                self.wfile.write(content)

            except FileNotFoundError:
                # print("FileNotFoundError")
                pass  # Conintue below (fetch new)

        # print("fetch from internet")
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

            self.send_response(200)
            self.send_header("Content-type", responseObject.headers["content-type"])
            self.end_headers()
            self.wfile.write(responseObject.content)


def port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


PORT = port()


server_address = ("127.0.0.1", PORT)
httpd = HTTPServer(server_address, S)
listenerThread = threading.Thread(target=httpd.serve_forever, daemon=True)
listenerThread.start()
