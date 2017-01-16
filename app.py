import argparse
import json
import pprint
import sys
import os
import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question
from dotenv import load_dotenv, find_dotenv
from yelp import Yelp
load_dotenv(find_dotenv())

app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger(__name__).setLevel(logging.DEBUG)

@ask.launch
def launch():
    welcome_text = render_template('welcome')

    return statement(welcome_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')

    return statement(help_text)


@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
def stop():
    bye_text = render_template('bye')

    return statement(bye_text)

@ask.session_ended
def session_ended():
    return "", 200


@ask.intent('EatMeIntent')
def yelp():
    yelp = Yelp(
        app_id=os.environ.get("YELP_APP_ID"),
        app_secret=os.environ.get("YELP_APP_SECRET"),
        app_access_token=os.environ.get("YELP_ACCESS_TOKEN")
    )

    biz = yelp.run(term='restaurant', location='92683')
    miles = int(biz['distance'] / 1609.344)
    print(biz)
    statement_text = render_template('answer',
        name=biz['name'],
        stars=biz['rating'],
        reviews=biz['review_count'],
        miles=miles,
        address=', '.join(biz['location']['display_address'])
    )
    statement_text = statement_text.replace('&', 'and')
    print(statement_text)

    return statement(statement_text).simple_card("Eat Me", statement_text)


def main():
    app.run()

if __name__ == '__main__':
    main()
