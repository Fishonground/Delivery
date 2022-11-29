from multiprocessing.resource_sharer import stop
import os
import threading
import time
from uuid import uuid4
from producer import proceed_to_deliver


ordering = False
UNIC_NAME_MOTION = uuid4().__str__()
UNIC_NAME_CAMERA = uuid4().__str__()
UNIC_NAME_CENTRAL = uuid4().__str__()
UNIC_NAME_COMMUNICATION_IN = uuid4().__str__()
UNIC_NAME_COMMUNICATION_OUT = uuid4().__str__()
UNIC_NAME_GPS = uuid4().__str__()
UNIC_NAME_POSITION = uuid4().__str__()
UNIC_NAME_SENSORS = uuid4().__str__()
UNIC_NAME_MONITOR = uuid4().__str__()

confirmation_response = True
count_direction_request = True
count_direction_response = True
motion_start_request = True
stop_request = True
stop_response = True
pincoding_request = True
lock_opening_request = True
lock_closing_request = True
operation_status_response = True
activate_request = True
deactivate_request = True
gps_response = True
gps_request = True



def error_msg(id):
    err_details = {
        "id": id,
        "operation": "internal_error",
        "deliver_to": "monitor",
        "source": UNIC_NAME_MONITOR
    }
    proceed_to_deliver(id, err_details)

def set_names(id):
    comm_out_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "communication_out",
        "source": "",
        "name": UNIC_NAME_COMMUNICATION_OUT
    }
    proceed_to_deliver(id, comm_out_details)
    camera_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "camera",
        "source": "",
        "name": UNIC_NAME_CAMERA
    }
    proceed_to_deliver(id, camera_details)
    central_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "central",
        "source": "",
        "name": UNIC_NAME_CENTRAL
    }
    proceed_to_deliver(id, central_details)
    communication_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "communication_IN",
        "source": "",
        "name": UNIC_NAME_COMMUNICATION_IN
    }
    proceed_to_deliver(id, communication_details)
    gps_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "gps",
        "source": "",
        "name": UNIC_NAME_GPS
    }
    proceed_to_deliver(id, gps_details)
    motion_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "motion",
        "source": "",
        "name": UNIC_NAME_MOTION
    }
    proceed_to_deliver(id, motion_details)
    position_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "position",
        "source": "",
        "name": UNIC_NAME_POSITION
    }
    proceed_to_deliver(id, position_details)
    sensors_details = {
        "id": id,
        "operation": "set_name",
        "deliver_to": "sensors",
        "source": "",
        "name": UNIC_NAME_SENSORS
    }
    proceed_to_deliver(id, sensors_details)


def awaiting_response(id, operation, dst, start_time):
    global confirmation_response
    global count_direction_request
    global count_direction_response
    global motion_start_request
    global stop_request
    global stop_response
    global pincoding_request
    global lock_opening_request
    global lock_closing_request
    global operation_status_response
    global activate_request
    global deactivate_request
    global gps_response
    global gps_request


    if  operation == "confirmation":
        while not confirmation_response:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[confirmation] timeout exception!")
                break
    elif  operation == "count_direction" and dst == "position":
        while not count_direction_response:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[count_direction] timeout exception!")
                break
    elif  operation == "count_direction" and dst != "position":
        while not motion_start_request:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[count_direction_answer] timeout exception!")
                break
    elif  operation == "motion_start":
        while not stop_request:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 100:
                print(f"[motion_start] timeout exception!")
                break

    elif  operation == "stop" and dst == "position":
        while not stop_response:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[stop_response] timeout exception!")
                break
    elif  operation == "stop" and dst != "position":
        while not gps_request:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[gps_request] timeout exception!")
                break
    elif  operation == "pincoding":
        while not pincoding_request:
            time.sleep(0.2)
            now = time.time()
            #here we are waiting for a long years
            if (now - start_time) > 100:
                print(f"[lock_opening] timeout exception!")
                break
    elif  operation == "lock_opening":
        while not pincoding_request:
            time.sleep(0.2)
            now = time.time()
            #here we are waiting for a long years
            if (now - start_time) > 100:
                print(f"[lock_opening] timeout exception!")
                # details['id'] = id
                # details['deliver_to'] = 'position'
                # details['operation'] = 'count_direction'
                # details['source'] = UNIC_NAME_CENTRAL
                # details['x1'] = 0
                # details['y1'] = 0
                # proceed_to_deliver(id, details)   
                break
    elif  operation == "lock_closing":
        while not lock_opening_request:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[lock_closing] timeout exception!")
                break
    elif  operation == "deactivate":
        while (not lock_closing_request) and (not pincoding_request):
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[deactivate] timeout exception!")
                break
    elif  operation == "where_am_i":
        while not gps_response:
            time.sleep(0.2)
            now = time.time()
            if (now - start_time) > 10:
                print(f"[where_am_i] timeout exception!")
                break
        
        


