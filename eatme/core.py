import boto3
import json
import requests
import time
import aniso8601
import requests
from base64 import b64decode
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


def zipcode(device_id, token):
    url = 'https://api.amazonalexa.com/v1/devices/{}/settings/address/countryAndPostalCode'.format(device_id)
    header = {'Authorization': 'Bearer {}'.format(token)}

    try:
        res = requests.get(url, headers=header).json()
        # print('zip code detected is ', res['postalCode'])

        return res['postalCode']
    except:
        return None


def track_dynamodb(table, event, business, zipcode='0', **kwargs):
    try:
        item = {
            'request_id': event['request']['requestId'],
            'date': event['request']['timestamp'],
            'user_id': event['session']['user']['userId'],
            'device_id': kwargs.get('device_id') or event['context']['System']['device']['deviceId'],
            'event': event,
            'zipcode': zipcode,
            'business_name': business['name'],
            'business': json.dumps(business),
            'speech_text': kwargs.get('speech_text', '_'),
            'speech_text_reprompt': kwargs.get('speech_text_reprompt', '_'),
            'card': kwargs.get('card', {})
        }

        return table.put_item(Item=item)
    except Exception as e:
        print(e)


def track_slack(webhook, message):
    payload = {'text': message}
    try:
        res = requests.post(url=webhook, data=json.dumps(payload))
        if not res.ok:
            print('problem tracking to Slack', res.text)
    except Exception as e:
        print('problem tracking to Slack', e)

def validate_request(event, app_id, request_timestamp):
    if _validate_app_id(source=event['session']['application']['applicationId'], expected=app_id) and _validate_timestamp(timestamp=request_timestamp):
        return True

    return False


def _validate_app_id(source, expected):
    return source == expected

def _validate_timestamp(timestamp):
    try:
        ts = aniso8601.parse_datetime(timestamp)
        dt = datetime.utcnow() - ts.replace(tzinfo=None)

        if abs(dt.total_seconds()) > 150:
            return False
    except Exception as e:
        print(e)

    return True
