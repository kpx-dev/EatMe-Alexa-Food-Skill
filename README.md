# EatMe - Alexa Food Skill
EatMe is an Alexa Food Skill that allow you to find good random place to eat near you, quickly. It's powered by Yelp.

<iframe width="560" height="315" src="https://www.youtube.com/embed/CJoA8alJ-K0" frameborder="0" allowfullscreen></iframe>

## Alexa Commands

You: Alexa, Enable the EatMe skill

You: Alexa, ask Eat Me where to eat?

Alexa: Try Glee Donuts and Burgers with 5 stars rating, 719 reviews, 3 miles from you.
Again, the place name is Glee Donuts and Burgers. Address is 9475 Heil Ave
Ste A, Fountain Valley, CA 92708

Alexa: Try Glee Donuts and Burgers, located at 9475 Heil Ave, Ste A, Fountain Valley, CA 92708

## How to make EatMe better?

```shell
  # install virtualenv
  virtualenv --python=python3 env

  # activate virtualenv
  . env/bin/activate

  # install packages
  pip install -r requirements.txt

  # generate your Yelp Access Token, that token should be good for 180 days
  curl "https://api.yelp.com/oauth2/token" \
  --form "grant_type=client_credentials" \
  --form "client_id=$CLIENT_ID" \
  --form "client_secret=$CLIENT_SECRET"

  # copy the sample .env file
  cp env-sample .env
```
