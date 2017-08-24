import json
import uuid
import logging

from flask import Blueprint, request, url_for
from flask import current_app as app

from f2e import model
from f2e import pdf

log = logging.getLogger(__name__)
mod = Blueprint('sendgrid', __name__)
# re_cid_url = re.compile(r'^cid:(?P<name>.+)@(?P<msgid>.*)$')

FAX_DATA = {}



@mod.route('/parse', methods=['POST'])
def parse():
    # Consume the entire email
    envelope = json.loads(request.form.get('envelope'))

    # Get some header information
    to_addresses = envelope['to']
    from_address = envelope['from']
    log.info('Envelope from: %s to: %s', from_address, to_addresses)

    text = request.form.get('text')
    html = request.form.get('html')
    subject = request.form.get('subject')
    from_ = request.form.get('from')
    to = request.form.get('to')

    num_attachments = int(request.form.get('attachments', 0))
    attachments = [
        request.files.get('attachment{}'.format(num))
        for num in range(1, num_attachments+1)]
    pdf_data = pdf.email_to_pdf(
        app.pdf, text, html,
        to, from_, subject,
        attachments)
    with open('out.pdf', 'wb') as fp:
        fp.write(pdf_data)
    id = str(uuid.uuid4())
    FAX_DATA[id] = pdf_data
    media_url = url_for('.fax_data', id=id, _external=True)
    log.info('Created data resource at %r', media_url)
    app.twilio_client.fax.v1.faxes.create(
        from_=app.config['FAX_NUMBER'],
        to=model.number_from_email(to),
        media_url=media_url)
    return 'OK'


@mod.route('/fax_data/<id>')
def fax_data(id):
    data = FAX_DATA.get(id, None)
    if data is None:
        log.error("Can't find fax %s, valid ids are %r", id, list(FAX_DATA))
    return data, 200

