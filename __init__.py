def yes_no(default, question):
    ''' default can be True, False, or None '''
    if default == None:
        yn_prompt = ' [yn]'
    elif default:
        yn_prompt = ' [Yn]'
    else:
        yn_prompt = ' [yN]'

    answer = input(question + yn_prompt).lower()

    if answer == 'y':
        return True
    elif answer == 'n':
        return False
    elif default != None:
        return default
    else:
        print("Invalid response: " + answer)
        return yes_no(default, question)

def shorten_string(string, length):
    ''' shortens a string and uses "..." to show it's been shortened '''
    if len(string) <= length:
        return string

    return string[:length-3] + '...'

class ProgressMapper(object):
    """ Use this to print 7/10 style progress indicators.

    Use the 'with' keyword.
    """
    def __init__(self, items_len):
        self.items_len = items_len
        self.rjust_num = len(str(items_len))
        self(-1)

    def __enter__(self):
        self(-1)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        print()

    def __call__(self, item_index):
        item_num  = str(item_index + 1).rjust(self.rjust_num)
        print('\r{item_num}/{self.items_len}'.format(**locals()), end=' ')

def progress_map(f, l):
    """
    Map a function to a list, and print a 7/10 style progress indicator
    while you're working.
    """

    with ProgressMapper(len(l)) as progress_mapper:
        for i, v in enumerate(l):
            f(v)
            progress_mapper(i)

def not_func(f):
    """ A decorator that not's a function's return value. """
    def new_f(*args, **kwargs):
        return not f(*args, **kwargs)

    return new_f

def lazy_property(fn):
    """A decorator for @properties.

    Only computes the return value once.
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))

        return getattr(self, attr_name)

    return _lazy_property