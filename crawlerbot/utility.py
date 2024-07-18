import uuid
from datetime import datetime

def get_mac_address():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])

def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')