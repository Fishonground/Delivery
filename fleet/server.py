#!/usr/bin/env python

import os
from urllib import response
from flask import Flask, make_response, send_file, abort, request, jsonify
import zipfile
from hashlib import sha256
port = 6004
app = Flask(__name__)




@app.route('/confirmation', methods=['POST'])
def get_confirmation():
    try:
        content = request.json
        print(f"[info] order sended with status {content}")
    except:
        return "error", 400
    return jsonify({"operation": "ordering confirmed", "status": content['status']})

@app.route('/status', methods=['POST'])
def get_ending():
    try:
        content = request.json
        print(f"[info] order delivered {content['status']}, rotot has been planted")
    except:
        return "error", 400
    return jsonify({"operation": "delivering confirmed", "status": content['status']})

if __name__ == "__main__":        # on running python app.py
    app.run(port=port, host="0.0.0.0")