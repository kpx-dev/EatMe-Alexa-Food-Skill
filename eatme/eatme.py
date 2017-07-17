import json
import boto3
import requests
import os
import yaml
import click

from base64 import b64decode
from eatme.yelp import Yelp
from pathlib import Path

kms = boto3.client('kms')
slack_webhook = kms.decrypt(CiphertextBlob=b64decode(os.environ.get('SLACK_WEBHOOK')))['Plaintext'].decode('utf-8')
yelp_keys = {
    'app_id': kms.decrypt(CiphertextBlob=b64decode(os.environ.get('YELP_APP_ID')))['Plaintext'].decode('utf-8'),
    'app_secret': kms.decrypt(CiphertextBlob=b64decode(os.environ.get('YELP_APP_SECRET')))['Plaintext'].decode('utf-8'),
    'app_access_token': kms.decrypt(CiphertextBlob=b64decode(os.environ.get('YELP_ACCESS_TOKEN')))['Plaintext'].decode('utf-8')
}
dynamodb_table = os.environ.get('TABLE_NAME')
with Path.cwd().joinpath('eatme/script.yml').open() as f: script = yaml.load(f)

def get_intent(event):
    return event['request']['intent']['name']


def random(event):
    yelp = Yelp(
        app_id=yelp_keys['app_id'],
        app_secret=yelp_keys['app_secret'],
        app_access_token=yelp_keys['app_access_token']
    )

    biz = yelp.run(term='restaurant', location='92683')
    miles = int(biz['distance'] / 1609.344)

    answer = script['answer'].format(
        name=biz['name'],
        stars=biz['rating'],
        reviews=biz['review_count'],
        miles=miles,
        address=', '.join(biz['location']['display_address'])
    )
    answer = answer.replace('&', 'and')
    next_statement = script['answer_repeat']

    return answer

    # return question(statement_text).reprompt(next_statement).simple_card(app_name, statement_text)

@click.command()
# @click.argument('name')
# @click.option('--count', default=1, help='Number of greetings.')
# @click.option('--name', prompt='Your name', help='The person to greet.')
def cli(name, count=0):
    print(name)

def main(event, context):
    status_code = 200
    payload = {}

    intent = get_intent(event=event)

    if intent == 'EatMeIntent':
        payload = random(event)

    print(payload)

    res_body = { 'message': payload, 'input': event }

    response = {
        'statusCode': status_code,
        # 'headers': {
        #     "x-custom-header" : "my custom header value"
        # },
        'body': json.dumps(res_body)
    }

    slack_payload = { 'text': 'Intent: {} \n{}'.format(intent, payload) }
    requests.post(url=slack_webhook, data=json.dumps(slack_payload))

    try:
        context.succeed(response)
    except Exception as e:
        print(e)
        pass


if __name__ == '__main__':
    event = {
    "session": {
        "sessionId": "SessionId.edb7d197-474a-4aa4-8578-617be75570db",
        "application": {
            "applicationId": "amzn1.ask.skill.64f32e53-97ef-4f27-b478-18be3862e5a7"
        },
        "attributes": {},
        "user": {
            "userId": "amzn1.ask.account.AHVWLUPSNFQ5ZZBGZIOJJKQFQUKPN3NYFAMLCJTQS56Z6NI7QTE2D4P5QEVAOML3TZR46646BKHAYVAYWRODUYM5U6XYNTQMPFBG3PMQ57UCZF3Y2K4ILEGVJIMBFCC4WAWKTCGSOI3JZ6HUW56Z2BOS57OO3AHN4U5JMIYJ6FOSYT3XRCVIZ5N2G2UWVOX36WHSVJVJPIB55DI",
            "accessToken": ""
        },
        "new": True
    },
    "request": {
        "requestId": "EdwRequestId.beba2d7b-321b-4f84-a5e3-effd508c7c5e",
        "locale": "en-US",
        "type": "IntentRequest",
        "timestamp": 1500274514095,
        "intent": {
            "name": "EatMeIntent",
            "slots": {}
        }
    },
    "context": {
        "System": {
            "application": {
                "applicationId": "applicationId"
            },
            "user": {
                "userId": "userId",
                "permissions": {
                    "consentToken": "consentToken"
                },
                "accessToken": "accessToken"
            },
            "device": {
                "deviceId": "deviceId",
                "supportedInterfaces": {}
            },
            "apiEndpoint": "apiEndpoint"
        }
    }
}

    main(event=event, context={})
