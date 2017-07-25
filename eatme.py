import json
import boto3
import requests
import os
import yaml

from eatme.yelp import Yelp
from eatme.core import success, decrypt, validate_request
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


def random():
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
    message = answer.replace('&', 'and')

    return success(title='Random eat', message=message, message_repeat=script['answer_repeat'])


def launch():
    return success(title='Welcome', message=script['welcome'], message_repeat=script['welcome_repeat'], close=False)


def end():
    return success(title='Goodbye', message=script['bye'], close=True)


# def create_favorite_color_attributes(favorite_color):
#     return {"favoriteColor": favorite_color}


# def set_color_in_session(intent, session):
#     """ Sets the color in the session and prepares the speech to reply to the
#     user.
#     """

#     card_title = intent['name']
#     session_attributes = {}
#     should_end_session = False

#     if 'Color' in intent['slots']:
#         favorite_color = intent['slots']['Color']['value']
#         session_attributes = create_favorite_color_attributes(favorite_color)
#         speech_output = "I now know your favorite color is " + \
#                         favorite_color + \
#                         ". You can ask me your favorite color by saying, " \
#                         "what's my favorite color?"
#         reprompt_text = "You can ask me your favorite color by saying, " \
#                         "what's my favorite color?"
#     else:
#         speech_output = "I'm not sure what your favorite color is. " \
#                         "Please try again."
#         reprompt_text = "I'm not sure what your favorite color is. " \
#                         "You can tell me your favorite color by saying, " \
#                         "my favorite color is red."
#     return build_response(session_attributes, build_speechlet_response(
#         card_title, speech_output, reprompt_text, should_end_session))


# def get_color_from_session(intent, session):
#     session_attributes = {}
#     reprompt_text = None

#     if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
#         favorite_color = session['attributes']['favoriteColor']
#         speech_output = "Your favorite color is " + favorite_color + \
#                         ". Goodbye."
#         should_end_session = True
#     else:
#         speech_output = "I'm not sure what your favorite color is. " \
#                         "You can say, my favorite color is red."
#         should_end_session = False

#     # Setting reprompt_text to None signifies that we do not want to reprompt
#     # the user. If the user does not respond or says something that is not
#     # understood, the session will end.
#     return build_response(session_attributes, build_speechlet_response(
#         intent['name'], speech_output, reprompt_text, should_end_session))


def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

    return random()


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return launch()


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "EatMeIntent":
        return random()
    elif intent_name == "AMAZON.HelpIntent":
        return launch()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return end()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    return end()
    # add cleanup logic here


def main(event, context):
    if not validate_request(event):
        return success(title='Error', message='Error')

    if event['session']['application']['applicationId'] != eatme_app_id:
        raise ValueError("Invalid Application ID: {}".format(event['session']['application']['applicationId']))

    if event['session']['new']:
        return on_session_started({'requestId': event['request']['requestId']}, event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


if __name__ == '__main__':
    test_file = 'test/eatme_intent.json'
    # test_file = 'test/launch.json'
    # test_file = 'test/end.json'
    with open(test_file, 'r') as f:
        event = json.load(f)

    res = main(event=event, context={})
    print(json.dumps(res, indent=3))
