import requests, json, requests_cache
from config import OMO_KEY, OMO_URL

requests_cache.install_cache('requests_cache', allowable_codes=(200, 404))


def getMap(externalid):
    data = False

    response = requests.get(f'{OMO_URL}/maps/external/{externalid}',
                            headers={'Authorization': f'Token {OMO_KEY}', 'Accept': '*/*'})
    if response.status_code == 200:
        data = json.loads(response.content)
    return data


def getGeoReference(id):
    data = False
    response = requests.get(f'{OMO_URL}/maps/{id}/georeferences',
                            headers={'Authorization': f'Token {OMO_KEY}', 'Accept': '*/*'})
    if response.status_code == 200:
        data = json.loads(response.content)
    return data


def getDimensions(iiif_url):
    data = False
    response = requests.get(iiif_url, headers={})
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
        #print(mapdata)
        rec['cdm'] = r
        rec['omo'] = {}
        rec['omo']['id'] = mapdata['id']
        rec['omo']['collection_id'] = mapdata['collection_id']
        rec['omo']['image_url'] = mapdata['image_url']
        rec['omo']['is_reviewed'] = mapdata['is_reviewed']
        iiifdata = getDimensions(mapdata['image_url'])
        if iiifdata:
            rec['omo']['width'] = iiifdata['width']
            rec['omo']['height'] = iiifdata['height']
        else:
            rec['omo']['width'] = 0
            rec['omo']['height'] = 0
        cdmiiifdata = getDimensions(r['iiif'])
        if iiifdata:
            rec['cdm']['width'] = cdmiiifdata['width']
            rec['cdm']['height'] = cdmiiifdata['height']
        else:
            rec['cdm']['width'] = 0
            rec['cdm']['height'] = 0
        grdata = getGeoReference(mapdata['id'])
        if grdata:
            num = 0
            rec['omo']['num_items'] = len(grdata['items'])
            rec['georeferences'] = []
            for item in grdata['items']:
                if len(item['gcps'])>0:
                    ref = {'id': item['id'], 'cutline': item['cutline'], 'gcps': item['gcps']}
                    rec['georeferences'].append(ref)
                    num += 1
                else:
                    print(mapdata['id'])
            rec['omo']['num_georeferences'] = num
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
