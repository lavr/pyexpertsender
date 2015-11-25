from utils import generate_request_xml
import urlparse
import urllib
import requests
from furl import furl
import xmltodict


class PyExpertSender:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.subscribers = PyExpertSender.Subscribers(api_url, api_key)
        self.lists = PyExpertSender.Lists(api_url, api_key)

    class Lists:
        path = '/Api/Lists'

        def __init__(self, api_url, api_key):
            self.api_url = api_url
            self.api_key = api_key

        def parse_xml(self, xml):
            return {
                'id': xml['Id'],
                'name': xml['Name'],
                'friendly_name': xml.get('FriendlyName', ''),
                'language': xml['Language'],
                'opt_in_mode': xml['OptInMode']
            }

        def get(self, seed_lists=False):
            url = furl(self.api_url)
            url.path = self.path
            url.args = {
                'apiKey': self.api_key,
                'seedLists': seed_lists
            }
            return [
                self.parse_xml(x)
                for x in xmltodict.parse(requests.request('GET', url.url).text)['ApiResponse']['Data']['Lists']['List']
            ]

    class Subscribers:
        path = '/Api/Subscribers'

        def __init__(self, api_url, api_key):
            self.api_url = api_url
            self.api_key = api_key

        def get(self, email, option='Long'):
            url = furl(self.api_url)
            url.path = self.path
            url.args = {
                'apiKey': self.api_key,
                'email': email,
                'option': option
            }
            requests.request('GET', url.url)

        def get_subscriber_xml(self, subscriber_data):
            return generate_request_xml(self.api_key, 'Subscriber', subscriber_data)

        def post_one(self, email, list_id, **kwargs):
            data = {
                'email': email,
                'list_id': list_id,
                'firstname': kwargs.get('firstname', ''),
                'lastname': kwargs.get('lastname', ''),
                'name': kwargs.get('name', ''),
                'mode': kwargs.get('mode', 'AddAndUpdate'),

            }

            xml = self.get_subscriber_xml(data)

            url = furl(self.api_url)
            url.path = self.path

            return requests.request(
                'POST',
                url,
                data=xml
            ).text
