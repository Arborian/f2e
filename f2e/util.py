import traceback
import subprocess

import six
import pdfkit


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


class PDFKit(object):
    OPTIONS = {
        'page-size': 'Letter',
        'encoding': 'utf-8',
        'load-error-handling': 'ignore',
        'load-media-error-handling': 'ignore',
        'margin-left': '0',
        'margin-right': '0',
        'dpi': '72',
        'image-dpi': '100'
    }

    def __init__(self, config):
        command = subprocess.check_output(['which', config['WKHTMLTOPDF_CMD']]).strip()
        self.config = pdfkit.configuration(wkhtmltopdf=command)

    def from_string(self, html):
        return pdfkit.from_string(
            input=html,
            output_path=False,
            options=self.OPTIONS,
            configuration=self.config)