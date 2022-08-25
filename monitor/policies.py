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
    if not ordering:
        if  src == 'communication' and dst == 'central' \
            and operation == 'ordering' and type(details['pincode']) == int \
                and type(details['x']) == int and type(details['y']) == int \
                and abs(details['x']) <= 200 and abs(details['y']) <= 200  and len(details) == 7 :
            authorized = True
            ordering = True


    if src == 'central' and dst == 'communication' \
        and operation == 'confirmation':
        authorized = True    
    if src == 'central' and dst == 'positioning' \
        and operation == 'count_direction':
        authorized = True    
    if src == 'positioning' and dst == 'central' \
        and operation == 'count_direction':
        authorized = True    
    if src == 'central' and dst == 'motion' \
        and operation == 'motion_start':
        authorized = True    
    if src == 'motion' and dst == 'positioning' \
        and operation == 'motion_start':
        #and details['verified'] is True:
        authorized = True    
    if src == 'motion' and dst == 'positioning' \
        and operation == 'stop':
        authorized = True    
    if src == 'positioning' and dst == 'central' \
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
        and operation == 'ready':
        authorized = True
        ordering = False

    return authorized