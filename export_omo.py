import requests, requests_cache, json
from collections import defaultdict
import pandas as pd
from config import OMO_KEY, OMO_URL

requests_cache.install_cache('requests_cache', allowable_codes=(200, 404))


def getMap(externalid):
    data = False

    response = requests.get(f'{OMO_URL}/maps/external/{externalid}',
                            headers={'Authorization': f'Token {OMO_KEY}', 'Accept': '*/*'})
    print(response.status_code)
    if response.status_code == 200:
        data = json.loads(response.content)
    return data


def getGeoReference(id):
    data = False
    response = requests.get(f'{OMO_URL}/maps/{id}/georeferences',
                            headers={'Authorization': f'Token {OMO_KEY}', 'Accept': '*/*'})
    print(response.status_code)
    if response.status_code == 200:
        data = json.loads(response.content)
    return data


fin = open('cdm_export.json', 'r')
d = json.load(fin)
out = {}
found = 0
grfound = 0
notfound = 0
for r in d:
    rec = {}
    mapdata = getMap(r['id'])
    if mapdata:
        print(mapdata)
        rec['cdm'] = r
        rec['omo'] = {}
        rec['omo']['id'] = mapdata['id']
        rec['omo']['collection_id'] = mapdata['collection_id']
        rec['omo']['image_url'] = mapdata['image_url']
        rec['omo']['is_reviewed'] = mapdata['is_reviewed']
        grdata = getGeoReference(mapdata['id'])
        print(grdata)
        if grdata:
            rec['omo']['num_georeferences'] = len(grdata['items'])
            rec['georeferences'] = []
            ref={}
            for item in grdata['items']:
                ref['id'] = item['id']
                ref['cutline'] = item['cutline']
                ref['gcps'] = item['gcps']
                rec['georeferences'].append(ref)
            grfound += 1
        else:
            rec['omo']['num_georeferences'] = 0
        found += 1
        out[r['dmrecord']] = rec
    else:
        notfound += 1


with open('ubvu_maps.json', 'w') as f:
    json.dump(out, f, indent=4, sort_keys=True)

print(f'not found: {notfound}, found: {found}, with georeferences: {grfound}')
