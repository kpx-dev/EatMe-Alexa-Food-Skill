import json
import boto3
import requests
import os
import yaml

from eatme.yelp import Yelp
from eatme.core import success, decrypt, validate_request, card
from pathlib import Path

slack_webhook = decrypt(key=os.environ.get('SLACK_WEBHOOK'))
yelp_keys = {
    'app_id': decrypt(key=os.environ.get('YELP_APP_ID')),
    'app_secret': decrypt(key=os.environ.get('YELP_APP_SECRET')),
    'app_access_token': decrypt(key=os.environ.get('YELP_ACCESS_TOKEN'))
}
dynamodb_table = os.environ.get('TABLE_NAME')
eatme_app_id = os.environ.get('EATME_APP_ID')

with Path.cwd().joinpath('eatme/script.yml').open() as f: script = yaml.load(f)


def location(event):
    device_id = event['context']['System']['device']['deviceId']
    url = 'https://api.amazonalexa.com/v1/devices/{}/settings/address/countryAndPostalCode'.format(device_id)
    token = event['context']['System']['user']['permissions']['consentToken']
    header = {'Authorization': 'Bearer {}'.format(token)}

    return requests.get(url, headers=header).json()

def random(event):
    user_zipcode = location(event)['postalCode'] or '92683'

    yelp = Yelp(
        app_id=yelp_keys['app_id'],
        app_secret=yelp_keys['app_secret'],
        app_access_token=yelp_keys['app_access_token']
    )

    biz = yelp.run(term='restaurant', location=user_zipcode)
    miles = int(biz['distance'] / 1609.344)

    answer = script['answer_speech'].format(
        name=biz['name'],
        stars=biz['rating'],
        reviews=biz['review_count'],
        miles=miles
    )
    speech_text = answer.replace('&', 'and')
    address = ', '.join(biz['location']['display_address'])
    card_title = script['answer_card_title'].format(name=biz['name'], rating=biz['rating'], review=biz['review_count'])
    card_content = script['answer_card_content'].format(name=biz['name'], address=address)

    res_card = card(title=card_title, content=card_content, img=biz['image_url'])

    return success(speech_text=speech_text, card=res_card, speech_text_reprompt=script['answer_repeat'])


def end():
    return success(speech_text=script['bye'])


def on_session_started(event):
    return random(event)


def on_launch(event):
    return success(speech_text=script['welcome'], speech_text_reprompt=script['welcome_repeat'])


def on_intent(event):
    intent_name = event['request']['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "EatMeIntent":
        return random(event)
    elif intent_name == "AMAZON.HelpIntent":
        return launch()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return end()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(event):
    return end()


def main(event, context):
    # print('raw event is: ', event)
    # print('raw context is: ', context)

    if not validate_request(event):
        raise ValueError("Failed validation")

    # if event['session']['application']['applicationId'] != eatme_app_id:
    #     raise ValueError("Invalid Application ID: {}".format(event['session']['application']['applicationId']))

    # if event['session']['new']:
    #     return on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event)
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event)
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event)


if __name__ == '__main__':
    test_file = 'test/eatme_intent_location.json'
    # test_file = 'test/launch.json'
    # test_file = 'test/end.json'
    # test_file = 'test/eatme_intent_.json'
    with open(test_file, 'r') as f:
        event = json.load(f)

    res = main(event=event, context={})
    print(json.dumps(res, indent=3))
