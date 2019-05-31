### this file will geocode the addresses
import requests
import json

def geocode(hnum, sname, boro, columns, mode='api'):
    url_prefix = 'https://geosupport.planninglabs.nyc/1B?'
    url = f'{url_prefix}house_number={hnum}&street_name={sname}&borough_code={boro}'
    content = json.loads(requests.get(url).content)
    result = {}
    for key in columns:
        try: 
            result[key] = content[key]
        except:
            result[key] = ''
    return result