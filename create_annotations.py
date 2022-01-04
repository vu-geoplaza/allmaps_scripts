import json
# https://raw.githubusercontent.com/allmaps/iiif-map-collections/master/georeferencing-annotations/ubvu-cdm21033-krt-2170.json

def createAnnotation(rec):
    print(rec)
    d = {}
    d['type'] = 'Annotation'
    d['@context'] = [
        "http://geojson.org/geojson-ld/geojson-context.jsonld",
        "http://iiif.io/api/presentation/3/context.json"
    ]
    d["motivation"]: "georeference"
    d['target'] = {}
    d['target']['source'] = rec['cdm']['iiif']
    d['target']['service']=[]
    service = {}
    service['@id'] = rec['cdm']['iiif']  # wanneer heb je hier meer van?
    service['type'] = 'ImageService2'
    service['profile'] = 'http://iiif.io/api/image/2/level2.json'
    d['target']['service'].append(service)
    d['target']['selector'] = {}
    d['target']['selector']['type'] = 'SvgSelector'
    points = []
    for coord in rec['georeferences'][0]['cutline']:
        points.append(f'{coord[0]},{coord[1]}')
    points_str = ' '.join(points)
    d['target']['selector'][
        'value'] = f'<svg width=\"{rec["omo"]["width"]}\" height=\"{rec["omo"]["height"]}\"><polygon points=\"{points_str}\" /></svg>'
    d['body'] = {}
    d['body']['type'] = 'featureCollection'
    d['body']['features'] = []
    for cp in rec['georeferences'][0]['gcps']:
        f = {}
        f['type'] = 'Feature'
        f['properties'] = {}
        f['properties']['pixelCoords'] = cp['pixel']
        f['geometry'] = {}
        f['geometry']['type'] = 'Point'
        f['geometry']['coordinates'] = cp['location']
        d['body']['features'].append(f)
    print(d)
    return d

fin = open('ubvu_maps.json', 'r')
data = json.load(fin)
out = {}
found = 0
grfound = 0
notfound = 0
for id in data:
    print(id)
    if data[id]['omo']['num_georeferences']>0:
        annot = createAnnotation(data[id])
        with open(f'annotations/ubvu_{id}.json', 'w') as f:
            json.dump(annot, f, indent=4, sort_keys=True)