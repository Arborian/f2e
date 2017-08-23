import os
import logging

import requests
from flask import Flask, jsonify, redirect, request
from flask_logconfig import LogConfig
from sendgrid import SendGridAPIClient
from twilio.rest import Client as TwilioRestClient
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from . import util
from .blueprints import bp_twilio, bp_sg

log = logging.getLogger(__name__)


def make_app(**extra_config):
    app = Flask(__name__,
        static_folder='static',
        template_folder='templates')
    app.config.from_object('f2e.default_config')
    for k in app.config:
        value_from_env = os.getenv(k)
        if value_from_env is None:
            continue
        app.config[k] = value_from_env
    app.config.update(extra_config)
    logcfg = LogConfig()
    logcfg.init_app(app)

    app.twilio_client = TwilioRestClient(
        app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN'])
    app.twilio_download_session = requests.Session()
    retries = Retry(
        total=3, backoff_factor=1,
        status_forcelist=[404, 502, 503, 504])
    app.twilio_download_session.auth=(
        app.config['TWILIO_ACCOUNT_SID'],
        app.config['TWILIO_AUTH_TOKEN'])
    app.twilio_download_session.mount(
        'http://', HTTPAdapter(max_retries=retries))
    app.twilio_download_session.mount(
        'https://', HTTPAdapter(max_retries=retries))
    app.sendgrid_client = SendGridAPIClient(
        apikey=app.config['SENDGRID_API_KEY'])
    app.pdf = util.PDFKit(app.config)

    logging.info('Mounting twilio directory')
    app.register_blueprint(bp_twilio.mod, url_prefix='/twilio')

    logging.info('Mounting sendgrid directory')
    app.register_blueprint(bp_sg.mod, url_prefix='/sg')

    if util.truthish(app.config['SECURE']):
        log.info('Only accepting https')

        @app.before_request
        def before_request():
            proto = request.headers.get('X-Forwarded-Proto', 'http')
            if proto == 'https':
                return
            if request.url.startswith('http://'):
                log.info('*** redirect url %s => https', request.url)
                log.info('... request headers follow')
                for k, v in request.headers.items():
                    log.info('... %20s => %r', k, v)
                url = request.url.replace('http://', 'https://', 1)
                return redirect(url, 301)

    return app
