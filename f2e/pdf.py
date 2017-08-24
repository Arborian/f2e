import re
import io
import base64
import logging
import subprocess
import unicodedata

import pdfkit
import PyPDF2
from bs4 import BeautifulSoup
from flask import render_template, render_template_string


log = logging.getLogger(__name__)


def email_to_pdf(
        kit, text, html,
        to, from_, subject,
        attachments):
    builder = PDFBuilder(kit, attachments)
    builder.append_html(
        render_template(
            'cover_sheet.html',
            to=to, from_=from_, subject=subject, text=text))
    if html:
        builder.append_html(
            render_template(
                'html_part.html',
                to=to, from_=from_, subject=subject, html=html))
    builder.append_attachments()
    return builder.get_data()



class PDFBuilder(object):
    re_cid_url = re.compile(r'^cid:(?P<name>.+)@(?P<msgid>.*)$')

    def __init__(self, kit, attachments):
        self.kit = kit
        self.writer = PyPDF2.PdfFileWriter()
        self.attachments = attachments
        self.attachment_index = {a.filename: a for a in attachments}
        for a in attachments:
            a.skip = False
            a.data = a.read()

    def get_data(self):
        fp = io.BytesIO()
        self.writer.write(fp)
        return fp.getvalue()

    def append_html(self, html_text, filename=None):
        html_text = unicodedata.normalize('NFKD', html_text)
        soup = BeautifulSoup(html_text, 'html.parser')
        soup = self._replace_cid_urls(soup)
        html_text = str(soup)
        pdf_data = self.kit.from_string(html_text, filename=filename)
        self.append_pdf(pdf_data)

    def append_pdf(self, pdf_data):
        rdr = PyPDF2.PdfFileReader(io.BytesIO(pdf_data))
        self.writer.appendPagesFromReader(rdr)

    def append_attachments(self):
        for a in self.attachments:
            if a.skip:
                continue
            if a.content_type == 'application/pdf':
                self.append_pdf(a.data)
            elif a.content_type == 'text/plain':
                self.append_text(a.data, filename=a.filename)
            elif a.content_type == 'text/html':
                self.append_html(a.data, filename=a.filename)
            elif a.content_type.startswith('image/'):
                self.append_image(
                    a.content_type, a.data, filename=a.filename)
            else:
                log.error('I have no idea what to do with %s', a)

    def append_text(self, data, filename=None):
        html = render_template_string(
            '<pre>{{data}}</pre>', data=data)
        self.append_html(html, filename=filename)

    def append_image(self, content_type, data, filename=None):
        url = self._data_url(content_type, data)
        html = render_template_string(
            '<img src="{{url}}"/>', url=url)
        self.append_html(html, filename=filename)

    def _replace_cid_urls(self, soup):
        for img in soup.find_all('img'):
            src = img.attrs.get('src', '')
            m = self.re_cid_url.match(src)
            if not m:
                continue
            att = self.attachment_index.get(m.group('name'))
            if att:
                durl = self._data_url(att.content_type, att.data)
                att.skip = True
            else:
                durl = '#'
            img.attrs['src'] = durl
        return soup

    def _data_url(self, content_type, data):
        data = base64.b64encode(data).decode('ascii')
        return 'data:{content_type};base64,{data}'.format(
            content_type=content_type,
            data=data)


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
        command = subprocess.check_output(['which', config['WKHTMLTOPDF_CMD']])
        command = command.strip()
        self.config = pdfkit.configuration(wkhtmltopdf=command)

    def from_string(self, html, filename=None):
        if filename:
            options = dict(
                self.OPTIONS,
                **{'header-left': filename})
        else:
            options = self.OPTIONS
        return pdfkit.from_string(
            input=html,
            output_path=False,
            options=options,
            configuration=self.config)