### this file will geocode the addresses
import requests
import json

def geocode(hnum, sname, boro, mode='api', columns=['Longitude', 'Latitude']):
    url_prefix = 'http://api-geosupport.planninglabs.nyc:5000/1b?'
    url = f'{url_prefix}house_number={hnum}&street_name={sname}&borough={boro}'
    content = json.loads(requests.get(url).content)
    return {key:content['results'][key] for key in columns}
