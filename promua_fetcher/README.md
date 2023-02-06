# promua_fetcher
promua_fetcher is essential part of [checkboxer](../README.md) solution.

## Designed function
Scrip written to fetch and store incoming new order from Prom.UA marketplace.
Ass additional option, filtering by order status name can be applied to fetched orders.

## Requirements
Python 3.10 required to run application.

## Configuring
'config.py' file required to run script with proper configuration.
Sample of config file:
>PROM_KEY = 'uor_prom_ua_api_key'
>
>PROM_HOST = 'my.prom.ua'
> 
>DB_HOST = 'db_host_name_or_ip'
> 
>DB_PORT = 3060
> 
>DB_NAME = 'data_base_name'
> 
>DB_USER = 'data_base_user_name'
> 
>DB_PASS = 'data_base_password'
> 
>PROM_ORDER_FILTER_STATUS_CORRECT = ['array', 'of', 'correct', 'filtered','status names']
> 
>PROM_ORDER_FILTER_STATUS_WRONG = ['these status names', 'will be', 'ignored']

## Usage
Use 'fetch' parameter to get all orders for today and yesterday:
> python promua_fetcher.py fetch

Data structure implementation and request format help to avoid dublication of data in storage data base. 

Use 'filter' to apply filter to saved in storage orders:
> python promua_fetcher.py filter