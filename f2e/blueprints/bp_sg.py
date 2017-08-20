import io
import json
import logging
import base64
import unicodedata

import pdfkit
import PyPDF2
from flask import Blueprint, request, render_template
from flask import render_template_string

from f2e import model

log = logging.getLogger(__name__)
mod = Blueprint('sendgrid', __name__)


OPTIONS = {
    'page-size': 'Letter',
    # 'dpi': 200,
    # 'disable-smart-shrinking': None,
}

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
    log.info('From: %s', from_)
    log.info('To:   %s', to)
    log.info('Subject: %s', subject)
    log.info('Text:\n%s', text)

    html_cover = render_template('cover_sheet.html', **locals())
    pdf_cover = pdfkit.from_string(html_cover, False, options=OPTIONS)

    rdr = PyPDF2.PdfFileReader(io.BytesIO(pdf_cover))
    wr = PyPDF2.PdfFileWriter()
    wr.appendPagesFromReader(rdr)
    if html:
        html = unicodedata.normalize("NFKD", html)
        pdf_html = pdfkit.from_string(html, False, options=OPTIONS)
        wr.appendPagesFromReader(PyPDF2.PdfFileReader(io.BytesIO(pdf_html)))

    # Process the attachements, if any
    num_attachments = int(request.form.get('attachments', 0))
    for num in range(1, (num_attachments + 1)):
        attachment = request.files.get(('attachment%d' % num))
        log.info('Found attachment %r', attachment)
        if attachment.content_type == 'application/pdf':
            wr.appendPagesFromReader(PyPDF2.PdfFileReader(attachment))
        elif attachment.content_type == 'text/plain':
            wr.appendPagesFromReader(render_text(attachment))
        elif attachment.content_type == 'text/html':
            wr.appendPagesFromReader(render_html(attachment))
        elif attachment.content_type.startswith('image/'):
            wr.appendPagesFromReader(render_image(attachment))
        else:
            log.error('I have no idea what to do with %s', attachment)

    with open('out.pdf', 'wb') as fp:
        wr.write(fp)

    return "OK"


def render_text(att):
    html = render_template_string(
        '<h1>{{filename}}</h1><pre>{{text}}</pre>',
        filename=att.filename, text=att.read())
    pdf = pdfkit.from_string(html, False, options=OPTIONS)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))


def render_html(att):
    pdf = pdfkit.from_string(att.read(), False, options=OPTIONS)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))


def render_image(att):
    html = render_template_string(
        '''
        <h1>{{filename}}</h1>
        <img src="data:{{content_type}};base64,{{data}}"/>
        ''',
        filename=att.filename,
        content_type=att.content_type,
        data=base64.b64encode(att.read()).decode('ascii'))
    pdf = pdfkit.from_string(html, False, options=OPTIONS)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))
