# Python基础与应用

## Python文件服务器

!!! reference "参考文档"

    [Python http.server 搭建http服务器用于下载/上传文件](https://blog.csdn.net/Norths_/article/details/130728255)  
    [基于flask，简单的http文件服务器，提供文件下载服务、文件上传服务](https://blog.csdn.net/liliangkuba/article/details/124936999)

切换到存储文件的目录，使用如下命令启动一个服务器

```bash
python -m http.server
```

上传功能得用flask新建一个服务器

```py
# coding: utf-8
from flask import send_file, request
from gevent import pywsgi
from flask import Flask
import sys
import os
import time

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    file_obj = request.files.get("file")
    if file_obj is None:
        return "Upload Empty"
    
    path = os.path.join(os.getcwd(), "files/{}".format(file_obj.filename))
    print("[*] upload path: {}".format(path))
    file_obj.save(path)
    return "Upload Success"

@app.route("/download")
def download():
    file_name = request.args.get('file_name')
    path = os.path.join(os.getcwd(), "files/{}".format(file_name))
    return send_file(path)

if __name__ == "__main__":
    print("[*] server start")
    server = pywsgi.WSGIServer(('0.0.0.0', 8000), app)
    server.serve_forever()
```