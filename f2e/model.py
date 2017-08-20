from flask import current_app as app


def number_from_email(email):
    return app.config['FAX_NUMBER']

def email_from_number(number):
    return app.config['EMAIL_ADDRESS']