from producer import proceed_to_deliver


ordering = False

def check_operation(id, details):
    global ordering
    authorized = False
    # print(f"[debug] checking policies for event {id}, details: {details}")
    print(f"[info] checking policies for event {id},"\
          f" {details['source']}->{details['deliver_to']}: {details['operation']}")
    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']
    
    if  src == 'communication' and dst == 'central' and operation == 'ordering':
        if type(details['pincode']) == str \
                and type(details['x1']) == int and type(details['y1']) == int \
                and abs(details['x1']) <= 100 and abs(details['y1']) <= 100  and len(details) == 7 :
            if not ordering:
                authorized = True
                ordering = True
            else:
                details['source'] = 'monitor'
                details['operation'] = 'reordering'
                details['deliver_to'] = 'monitor'
                proceed_to_deliver(id, details)
        else:
            details['source'] = 'monitor'
            details['operation'] = 'invalid_order'
            details['deliver_to'] = 'monitor'
            proceed_to_deliver(id, details)

    if src == 'central' and dst == 'communication' \
        and operation == 'confirmation':
        authorized = True    
    if src == 'central' and dst == 'position' \
        and operation == 'count_direction':
        authorized = True    
    if src == 'position' and dst == 'central' \
        and operation == 'count_direction':
        authorized = True    
    if src == 'central' and dst == 'motion' \
        and operation == 'motion_start':
        authorized = True    
    if src == 'motion' and dst == 'position' \
        and operation == 'motion_start':
        #and details['verified'] is True:
        authorized = True    
    if src == 'motion' and dst == 'position' \
        and operation == 'stop':
        authorized = True    
    if src == 'position' and dst == 'central' \
        and operation == 'stop':
        authorized = True
    if src == 'hmi' and dst == 'central' \
        and operation == 'pincoding':
        authorized = True    
    if src == 'central' and dst == 'sensors' \
        and operation == 'lock_opening':
        authorized = True
#     if src == 'sensors' and dst == 'central' \
#         and operation == 'lock_opening':
#         authorized = True
    if  src == 'sensors' and dst == 'central'\
        and operation == 'lock_closing':
        authorized = True
    if  src == 'central' and dst == 'communication'\
        and operation == 'operation_status' and len(details) == 5:
        authorized = True
        ordering = False
    if  src == 'central' and dst == 'camera'\
        and operation == 'activate':
        authorized = True
    if  src == 'central' and dst == 'camera'\
        and operation == 'deactivate':
        authorized = True

    if  src == 'monitor' and dst == 'monitor':
        authorized = True
    if  src == 'central' and dst == 'monitor':
        authorized = True

    #are not in code yet
    if  src == 'central' and dst == 'gps'\
        and operation == 'where_am_i':
        authorized = True
    #simple checking length of messages
    if  src == 'gps' and dst == 'central'\
        and operation == 'gps' and len(details) == 6:
        authorized = True
    if  src == 'gps' and dst == 'central'\
        and operation == 'gps_error' and len(details) == 4:
        authorized = True
    if  src == 'position' and dst == 'gps'\
        and operation == 'nonexistent':
        authorized = True
        

    return authorized
