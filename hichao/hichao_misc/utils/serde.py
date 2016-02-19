import msgpack
import pickle

default_format = pickle

def serialize(key, value, serformat=default_format.dumps):
    if type(value) == str:
        return value, 1
    return serformat(value)

def deserialize(key, value, deformat=default_format.loads, flags=2):
    if flags == 1:
        return value
    if flags == 2:
        return deformat(value)
    raise Exception("Unknown flags for value: {1}".format(flags))