def check_operation(id, details):
    global ordering
    global UNIC_NAME_MOTION
    global UNIC_NAME_CAMERA
    global UNIC_NAME_CENTRAL
    global UNIC_NAME_COMMUNICATION_IN
    global UNIC_NAME_COMMUNICATION_OUT
    global UNIC_NAME_GPS
    global UNIC_NAME_POSITION
    global UNIC_NAME_SENSORS
    global UNIC_NAME_MONITOR
    global confirmation_response
    global count_direction_request
    global count_direction_response
    global motion_start_request
    global stop_request
    global stop_response
    global pincoding_request
    global lock_opening_request
    global lock_closing_request
    global operation_status_response
    global activate_request
    global deactivate_request
    global gps_response
    global gps_request
    authorized = False
    # print(f"[debug] checking policies for event {id}, details: {details}")
    # print(f"[info] checking policies for event {id},"\
    #       f" {details['source']}->{details['deliver_to']}: {details['operation']}")

    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']
    
    if  src == 'communication_in' and dst == 'central' and operation == 'ordering':
        if type(details['pincode']) == str \
                and type(details['x1']) == int and type(details['y1']) == int \
                and abs(details['x1']) <= 200 and abs(details['y1']) <= 200  and len(details) == 7 :
            if not ordering:
                authorized = True
                ordering = True

                #
                #set names
                #
                set_names(id)
                #
                #
                #

                #
                #awaiting answer + antiddos
                #
                start_time = time.time()
                confirmation_response = False
                count_direction_request = False
                threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
                #
                #
                #

            else:
                e = {
                        'id':id,
                        'deliver_to': 'monitor',
                        'operation': 'reordering',
                        'source': 'monitor'
                    }
                proceed_to_deliver(id, e)  
                # details['source'] = UNIC_NAME_MONITOR
                # details['operation'] = 'reordering'
                # details['deliver_to'] = 'monitor'
                # proceed_to_deliver(id, details)
        else:
            details['source'] = UNIC_NAME_MONITOR
            details['operation'] = 'invalid_order'
            details['deliver_to'] = 'monitor'
            proceed_to_deliver(id, details)
    
    if src == UNIC_NAME_CENTRAL and dst == 'communication_out' \
        and operation == 'confirmation':
        #antiddos
        details['source'] = 'central'
        if not confirmation_response:
            confirmation_response = True
            authorized = True
        else:
            error_msg(id)    
    if src == UNIC_NAME_CENTRAL and dst == 'position' \
        and operation == 'count_direction':
        details['source'] = 'central'
        authorized = True
        start_time = time.time()
        count_direction_response = False
        threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()    

    if src == UNIC_NAME_POSITION and dst == 'central' \
        and operation == 'count_direction':
        
        if not count_direction_response:
            count_direction_response = True   
            details['source'] = 'position'
            authorized = True 
            start_time = time.time()
            motion_start_request = False
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
        else:
            error_msg(id)

    if src == UNIC_NAME_CENTRAL and dst == 'motion' \
        and operation == 'motion_start':    
        if not motion_start_request:
            motion_start_request = True
            details['source'] = 'central'
            authorized = True
            start_time = time.time()
            stop_request = False
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
        else:
            error_msg(id)    

    if src == UNIC_NAME_MOTION and dst == 'position' \
        and operation == 'motion_start':
        #and details['verified'] is True:
        details['source'] = 'motion'
        authorized = True    
    
    if src == UNIC_NAME_MOTION and dst == 'position' \
        and operation == 'stop':
        if not stop_request:
            stop_request = True
            details['source'] = 'motion'
            authorized = True
            start_time = time.time()
            stop_response = False
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()   
        else:
            error_msg(id) 
    if src == UNIC_NAME_POSITION and dst == 'central' \
        and operation == 'stop':
        if not stop_response:
            stop_response = True
            details['source'] = 'position'
            authorized = True
            start_time = time.time()
            gps_request = False
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
        else:
            error_msg(id)


    # here should understand that when hmi would be hardware, UNIC_NAME_HMI will be able to be, 
    # but now there are some software troubles to do it
    if src == 'hmi' and dst == 'central' \
        and operation == 'pincoding':
        #if not activate_request:
            #activate_request = True
        authorized = True
        start_time = time.time()
        pincoding_request = False
        threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()    
    if src == UNIC_NAME_CENTRAL and dst == 'sensors' \
        and operation == 'lock_opening':
        details['source'] = 'central'
        if not pincoding_request:
            try:
                files = os.listdir("/storage")
                #print (files)
                files = [file for file in files if "Picture_" in file]
                #print (files)
                file = max(files, key=lambda i: os.stat("/storage/"+i).st_mtime)
                #print(file)
                if (time.time() - os.stat("/storage/"+file).st_mtime) < 30:
                    print("Picture was founded!")
                    pincoding_request = True
                    authorized = True
                    lock_closing_request = False
                    start_time = time.time()
                    threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
                else:
                    error_msg(id)
                    count_direction_response = False
                    print('No picture founded!')
                    pincoding_request = True
                    m = {
                        'id':id,
                        'deliver_to': 'position',
                        'operation': 'count_direction',
                        'source': 'central',
                        'x1': 0,
                        'y1': 0
                    }
                    proceed_to_deliver(id, m)   
            except Exception as e:
                print(f"[error] failed to find picture: {e}")
        else:
            error_msg(id)
            
