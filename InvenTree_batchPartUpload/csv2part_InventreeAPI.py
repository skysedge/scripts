#!/bin/python3
import copy

import requests
import json

#Supply authentication token
token = 'inv-e2a3fa9fb1ed97057fbfd92342b954cc498cc994-20240713'
headers = {
    'AUTHORIZATION': f'Token {token}'
}

#URL to localhost
inventreeURL = 'http://172.16.0.156/api/part/'   

#Template part data
partData = {
        "active": True,
            "assembly": True,
            "category": 0,
            "component": True,
            "creation_user": 0,
            "default_expiry": 2147483647,
            "default_location": 0,
            "default_supplier": 0,
            "description": "test part",
            "image": "http://example.com",
            "remote_image": "http://example.com",
            "existing_image": "string",
            "IPN": "string",
            "is_template": True,
            "keywords": "string",
            "last_stocktake": "2019-08-24",
            "link": "http://example.com",
            "minimum_stock": 0.1,
            "name": "string",
            "notes": "string",
            "purchaseable": True,
            "revision": "string",
            "salable": True,
            "trackable": True,
            "units": "string",
            "variant_of": 0,
            "virtual": True,
            "responsible": 0,
            "tags": [
                "string"
            ]
}

#POST request to add partData
x = requests.post(inventreeURL, json=json.dumps(partData), headers=headers)

print(x.text)
