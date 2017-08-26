import re
import logging

from flask import current_app as app

log = logging.getLogger(__name__)
re_fax_email_addr = re.compile(r'(?P<addr>.*)(?P<number>\+.*)@.*')


def number_from_email(email):
    m = re_fax_email_addr.search(email)
    if not m:
        log.error('Invalid email address, not sending fax')
        return None
    elif m.group('addr') != app.config['FAX_EMAIL_PREFIX']:
        log.error('Invalid email address %r, not sending fax')
        return None
    else:
        return m.group('number')


def email_from_number(number):
    return app.config['EMAIL_ADDRESS']
