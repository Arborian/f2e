from io import BytesIO
import logging
import base64

import sendgrid
from sendgrid.helpers import mail
from twilio.twiml.fax_response import FaxResponse
from flask import Blueprint, request, url_for, abort, Response
from flask import current_app as app

from f2e import model

log = logging.getLogger(__name__)
mod = Blueprint('twilio', __name__)


@mod.route('/fax/sent', methods=['POST'])
def fax_sent():
    resp = FaxResponse()
    resp.receive(action=url_for('.fax_received'))
    return str(resp)


@mod.route('/fax/received', methods=['POST'])
def fax_received():
    """Define a handler for when the fax finished sending to us."""
    # We will have a URL to the contents of the fax at this point
    # log the URL of the PDF received in the fax
    media_url = request.form.get('MediaUrl')

    if media_url:
        r = app.twilio_download_session.get(media_url)
        r.raise_for_status()
        content = r.content
        content_type = r.headers['content-type']
    else:
        content = None
        content_type = None

    from_ = request.form.get('From')
    to = request.form.get('To')
    status = request.form.get('Status')
    pages = request.form.get('NumPages')
    media_url = request.form.get('MediaUrl')
    error_code = request.form.get('ErrorCode')
    error_message = request.form.get('ErrorMessage')

    send_fax_as_email(
        from_, to, status, pages, error_code, error_message,
        content, content_type)

    # Respond with empty 200/OK to Twilio
    return '', 200


def send_fax_as_email(
        from_, to, status, pages,
        error_code, error_message,
        content, content_type):
    message = mail.Mail()
    message.from_email = mail.Email(
        '{}{}@{}'.format(
            app.config['FAX_EMAIL_PREFIX'],
            from_,
            app.config['INBOUND_EMAIL_DOMAIN']))
    message.subject = 'Incoming fax'
    personalization = mail.Personalization()
    personalization.add_to(mail.Email(model.email_from_number(to)))
    message.add_personalization(personalization)
    message.add_content(mail.Content(
        'text/html',
        '''
        <table>
            <tr><th>From</th><td>{from_}</td></tr>
            <tr><th>To</th><td>{to}</td></tr>
            <tr><th>Status</th><td>{status}</td></tr>
            <tr><th>Pages</th><td>{pages}</td></tr>
            <tr><th>Fax Error Code</th><td>{error_code}</td>
            <tr><th>Fax Error Message</th><td>{error_message}</td>
        </table>
        '''.format(**locals())))

    if content:
        attachment = mail.Attachment()
        attachment.content = base64.b64encode(content).decode('ascii')
        attachment.type = content_type
        attachment.filename = 'fax.pdf'
        attachment.disposition = "attachment"
        attachment.content_id = "Fax"
        message.add_attachment(attachment)

    data = message.get()

    app.sendgrid_client.client.mail.send.post(request_body=data)