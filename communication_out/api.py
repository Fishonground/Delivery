from hashlib import sha256
import hashlib
import multiprocessing
from time import sleep
import time
import uuid
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 6009

app = Flask(__name__)             # create an app instance
timestamp = 0

_requests_queue: multiprocessing.Queue = None

def hash_password(password):
    # uuid используется для генерации случайного числа
    salt = uuid.uuid4().hex
    return hashlib.sha256(salt.encode() + password.encode()).hexdigest() + ':' + salt

def validate_content(content):
    if abs(content['x']) > 100 or abs(content['y']) > 100 or len(content) != 3:
        return False
    return True


@app.route("/ordering", methods=['POST'])
def ordering():
    pass
    # content = request.json
    # try:
    #     global timestamp
    #     if (time.time() - timestamp) < 5:
    #         return "timeout", 504
    #     else:
    #         timestamp = time.time()
    #     auth = request.headers['auth']
    #     if auth != 'very-secure-token':
    #         return "unauthorized", 401
    # except:
    #     return "unauthorized", 401
    # req_id = uuid4().__str__()

    # try:
    #     if validate_content(content):
    #         #https://docs.python.org/3/library/hashlib.html
    #         #here it's only for demonstrating
    #         #obviously, hash should be sended from fleet
    #         #but fleet is emulated by request.rest, so...
    #         hashed_password = hash_password(str(content['pincode']))
    #         print('Password: ' + hashed_password)

    #         communication_details = {
    #             "id": req_id,
    #             "operation": "ordering",
    #             "deliver_to": "central",
    #             "source": "",
    #             #"pincode": sha256(content['pincode']).hexdigest(),
    #             "pincode": hashed_password,
    #             "x1": content['x'],
    #             "y1": content['y']
    #             }
    #         _requests_queue.put(communication_details)
    #         print(f"ordering event: {communication_details}")
    #         #sleep(10)
    #     else:
    #         error_message = f"bad request"
    #         return error_message, 400
    # except:
    #     error_message = f"malformed request {request.data}"
    #     print(error_message)
    #     return error_message, 400
    # return jsonify({"operation": "ordering requested", "id": req_id})

def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()