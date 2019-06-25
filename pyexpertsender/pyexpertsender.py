from .utils import generate_request_xml
import requests
from furl import furl
import xmltodict


class PyExpertSender:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.subscribers = PyExpertSender.Subscribers(api_url, api_key)
        self.lists = PyExpertSender.Lists(api_url, api_key)
        self.fields = PyExpertSender.Fields(api_url, api_key)
        self.workflows = PyExpertSender.CustomWorkflows(api_url, api_key)
        self.transactionals = PyExpertSender.TransactionalEmails(api_url, api_key)

    class Lists:
        path = '/v2/Api/Lists'

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
            result = xmltodict.parse(requests.request('GET', url.url).text)['ApiResponse']['Data']['Lists']['List']

            if not isinstance(result, list):
                result = [result]

            return [
                self.parse_xml(x)
                for x in result
            ]

    class Subscribers:
        path = '/v2/Api/Subscribers'

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
            return requests.request('GET', url.url)

        def get_subscriber_xml(self, subscriber_data):
            return generate_request_xml(self.api_key, 'Subscriber', subscriber_data)

        def post_one(self, email, list_id, **kwargs):
            data = dict(email=email, list_id=list_id, **kwargs)
            data.setdefault('properties', kwargs.get('customs', []))  # support for legacy parameter `customs`
            data.setdefault('mode', 'AddAndUpdate')

            for k, v in list(data.items()):
                if v is None:
                    data.pop(k)

            xml = self.get_subscriber_xml(data)

            url = furl(self.api_url)
            url.path = self.path

            r = requests.request(
                'POST',
                url.url,
                data=xml
            )
            return r

    class Fields:
        path = '/v2/Api/Fields'

        def __init__(self, api_url, api_key):
            self.api_url = api_url
            self.api_key = api_key

        def parse_xml(self, xml):
            return {
                'id': xml['Id'],
                'name': xml['Name'],
                'friendly_name': xml.get('FriendlyName', ''),
                'type': xml['Type']
            }

        def get(self, seed_lists=False):
            url = furl(self.api_url)
            url.path = self.path
            url.args = {
                'apiKey': self.api_key
            }
            result = xmltodict.parse(requests.request('GET', url.url).text)['ApiResponse']['Data']['Fields']['Field']
            if not isinstance(result, list):
                result = [result]

            return [
                self.parse_xml(x)
                for x in result
            ]

    class CustomWorkflows:
        path = '/v2/Api/WorkflowCustomEvents'

        def __init__(self, api_url, api_key):
            self.api_url = api_url
            self.api_key = api_key

        def post(self, event_id, email):
            url = furl(self.api_url)
            url.path = self.path

            return requests.request(
                'POST',
                url.url,
                data=generate_request_xml(self.api_key, '', {
                    'Custom_Event_Id': event_id,
                    'Subscriber_Email': email
                })
            )

    class TransactionalEmails:
        path = '/v2/Api/Transactionals/'

        def __init__(self, api_url, api_key):
            self.api_url = api_url
            self.api_key = api_key

        def post(self, email_id, email, snippets):
            url = furl(self.api_url)
            url.path = self.path

            return requests.request(
                'POST',
                url.url + str(email_id),
                data=generate_request_xml(self.api_key, '', {
                    'Receiver': {
                        'Email': email
                    },
                    'Snippets': [
                        {'Snippet':
                            {
                                'Name': k,
                                'Value': v
                            }
                        } for (k, v) in snippets.items()
                    ]
                })
            )
