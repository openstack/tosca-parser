import numbers    

class Constraint(object): 
    
    CONSTRAINTS = (EQUAL, GREATER_THAN,
                   GREATER_OR_EQUAL, LESS_THAN, LESS_OR_EQUAL, IN_RANGE, VALID_VALUES,
                   LENGTH, MIN_LENGHT, MAX_LENGTH, PATTERN) = \
                   ('equal', 'greater_than', 'greater_or_equal',
                     'less_than', 'less_or_equal', 'in_range', 'valid_values', 'length', 'min_length',
                     'max_length', 'pattern')
                    
    def __init__(self, propertyname, value, constraint): 
        self.propertyname = propertyname
        self.value = value
        self.constraint = constraint #dictionary e.g. valid_values: [ 1, 2, 4, 8 ] or greater_or_equal: 1
    
    def validate(self):
        # for key in self.constraint.iterkeys():
        for key, value in self.constraint.iteritems():
            if key == "greater_or_equal":
                self.validate_greater_than(value)
        
    def validate_equal(self):
        pass

    def validate_greater_than(self, value):
        if self.value < value:
            print("%s value requires to be greater than %s" % (self.propertyname, value))
    
    def validate_greater_or_equal(self):
        pass
    
    def validate_less_than(self):
        pass
    
    def validate_less_or_equal(self):
        pass
    
    def validate_in_range(self):
        pass
    
    def validate_valid_values(self):
        pass
    
    def validate_length(self):
        pass
    
    def validate_min_length(self):
        pass
    
    def validate_max_length(self):
        pass
    
    def validate_pattern(self):
        pass

    @staticmethod
    def validate_integer(value):
        if not isinstance(value, (int, long)):
            import pdb 
            pdb.set_trace()
            raise TypeError('value is not an integer for %s' %value)
        return Constraint.validate_number(value)
    
    @staticmethod
    def validate_number(value):
        return Constraint.str_to_num(value)

    @staticmethod
    def validate_string(value):
        if not isinstance(value, basestring):
            raise ValueError('Value must be a string %s' %value)
        return value
    
    @staticmethod
    def validate_list(self, value):
        pass
    
    @staticmethod
    def str_to_num(value):
        """Convert a string representation of a number into a numeric type."""
        if isinstance(value, numbers.Number):
            return value
        try:
            return int(value)
        except ValueError:
            return float(value)