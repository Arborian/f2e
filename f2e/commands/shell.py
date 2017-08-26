"""Shell command."""
import json
import logging
from pprint import pprint

from flask import url_for
from cliff.command import Command
from IPython import embed

from f2e.app import make_app

log = logging.getLogger(__name__)

TEST_FAX_URL = 'https://www.twilio.com/docs/documents/25/justthefaxmaam.pdf'

class Shell(Command):
    """Run an interactive shell."""

    def take_action(self, parsed_args):
        app = make_app(
            SERVER_NAME='shell',
            EVENTLET=False)
        with app.app_context():
            embed()


def ngrokify(app, base_url):
    '''Setup webhooks so everything works with ngrok'''
    # Fixup Sendgrid webhooks
    parse_setting_path = 'user/webhooks/parse/settings/{}'.format(
        app.config['INBOUND_EMAIL_DOMAIN'])
    sg_url = base_url + url_for('sendgrid.parse', _external=False)
    r = app.sendgrid_client.client._(parse_setting_path).patch(
        request_body=dict(url=sg_url))
    pprint(json.loads(r.body))
    # Fixup Twilio webhooks
    for num in app.twilio_client.incoming_phone_numbers.list(
            phone_number=app.config['FAX_NUMBER']):
        num.update(
            voice_url=base_url + url_for('twilio.fax_sent', _external=False))


def send_fax(app, media_url=TEST_FAX_URL):
    return app.twilio_client.fax.v1.faxes.create(
        from_=app.config['FAX_NUMBER'],
        to=app.config['FAX_NUMBER'],
        media_url=media_url)
