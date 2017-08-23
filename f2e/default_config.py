import logging

LOGCONFIG = './logging.debug.yaml'
LOGCONFIG_REQUESTS_ENABLED = True
LOGCONFIG_REQUESTS_LEVEL = logging.INFO
LOGCONFIG_REQUESTS_MSG_FORMAT = '{remote_addr} - - {method} "{base_url}" {status} ({execution_time}ms)'

WKHTMLTOPDF_CMD='wkhtmltopdf'

EVENTLET = True
SECURE = None

TWILIO_ACCOUNT_SID = None
TWILIO_AUTH_TOKEN = None

SENDGRID_API_KEY = None
INBOUND_EMAIL_DOMAIN = None

EMAIL_ADDRESS = None
FAX_NUMBER = None
