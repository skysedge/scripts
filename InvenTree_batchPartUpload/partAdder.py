import requests

inventreeURL = 'http://172.16.0.156/api/part/'   

partData = {
    "active": true,
    "assembly": true,
    "category": 0,
    "component": true,
    "creation_user": 0,
    "default_expiry": 2147483647,
    "default_location": 0,
    "default_supplier": 0,
    "description": "test part",
    "image": "http://example.com",
    "remote_image": "http://example.com",
    "existing_image": "string",
    "IPN": "string",
    "is_template": true,
    "keywords": "string",
    "last_stocktake": "2019-08-24",
    "link": "http://example.com",
    "minimum_stock": 0.1,
    "name": "string",
    "notes": "string",
    "purchaseable": true,
    "revision": "string",
    "salable": true,
    "trackable": true,
    "units": "string",
    "variant_of": 0,
    "virtual": true,
    "responsible": 0,
    "tags": [
        "string"
    ]
}

x = requests.post(inventreeURL, json = partData)

print(x.text)
