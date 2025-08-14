
def send_can_11b(bus, id, data):
    return send_can(bus, id, data, False)


def send_can_29b(bus, id, data):
    return send_can(bus, id, data, True)



def send_can(bus, id, data, extended):
    message = can.Message(arbitration_id=id, is_extended_id=extended, data=data)
    bus.send(message)


def rcv_can_11b(bus, can_id, timeout):
    """
    from the python-can can:
            --filter ...
            Comma separated filters can be specified for the given
            CAN interface: <can_id>:<can_mask> (matches when
            <received_can_id> & mask == can_id & mask)
            <can_id>~<can_mask> (matches when <received_can_id> &
            mask != can_id & mask)
    """
    return rcv_can(bus, can_id, timeout, False)


def rcv_can_29b(bus, can_id, timeout):
    return rcv_can(bus, can_id, timeout, True)


def rcv_can(bus, can_id, timeout, extended):
    bus.set_filters([{"can_id": can_id, "can_mask": can_id, "extended": extended}])
    message = bus.recv(timeout=timeout)
    return message

def receive_msg(bus, id, extended):
    if not bus:
        return "Bus Error"
    [can_id_string, timeout, format_str] = id.split(":", 2)
    can_id = int(can_id_string, 16)
    timeout = int(timeout) / 1000
    message = rcv_can(bus, can_id, timeout, extended)
    return message
