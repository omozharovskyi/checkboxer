import json
import http.client
from config import *
import pprint


class PromuaAPIClient(object):

    def __init__(self, token, host):
        self.token = token
        self.host = host

    def make_request(self, method, url, body=None):
        connection = http.client.HTTPSConnection(self.host)
        headers = {
            'Authorization': 'Bearer {}'.format(self.token),
            'Content-type': 'application/json'
        }
        if body:
            body = json.dumps(body)
        connection.request(method, url, body=body, headers=headers)
        response = connection.getresponse()
        # if response.status != 200:
        #     raise HTTPError('{}: {}'.format(response.status, response.reason))
        response_data = response.read()
        return json.loads(response_data.decode())

    def get_order_list(self):
        url = '/api/v1/orders/list'
        method = 'GET'
        return self.make_request(method, url)

    def get_orders_status_list(self):
        url = '/api/v1/order_status_options/list'
        method = 'GET'
        return self.make_request(method, url)


def main():
    api_client = PromuaAPIClient(PROM_KEY, PROM_HOST)
    pprint.pprint(api_client.get_order_list())


if __name__ == '__main__':
    main()
