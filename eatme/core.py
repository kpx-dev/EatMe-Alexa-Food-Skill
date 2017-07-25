import boto3
import json
import requests
from base64 import b64decode
from OpenSSL import crypto
from datetime import datetime

class VerificationError(Exception): pass

kms = boto3.client('kms')

def success(title, message, message_repeat=None, session_attributes={}, close=True):
    speechlet = _speechlet(title=title, message=message, reprompt_text=message_repeat, should_end_session=close)

    return _response(speechlet=speechlet)

def error(title, message, message_repeat=None, session_attributes={}, close=True):
    speechlet = _speechlet(title=title, message=message, reprompt_text=message_repeat, should_end_session=close)

    return _response(speechlet=speechlet)

def decrypt(key):
    return kms.decrypt(CiphertextBlob=b64decode(key))['Plaintext'].decode('utf-8')

def _speechlet(title, message, reprompt_text=None, should_end_session=True, title_prefix='EatMe - '):
    payload = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': message
        },
        'card': {
            'type': 'Simple',
            'title': title_prefix + title,
            'content': message
        },
        'shouldEndSession': should_end_session
    }

    if reprompt_text:
        payload['reprompt'] = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        }

    return payload

def _response(speechlet, session_attributes={}):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet
    }

def validate_request(request):
    # _validate_cert()
    # _validate_signature()
    # _validate_timestamp()

    return True


def _validate_cert(cert_url):
    cert_data = requests.get(cert_url)
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)

    not_after = cert.get_notAfter().decode('utf-8')
    not_after = datetime.strptime(not_after, '%Y%m%d%H%M%SZ')
    if datetime.utcnow() >= not_after:
        return False

    found = False
    for i in range(0, cert.get_extension_count()):
        extension = cert.get_extension(i)
        short_name = extension.get_short_name().decode('utf-8')
        value = str(extension)
        if 'subjectAltName' == short_name and 'DNS:echo-api.amazon.com' == value:
            found = True
            break

    if not found:
        return False

    return True


def _validate_signature(cert, signature, signed_data):
    try:
        signature = base64.b64decode(signature)
        crypto.verify(cert, signature, signed_data, 'sha1')
    except crypto.Error as e:
        raise VerificationError(e)


def _validate_timestamp(timestamp):
    dt = datetime.utcnow() - timestamp.replace(tzinfo=None)
    if abs(dt.total_seconds()) > 150:
        raise VerificationError("Timestamp verification failed")
