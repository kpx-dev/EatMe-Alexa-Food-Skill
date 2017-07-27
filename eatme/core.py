import boto3
import json
import requests
from base64 import b64decode
from OpenSSL import crypto
from datetime import datetime

class VerificationError(Exception): pass

kms = boto3.client('kms')

def card(title, content, img=None):
    if img:
        card = _standard_card(title=title, content=content, small_img=img, large_img=img)
    else:
        card = _simple_card(title=title, content=content)

    return card

def success(speech_text, card=None, speech_text_reprompt=None, session_attributes={}):
    speechlet = _speechlet(speech_text=speech_text, card=card, speech_text_reprompt=speech_text_reprompt)

    return _response(speechlet=speechlet)

def error(title, message, small_img=None, large_img=None, message_repeat=None, session_attributes={}, close=True):
    card = _standard_card(title=title, content=content, small_img=small_img, large_img=large_img)
    speechlet = _speechlet(title=title, message=message, card=card, reprompt_text=message_repeat, should_end_session=close)

    return _response(speechlet=speechlet)

def decrypt(key):
    return kms.decrypt(CiphertextBlob=b64decode(key))['Plaintext'].decode('utf-8')

def _simple_card(title, content):
    return {
        'type': 'Simple',
        'title': title,
        'content': content
    }

def _standard_card(title, content, small_img=None, large_img=None):
    payload = {
        'type': 'Standard',
        'title': title,
        'text': content
    }

    if small_img or large_img:
        payload['image'] = {
            # small 720w x 480h
            # large 1200w x 800h
            'smallImageUrl': small_img,
            'largeImageUrl': large_img
        }

    return payload


def _link_card():
    return {
        'type': 'LinkAccount'
    }


def _speechlet(speech_text, card=None, speech_text_reprompt=None):
    payload = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': speech_text
        },
        'shouldEndSession': True
    }

    if card:
        payload['card'] = card

    if speech_text_reprompt:
        payload['reprompt'] = {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_text_reprompt
            }
        }

        payload['shouldEndSession'] = False

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
