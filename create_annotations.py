import json


# https://raw.githubusercontent.com/allmaps/iiif-map-collections/master/georeferencing-annotations/ubvu-cdm21033-krt-2170.json

def createAnnotationPage(rec):
    d = {}
    d['type'] = 'AnnotationPage'
    d['@context'] = [
        "http://geojson.org/geojson-ld/geojson-context.jsonld",
        "http://iiif.io/api/presentation/3/context.json"
    ]
    items = []
    i = 0
    while i < len(rec['georeferences']):
        print(i, len(rec['georeferences']))
        page = createAnnotation(rec, index=i)
        page['target']['type'] = 'Image'
        page['target']['source'] = f'{page["target"]["source"]}/full/full/0/default.jpg'
        items.append(page)
        i += 1
    d['items'] = items
    return d


def createAnnotation(rec, index=0):
    shrink_factor = rec['cdm']['width'] / rec['omo']['width']  # images in Cdm have been resized!
    d = {}
    d['type'] = 'Annotation'
    d['@context'] = [
        "http://geojson.org/geojson-ld/geojson-context.jsonld",
        "http://iiif.io/api/presentation/3/context.json"
    ]
    d["motivation"]: "georeference"
    d['target'] = {}
    d['target']['source'] = rec['cdm']['iiif']
    d['target']['service'] = []
    service = {}
    service['@id'] = rec['cdm']['iiif']  # wanneer heb je hier meer van?
    service['type'] = 'ImageService2'
    service['profile'] = 'http://iiif.io/api/image/2/level2.json'
    d['target']['service'].append(service)
    d['target']['selector'] = {}
    d['target']['selector']['type'] = 'SvgSelector'

    points = []
    for coord in rec['georeferences'][index]['cutline']:
        points.append(f'{int(round(coord[0] * shrink_factor))},{int(round(coord[1] * shrink_factor))}')
    cutline_str = ' '.join(points)
    image_width = int(round(rec["omo"]["width"] * shrink_factor))
    image_height = int(round(rec["omo"]["height"] * shrink_factor))
    d['target']['selector'][
        'value'] = f'<svg width=\"{image_width}\" height=\"{image_height}\"><polygon points=\"{cutline_str}\" /></svg>'

    d['body'] = {}
    d['body']['type'] = 'featureCollection'
    d['body']['features'] = []
    for cp in rec['georeferences'][index]['gcps']:
        f = {}
        f['type'] = 'Feature'
        f['properties'] = {}
        f['properties']['pixelCoords'] = [int(round(cp['pixel'][0] * shrink_factor)),
                                          int(round(cp['pixel'][1] * shrink_factor))]
        f['geometry'] = {}
        f['geometry']['type'] = 'Point'
        f['geometry']['coordinates'] = cp['location']
        d['body']['features'].append(f)
    return d


def store(annot, is_reviewed):
    if is_reviewed:
        folder = 'annotations'
    else:
        folder = 'annotations_unreviewed'
    with open(f'{folder}/ubvu_{id}.json', 'w') as f:
        json.dump(annot, f, indent=4)


fin = open('ubvu_maps.json', 'r')
data = json.load(fin)
out = {}
found = 0
grfound = 0
notfound = 0
for id in data:
    print(id)
    if data[id]['omo']['num_georeferences'] == 1:
        annot = createAnnotation(data[id])
        store(annot, data[id]['omo']['is_reviewed'])
    elif data[id]['omo']['num_georeferences'] > 1:
        annot = createAnnotationPage(data[id])
        store(annot, data[id]['omo']['is_reviewed'])
