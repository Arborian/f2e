import traceback

import six


TRUTHY = set(['true', 't', 'yes', 'y', 'on', '1'])
FALSEY = set(['false', 'f', 'no', 'n', 'off', '0'])


def truthish(value):
    """Convert a (possibly string) value to a boolean."""
    if isinstance(value, bool):
        return value
    assert isinstance(value, six.string_types), "Cannot convert a {}".format(
        type(value))
    val = value.lower()
    if val in TRUTHY:
        return True
    assert val in FALSEY, "Unknown boolish value {}".format(value)
    return False


def debug_hook(type, value, tb):
    """Launch the ipdb debugger on errors."""
    import ipdb
    traceback.print_exception(type, value, tb)
    print
    ipdb.pm()
