#!/usr/bin/env python

import os
from urllib import response
from flask import Flask, make_response, send_file, abort, request
import zipfile
from hashlib import sha256
port = 6004
app = Flask(__name__)




@app.route('/confirmation', methods=['POST'])
def get_confirmation():
    
    try:
        content = request.json
        print(f"[info] order sended with status {content['status']}")
        return "ok", 200    
    except:
        abort(404)

@app.route('/ending', methods=['POST'])
def get_ending():
    try:
        content = request.json
        print(f"[info] order delivered {content['status']}, rotot has been planted")
        return "ok", 200         
    except:
        abort(404)

if __name__ == "__main__":        # on running python app.py
    app.run(port=port, host="0.0.0.0")