import requests
import random


class Yelp(object):

    def __init__(self, app_id, app_secret, app_access_token):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_access_token = app_access_token
        self.host = 'https://api.yelp.com'
        self.default = {
            'radius': 16093,  # meters, 10 miles
            'limit': 40
        }

    def request(self, path, url_params={}):
        url = '{0}{1}'.format(self.host, path.encode('utf8'))
        headers = {
            'Authorization': 'Bearer %s' % self.app_access_token,
        }

        print('Querying {0} ...'.format(url))
        response = requests.request('GET', url, headers=headers,
                                    params=url_params)

        return response.json()

    def search(self, term, location):
        path = '/v3/businesses/search'

        url_params = {
            'term': term.replace(' ', '+'),
            'location': location.replace(' ', '+'),
            'limit': self.default['limit'],
            'radius': self.default['radius'],
            'open_now': True,
            'categories': 'food',
            # 'attributes': 'cashback'
            # hot_and_new - Hot and New businesses
            # request_a_quote - Businesses have the Request a Quote feature
            # waitlist_reservation - Businesses that have an online waitlist
            # cashback - Businesses that offer Cash Back
            # deals - Businesses that offer Deals
        }

        return self.request(path, url_params=url_params)

    # def get_business(self, business_id):
    #     return request('/v3/businesses/{}'.format(business_id))

    def run(self, term, location):
        response = self.search(term, location)
        businesses = response.get('businesses')
        random.shuffle(businesses)

        return businesses[0]

        # if not businesses:
        #     print(u'No businesses for {0} in {1} found.'.format(term, location))
        #     return
        #
        # business_id = businesses[0]['id']
        #
        # print(u'{0} businesses found, querying business info ' \
        #     'for the top result "{1}" ...'.format(
        #         len(businesses), business_id))
        # response = get_business(bearer_token, business_id)
        #
        # print(u'Result for business "{0}" found:'.format(business_id))
        # pprint.pprint(response, indent=2)

    # def obtain_bearer_token(host, path):
    #     """Given a bearer token, send a GET request to the API.
    #
    #     Args:
    #         host (str): The domain host of the API.
    #         path (str): The path of the API after the domain.
    #         url_params (dict): An optional set of query parameters in the request.
    #
    #     Returns:
    #         str: OAuth bearer token, obtained using client_id and client_secret.
    #
    #     Raises:
    #         HTTPError: An error occurs from the HTTP request.
    #     """
    #     url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    #     assert CLIENT_ID, "Please supply your client_id."
    #     assert CLIENT_SECRET, "Please supply your client_secret."
        # GRANT_TYPE = 'client_credentials'

    #     data = urlencode({
    #         'client_id': CLIENT_ID,
    #         'client_secret': CLIENT_SECRET,
    #         'grant_type': GRANT_TYPE,
    #     })
    #     headers = {
    #         'content-type': 'application/x-www-form-urlencoded',
    #     }
    #     response = requests.request('POST', url, data=data, headers=headers)
    #     bearer_token = response.json()['access_token']
    #     print(bearer_token)
    #     return bearer_token
