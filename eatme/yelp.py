import requests
import random


class Yelp(object):

    def __init__(self, app_id, app_secret, app_access_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_access_token = app_access_token
        self.host = 'https://api.yelp.com/v3'
        self.default = {
            'radius': 4828,  # meters, 3 miles
            'limit': 50
        }

    def request(self, path, params={}):
        def _make_request(params):
            url = '{}/{}'.format(self.host, path)
            headers = { 'Authorization': 'Bearer {}'.format(self.app_access_token) }

            return requests.get(url=url, headers=headers, params=params)

        res = _make_request(params=params)

        # check for expired access token:
        if res.status_code == 401:
            print('Yelp token expired....')
            auth_url = 'https://api.yelp.com/oauth2/token'
            auth_params = {
                'grant_type': 'client_credentials',
                'client_id': self.app_id,
                'client_secret': self.app_secret
            }
            auth_res = requests.post(url=auth_url, data=auth_params).json()
            self.app_access_token = auth_res.get('access_token')
            res = _make_request(params=params)

        return res.json()

    def search(self, term, location):
        path = 'businesses/search'

        params = {
            'term': term,
            'location': location,
            'limit': self.default['limit'],
            'radius': self.default['radius'],
            'open_now': True,
            'categories': 'food',
            'sort_by': 'rating' #  best_match, rating, review_count or distance
            # 'sort_by': 'review_count', #  best_match, rating, review_count or distance
            # 'attributes': 'cashback'
            # 'hot_and_new': True, # - Hot and New businesses
            # request_a_quote - Businesses have the Request a Quote feature
            # waitlist_reservation - Businesses that have an online waitlist
            # cashback - Businesses that offer Cash Back
            # deals - Businesses that offer Deals
        }

        return self.request(path, params=params)

    def run(self, term, location):
        min_rating = 4
        max_try = 10
        current_try = 0

        response = self.search(term, location)
        businesses = response.get('businesses')

        while True:
            current_try += 1
            random_biz_index = random.randint(0, len(businesses) - 1)
            biz = businesses[random_biz_index]

            if float(biz['rating']) >= min_rating or current_try > max_try:
                return biz
