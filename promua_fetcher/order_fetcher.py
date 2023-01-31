import json
import http.client
import time
from promua_fetcher.config import *
import mysql.connector
from mysql.connector import errorcode
import argparse
import re
import logging
from datetime import timedelta, date

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

    def get_order_id_status_name(self, order_id):
        url = f'/api/v1/orders/{order_id}'
        logging.debug(f"Requesting: {url}")
        method = 'GET'
        return self.make_request(method, url)['order']['status_name']


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

    def get_unfiltered_orders(self):
        logging.debug("Requesting from data base list of orders with status 'unconfirmed'")
        cursor = self.context.cursor()
        select_sql_query = "SELECT order_id FROM orders_list WHERE internal_order_status='unconfirmed'"
        try:
            cursor.execute(select_sql_query)
            orders_data = cursor.fetchall()
        except mysql.connector.Error as err:
            logging.debug(f"Failure upon fetching orders from data base:\n{err}")
            return None
        else:
            return orders_data

    def update_order_status(self, order_id, order_status):
        cursor = self.context.cursor()
        update_query = 'UPDATE orders_list SET internal_order_status=%s WHERE order_id=%s'
        try:
            cursor.execute(update_query, (order_status, order_id))
            self.context.commit()
            logging.debug("Order status updated in data base")
        except mysql.connector.Error as err:
            logging.debug(f"Failure upon updating order status in data base:\n{err}")
        cursor.close()


def main():
    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]: %(message)s')
    args = init_parameters()
    logging.debug("'order_fetcher' tool to fetch and filter orders from prom.ua for further processing")
    api_client = PromuaAPIClient(PROM_KEY, PROM_HOST)
    logging.debug("API client created")
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
        wait_orders = db_client.get_unfiltered_orders()
        logging.debug(f"Totally {len(wait_orders)} orders to filter.")
        for order in wait_orders:
            time.sleep(0.5)
            order_status_name = api_client.get_order_id_status_name(order[0])
            if order_status_name in PROM_ORDER_FILTER_STATUS_CORRECT:
                logging.debug(f"Order {order[0]} status: '{order_status_name}'. Updating as 'confirmed' one.")
                db_client.update_order_status(order[0], 'confirmed')
            elif order_status_name in PROM_ORDER_FILTER_STATUS_WRONG:
                logging.debug(f"Order {order[0]} status: '{order_status_name}'. Updating as 'ignored' one.")
                db_client.update_order_status(order[0], 'ignored')
            else:
                logging.debug(f"Order {order[0]} status: '{order_status_name}'. Skipping.")
    else:
        print("'mode' can be only 'fetch' or 'filter'. Exiting. Use '--help' for detailed info.")
    db_client.disconnect_db()


if __name__ == '__main__':
    main()