#     if src == 'sensors' and dst == 'central' \
#         and operation == 'lock_opening':
#         authorized = True
    if  src == UNIC_NAME_SENSORS and dst == 'central'\
        and operation == 'lock_closing':
        details['source'] = 'sensors'
        if not lock_closing_request:
            lock_closing_request = True
            authorized = True
            start_time = time.time()
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()   
        else:
            error_msg(id)
    if  src == UNIC_NAME_CENTRAL and dst == 'communication_out'\
        and operation == 'operation_status' and len(details) == 5:
        details['source'] = 'central'
        authorized = True
        ordering = False
    if  src == UNIC_NAME_CENTRAL and dst == 'camera'\
        and operation == 'activate':
        details['source'] = 'central'
        authorized = True
        activate_request = False
        start_time = time.time()
        threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()  
         
    if  src == UNIC_NAME_CENTRAL and dst == 'camera'\
        and operation == 'deactivate':
        if not lock_closing_request:
            lock_closing_request = True
            details['source'] = 'central'
            authorized = True
        elif not pincoding_request:
            pincoding_request = True
            details['source'] = 'central'
            authorized = True
        else:
            error_msg(id)
        

    if  src == UNIC_NAME_MONITOR and dst == 'monitor':
        details['source'] = 'monitor'
        authorized = True
    if  src == UNIC_NAME_CENTRAL and dst == 'monitor':
        details['source'] = 'central'
        authorized = True

    
    if  src == UNIC_NAME_CENTRAL and dst == 'gps'\
        and operation == 'where_am_i':
        if not gps_request:
            gps_request = True
            details['source'] = 'central'
            authorized = True
            start_time = time.time()
            gps_response = False
            threading.Thread(target=lambda: awaiting_response(id, operation, dst, start_time)).start()
        else:
            error_msg(id)
    #simple checking length of messages
    if  src == UNIC_NAME_GPS and dst == 'central'\
        and operation == 'gps' and len(details) == 6:
        if not gps_response:
            gps_response = True
            details['source'] = 'gps'
            authorized = True
        else:
            error_msg(id)
    if  src == UNIC_NAME_GPS and dst == 'central'\
        and operation == 'gps_error' and len(details) == 4:
        if not gps_response:
            gps_response = True
            details['source'] = 'gps'
            authorized = True
        else:
            error_msg(id)
    if  src == UNIC_NAME_POSITION and dst == 'gps'\
        and operation == 'nonexistent':
        details['source'] = 'position'
        authorized = True
        

    return authorized