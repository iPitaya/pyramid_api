
class RequirementException(Exception):
    pass

def require(val):
    if not val:
        raise RequirementException
    return val

