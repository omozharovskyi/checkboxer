import json
import http.client
from config import *
import mysql.connector
from mysql.connector import errorcode
import argparse
import sys
import re
import logging
from datetime import timedelta, date
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
            logging.debug(f"Failure to complete request:{response.status}: {response.reason}")
            raise HTTPError(f'{response.status}: {response.reason}')
        logging.debug("Data from API requested successfully")
        response_data = response.read()
        return json.loads(response_data.decode())

    def get_order_list(self):
        yesterday_date = str(date.today() - timedelta(days=1)) + "T00:00:00"
        url = f'/api/v1/orders/list?date_from={yesterday_date}&limit=100'
        logging.debug(f"Requesting: {url}")
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
                logging.debug("Wrong username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.debug("Database does not exist")
            else:
                logging.debug(err)
            logging.debug("Failure with connection to data base")
            return False
        else:
            logging.debug("Successfully connected to data base")
            return True

    def disconnect_db(self):
        logging.debug("Disconnecting from data base")
        self.context.close()

    def insert_order(self, order_create_date, order_id, order_summ):
        cursor = self.context.cursor()
        insert_sql_query = 'INSERT IGNORE INTO orders_list (create_date, order_id, order_sum) VALUES (%s, %s, %s)'
        try:
            cursor.execute(insert_sql_query, (order_create_date, order_id, order_summ))
            self.context.commit()
            logging.debug("Order information inserted in data base")
        except mysql.connector.Error as err:
            logging.debug(f"Failure upon inserting order information in data base:\n{err}")
        cursor.close()


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]: %(message)s')
    args = init_parameters()
    api_client = PromuaAPIClient(PROM_KEY, PROM_HOST)
    db_client = MySQLClient(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
    db_client.connect_db()
    if args.mode == 'fetch':
        orders = api_client.get_order_list()
        logging.debug(f"Totally {len(orders['orders'])} orders fetched.")
        for order in orders['orders']:
            logging.debug(f"ID: {order['id']}, date: {order['date_created']}, price: {order['price']}")
            order_price = order['price'][0:-4]
            order_price = re.sub('\s', '', order_price)
            order_price = order_price.replace(",", ".")
            logging.debug(f"Normalized price: '{order_price}'")
            db_client.insert_order(order['date_created'], order['id'], order_price)
    elif args.mode == 'filter':
        pass
    else:
        print("'mode' can be only 'fetch' or 'filter'. Exiting. Use '--help' for detailed info.")
    db_client.disconnect_db()

    # pprint.pprint(api_client.get_order_list())
    # pprint.pprint(api_client.get_orders_status_list())
    # orders_list = api_client.get_order_list()
    # for order in orders_list['orders']:
    #     pprint.pprint(order['status_name'])


if __name__ == '__main__':
    main()
