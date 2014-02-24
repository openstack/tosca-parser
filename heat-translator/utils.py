import numbers

def validate_integer(value):
    if not isinstance(value, (int, long)):
        raise TypeError('value is not an integer for %s' %value)
    return validate_number(value)
    
def validate_number(value):
    return str_to_num(value)

def validate_string(value):
    if not isinstance(value, basestring):
        raise ValueError(_('Value must be a string'))
    return value

def validate_list(self, value):
    pass
    
def str_to_num(value):
    '''Convert a string representation of a number into a numeric type.'''
    if isinstance(value, numbers.Number):
        return value
    try:
        return int(value)
    except ValueError:
        return float(value)