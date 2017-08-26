import re
import logging

from flask import current_app as app

log = logging.getLogger(__name__)
re_fax_email_addr = re.compile(r'(?P<addr>.*)(?P<number>\+.*)@.*')


def number_from_email(email):
    m = re_fax_email_addr.search(email)
    default_number = app.config['FAX_NUMBER']
    if not m:
        log.error('Invalid email address send fax to %s', default_number)
        return default_number
    elif m.group('addr') != app.config['FAX_EMAIL_PREFIX']:
        log.error(
            'Invalid email address %r send fax to %s',
            m.groupdict(),
            default_number)
        return default_number
    else:
        return m.group('number')


def email_from_number(number):
    return app.config['EMAIL_ADDRESS']
