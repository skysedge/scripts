#!/bin/python3

import requests

import requests
from requests.auth import HTTPBasicAuth

# Your IvenTree username and password
username = 'pierogi'
password = 'inventree4u'

# The URL you want to access
url = 'http://172.16.0.156/api/user/token/'

# Make the GET request with Basic Authentication
response = requests.get(url, auth=HTTPBasicAuth(username, password))

print(response.text)

