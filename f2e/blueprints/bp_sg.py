import io
import re
import json
import logging
import base64
import unicodedata

from bs4 import BeautifulSoup
import PyPDF2
from flask import Blueprint, request, render_template
from flask import render_template_string
from flask import current_app as app

from f2e import model

log = logging.getLogger(__name__)
mod = Blueprint('sendgrid', __name__)
re_cid_url = re.compile(r'^cid:(?P<name>.+)@(?P<msgid>.*)$')


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
    pdf_cover = app.pdf.from_string(html_cover)

    # Read the attachements
    num_attachments = int(request.form.get('attachments', 0))
    attachments = [
        request.files.get('attachment{}'.format(num))
        for num in range(1, num_attachments+1)]
    attachments_byname = {a.filename: a for a in attachments}
    for a in attachments:
        a.skip = False
        a.data = a.read()

    rdr = PyPDF2.PdfFileReader(io.BytesIO(pdf_cover))
    wr = PyPDF2.PdfFileWriter()
    wr.appendPagesFromReader(rdr)
    if html:
        html = unicodedata.normalize("NFKD", html)
        soup = BeautifulSoup(html, 'html.parser')
        for img in soup.find_all('img'):
            src = img.attrs.get('src', '')
            m = re_cid_url.match(src)
            if not m:
                continue
            att = attachments_byname.get(m.group('name'))
            if att:
                durl = data_url(att)
                att.skip = True
            else:
                durl = '#'
            img.attrs['src'] = durl

        html = str(soup)

        html = render_template('html_part.html', **locals())
        try:
            pdf_html = app.pdf.from_string(html)
            wr.appendPagesFromReader(PyPDF2.PdfFileReader(io.BytesIO(pdf_html)))
        except Exception as err:
            log.exception('Error rendering html')
            with open('error.html', 'w') as fp:
                fp.write(html)

    for attachment in attachments:
        if attachment.skip:
            continue
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
        filename=att.filename, text=att.data)
    pdf = app.pdf.from_string(html)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))


def render_html(att):
    pdf = app.pdf.from_string(att.data)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))


def render_image(att):
    import ipdb; ipdb.set_trace();
    html = render_template_string(
        '''
        <h1>{{filename}}</h1>
        <img src="{{url}}"/>
        ''',
        filename=att.filename,
        url=data_url(att))
    pdf = app.pdf.from_string(html)
    return PyPDF2.PdfFileReader(io.BytesIO(pdf))


def data_url(att):
    data = base64.b64encode(att.data).decode('ascii')
    return 'data:{content_type};base64,{data}'.format(
        content_type=att.content_type,
        data=data)

