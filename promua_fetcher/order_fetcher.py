import json
import http.client
from config import *
import mysql.connector
from mysql.connector import errorcode
import argparse
import sys
import pprint

__version__ = '0.1'


def init_parameters() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Script to fetch and filter orders from prom.ua for further processing in semiautomatic mode."
    )
    parser.add_argument("mode", help="fetch - fetches order, filter - check order for defined status.", type=str)
    parser.add_argument("--version", help="Print version info", action='version', version='%(prog)s v.' + __version__)
    return parser.parse_args()


class HTTPError(Exception):
    pass


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
        if response.status != 200:
            raise HTTPError(f'{response.status}: {response.reason}')
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


class MySQLClient(object):
    def __init__(self, server, port, dbname, user, password):
        self.context = None
        self.server = server
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password

    def connect_db(self):
        try:
            self.context = mysql.connector.connect(
                user=self.user,
                password=self.password,
                host=self.server,
                port=self.port,
                database=self.dbname,
                use_pure=False
            )
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Wrong username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            return False
        else:
            return True

    def disconnect_db(self):
        self.context.close()

    def insert_order(self, order_create_date, order_id, order_summ):
        cursor = self.context.cursor()
        insert_sql_query = 'INSERT IGNORE INTO orders_list (create_date, order_id, order_sum) VALUES (%s, %s, %s)'
        cursor.execute(insert_sql_query, (order_create_date, order_id, order_summ))
        self.context.commit()
        cursor.close()

    def get_max_order_id(self):
        cursor = self.context.cursor()
        query = "SELECT MAX(order_id) FROM orders_list"
        cursor.execute(query)
        output = cursor.fetchone()
        if output[0] is None:
            return False
        else:
            return output[0]


def main():
    args = init_parameters()
    api_client = PromuaAPIClient(PROM_KEY, PROM_HOST)
    db_client = MySQLClient(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    db_client.connect_db()

    if args.mode == 'fetch':
        start_order_id = db_client.get_max_order_id()
    elif args.mode == 'filter':
        print('filter')
    db_client.disconnect_db()
    sys.exit("'mode' can be only 'fetch' or 'filter'. Exiting. Use '--help' for detailed info.")

    # pprint.pprint(api_client.get_order_list())
    # pprint.pprint(api_client.get_orders_status_list())
    # orders_list = api_client.get_order_list()
    # for order in orders_list['orders']:
    #     pprint.pprint(order['status_name'])


if __name__ == '__main__':
    main()
