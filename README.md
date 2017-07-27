# EatMe - Alexa Food Skill
EatMe is an Alexa Food Skill that allow you to find good random place to eat near you, quickly. It's powered by Yelp.

![logo](assets/eatme_logo_108.png)

## Video Demo
[![EatMe Demo](http://img.youtube.com/vi/CJoA8alJ-K0/0.jpg)](http://www.youtube.com/watch?v=CJoA8alJ-K0)

## Alexa Commands

**You**: Alexa, Enable the EatMe skill

**You**: Alexa, ask Eat Me where to eat?

**Alexa**: Try Glee Donuts and Burgers with 5 stars rating, 719 reviews, 3 miles from you.
Again, the place name is Glee Donuts and Burgers. Address is 9475 Heil Ave
Ste A, Fountain Valley, CA 92708

## Make EatMe better

```shell
  # install virtualenv
  virtualenv --python=python3 env

  # activate virtualenv
  source env/bin/activate

  # install packages
  ./scripts/install

  # generate your Yelp Access Token, that token should be good for 180 days
  curl -X POST -d \
  --form "grant_type=client_credentials" \
  --form "client_id=$CLIENT_ID" \
  --form "client_secret=$CLIENT_SECRET" \
  "https://api.yelp.com/oauth2/token"

  # start Lambda function locally
  ./scripts/start

```

## Deploy

This service uses AWS SAM which uses CloudFormation to create resources.

```shell
  # deploy
  ./scripts/deploy

  # tail the log to debug
  ./scripts/tail

```

## Encrypt Environment Keys

```shell
  # encrypt secret environment variable
  ./scripts/encrypt "SECRET_VALUE"

```