# checkboxer
Checkboxer is semi-automatic solution, made for those who taking 
small business in Ukraine making sales via Prom.UA marketplace. Ukrainian 
law and tax authorities require to issue sale receipt for each dale.
In case of few purchases per day, solution via checkbox.ua is good 
and nice. But in case of 20+ purchases with 5+ positions in order, making
sale receipts can be messy.

Checkboxer interacts with prom.ua marketplace and checkbox.ua sale receipts 
integrator using open API of both services.

Checkboxer will require API-key from your prom.ua account with rights to read
orders data.

Checkboxer also will require checkbox.ua cashier login and password. For this
cashier account electronic digital signature should be uploaded to checkbox.ua cloud.
Account which works via mobile checkbox.ua application usually fits this requirements, 
if step out from technical details.

## Solution concept
Checkboxer consist of following parts:
- [check_creator](./check_creator/README.md) - Python script that designed to run only 
once at end of day. Its creates sale receipts for all sales made during day.
- [payment_checker](./payment_checker/README.md) - optional Python script to check bank account
for incoming payments, that corresponds to sale. Should be run periodically during day, to have up-to-date data.
Only PrivatBank and Monobank expected to be supported.
- [promua_fetcher](./promua_fetcher/README.md) - Python script, that saves orders numbers from 
prom.ua portal according to filter criteria , for further processing by [check_creator](./check_creator/README.md)
at end of day. Should be run periodically during day, to have up-to-date data.
- [sql](./sql/README.md) - sql structure of data base, required for solution
- [unit_tests](./unit_tests/README.md) - unit tests for each component to use during expected CI/CD process
- [web_frontend](./web_frontend/README.md) - user interface for Checkboxer. Can be used to manually enter order numbers 
and payment amount, view previously created sales receipts. Also verification and correction of auto fetched order 
numbers (by [promua_fetcher](./promua_fetcher/README.md)) and auto filled payed 
(by [payment_checker](./payment_checker/README.md)) amount for sale can be done via this user interface.

### Run flow
1. During day [promua_fetcher](./promua_fetcher/README.md) periodically loads data from sale platform Prom.UA
2. During day [payment_checker](./payment_checker/README.md) periodically check incoming payments to verify whether 
order got payed.
3. During day owner/operator/manager using [web_frontend](./web_frontend/README.md) ensures and correct
in case of non-standard situations) data.
4. At the end of the business day [check_creator](./check_creator/README.md) proceeds all confirmed orders and creates
sales receipts for each order. Delivery sales receipts to client made by checkbox.ua sale receipts integrator.
5. Next day, in case of client request, corresponding sale receipt can be found and forwarded to client as web-link 
or document.

## Requirements
Python 3.10 required to run application.

## Installation
TBD - solution expected to be installed on cloud platform(AWS/Azure/Google)

## Usage
TBD - solution expected to be installed and configured on cloud platform(AWS/Azure/Google). Web interface should 
be accessed for usage.
