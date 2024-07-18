import uuid
from datetime import datetime

from sklearn.metrics.pairwise import cosine_similarity as cs


def get_mac_address():
    ''' Returns the MAC address of the device '''
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])

def get_current_time():
    ''' Returns the current datetime in the format '%Y-%m-%d %H:%M:%S' '''
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def cosine_similarity(vector1, matrix):
    ''' Returns the cosine similarity between a vector and a matrix '''
    return cs(vector1, matrix).flatten()