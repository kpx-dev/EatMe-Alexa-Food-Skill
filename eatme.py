import json
import boto3
import requests
import os
import yaml

from eatme.yelp import Yelp
from eatme.core import success, decrypt, validate_request, card, zipcode, track_dynamodb, track_slack
from pathlib import Path
from datetime import datetime

slack_webhook = decrypt(key=os.environ.get('SLACK_WEBHOOK'))
yelp_keys = {
    'app_id': decrypt(key=os.environ.get('YELP_APP_ID')),
    'app_secret': decrypt(key=os.environ.get('YELP_APP_SECRET')),
    'app_access_token': decrypt(key=os.environ.get('YELP_ACCESS_TOKEN'))
}
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME'))
eatme_app_id = os.environ.get('EATME_APP_ID')

with Path.cwd().joinpath('eatme/script.yml').open() as f: script = yaml.load(f)


def random(event):
    user_zipcode = '92683'
    device_id = 'Unknown'

    if 'context' in event and 'consentToken' in event['context']['System']['user']['permissions']:
        device_id = event['context']['System']['device']['deviceId']
        token = event['context']['System']['user']['permissions']['consentToken']
        user_zipcode = zipcode(device_id=device_id, token=token) or user_zipcode

    yelp = Yelp(
        app_id=yelp_keys['app_id'],
        app_secret=yelp_keys['app_secret'],
        app_access_token=yelp_keys['app_access_token']
    )

    biz = yelp.run(term='food', location=user_zipcode)

    # convert meter to miles
    miles = int(biz['distance'] / 1609.344)

    answer = script['answer_speech'].format(
        name=biz['name'],
        stars=biz['rating'],
        reviews=biz['review_count'],
        miles=miles
    )
    speech_text = answer.replace('&', 'and')
    address = ', '.join(biz['location']['display_address'])
    card_title = script['answer_card_title'].format(name=biz['name'], rating=biz['rating'])
    card_content = script['answer_card_content'].format(name=biz['name'], review=biz['review_count'] ,address=address)

    res_card = card(title=card_title, content=card_content, img=biz['image_url'])

    track_dynamodb(
        table=table,
        event=event,
        device_id=device_id,
        zipcode=user_zipcode,
        business=biz,
        speech_text=speech_text, card=res_card, speech_text_reprompt=script['answer_repeat'])

    return success(speech_text=speech_text, card=res_card, speech_text_reprompt=script['answer_repeat'])


def end(event):
    return success(speech_text=script['bye'])


def help(event):
    return success(speech_text=script['help'], speech_text_reprompt=script['help_repeat'])


def on_session_started(event):
    return random(event)


def on_launch(event):
    return success(speech_text=script['welcome'], speech_text_reprompt=script['welcome_repeat'])


def on_session_ended(event):
    return end(event)


def on_intent(event):
    intent_name = event['request']['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "EatMeIntent":
        return random(event)
    elif intent_name == "AMAZON.HelpIntent":
        return help(event)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return end(event)
    else:
        raise ValueError("Invalid intent")


def main(event, context):
    track_slack(webhook=slack_webhook, message='```New request on {}: \n {}```'.format(
        datetime.now().isoformat(),
        json.dumps(event, indent=3)))

    request_timestamp = event['request']['timestamp']

    if not os.environ.get('DEBUG') and not validate_request(event, app_id=eatme_app_id, request_timestamp=request_timestamp):
        raise ValueError("Failed validation")

    # must have device permission before continue:
    if 'permissions' not in event['context']['System']['user'] or 'consentToken' not in event['context']['System']['user']['permissions']:
        return success(speech_text=script['require_permission'])

    # if event['session']['new']:
    #     return on_session_started(event)

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
