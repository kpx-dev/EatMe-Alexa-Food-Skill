import json
import os
import logging
from flask import Flask, render_template
from flask_ask import Ask, statement, question
from flask_ask.verifier import VerificationError
from dotenv import load_dotenv, find_dotenv
from yelp import Yelp
from flask_dotenv import DotEnv

load_dotenv(find_dotenv())
app = Flask(__name__)
ask = Ask(app, '/')
env = DotEnv()
env.init_app(app)

logging.getLogger(__name__).setLevel(logging.DEBUG)
app_name = 'Eat Me'

@ask.launch
def launch():
    welcome_text = render_template('welcome')
    welcome_repeat_text = render_template('welcome_repeat')

    return question(welcome_text).reprompt(welcome_repeat_text).simple_card(
        app_name, welcome_text)


@ask.intent('AMAZON.HelpIntent')
def help():
    help_text = render_template('help')
    welcome_repeat_text = render_template('welcome_repeat')

    return question(help_text).reprompt(welcome_repeat_text).simple_card(
        app_name, help_text)


@ask.intent('AMAZON.StopIntent')
@ask.intent('AMAZON.CancelIntent')
def stop():
    bye_text = render_template('bye')

    return statement(bye_text)


@ask.intent('EatMeIntent')
def yelp():
    yelp = Yelp(
        app_id=os.environ.get("YELP_APP_ID"),
        app_secret=os.environ.get("YELP_APP_SECRET"),
        app_access_token=os.environ.get("YELP_ACCESS_TOKEN")
    )

    biz = yelp.run(term='restaurant', location='92683')
    miles = int(biz['distance'] / 1609.344)
    # print(biz)
    statement_text = render_template(
        'answer',
        name=biz['name'],
        stars=biz['rating'],
        reviews=biz['review_count'],
        miles=miles,
        address=', '.join(biz['location']['display_address'])
    )
    statement_text = statement_text.replace('&', 'and')
    next_statement = render_template('answer_repeat')
    print(statement_text)

    return question(statement_text).reprompt(next_statement).simple_card(app_name, statement_text)


@app.route('/')
def healthcheck():
    return 'ok'


@ask.session_ended
def session_ended():
    return statement('')


@app.errorhandler(VerificationError)
def failed_verification(error):
    print(error)
    return str(error), 400


@app.errorhandler(Exception)
def global_exception(error):
    print(error)
    return statement('')


def main():
    app.run()


if __name__ == '__main__':
    main()
