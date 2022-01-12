import json


# https://raw.githubusercontent.com/allmaps/iiif-map-collections/master/georeferencing-annotations/ubvu-cdm21033-krt-2170.json

def createAnnotationPage(rec):
    items = []
    i = 0
    while i < len(rec['georeferences']):
        page = createAnnotation(rec, index=i)
        page['target']['type'] = 'Image'
        page['target']['source'] = f'{page["target"]["source"]}/full/full/0/default.jpg'
        items.append(page)
        i += 1

    return {'type': 'AnnotationPage',
            '@context': [
                "http://geojson.org/geojson-ld/geojson-context.jsonld",
                "http://iiif.io/api/presentation/3/context.json"
            ],
            'items': items}


def createAnnotation(rec, index=0):
    shrink_factor = rec['cdm']['width'] / rec['omo']['width']  # images in Cdm have been resized!

    points = []
    for coord in rec['georeferences'][index]['cutline']:
        points.append(f'{int(round(coord[0] * shrink_factor))},{int(round(coord[1] * shrink_factor))}')
    cutline_str = ' '.join(points)
    image_width = int(round(rec["omo"]["width"] * shrink_factor))
    image_height = int(round(rec["omo"]["height"] * shrink_factor))
    selector = f'<svg width=\"{image_width}\" height=\"{image_height}\"><polygon points=\"{cutline_str}\" /></svg>'

    features = []
    for cp in rec['georeferences'][index]['gcps']:
        f = {
            'type': 'Feature',
            'properties': {
                'pixelCoords': [int(round(cp['pixel'][0] * shrink_factor)), int(round(cp['pixel'][1] * shrink_factor))]
            },
            'geometry': {
                'type': 'Point',
                'coordinates': cp['location']
            }
        }
        features.append(f)

    return {
        "type": "Annotation",
        "@context": [
            "http://geojson.org/geojson-ld/geojson-context.jsonld",
            "http://iiif.io/api/presentation/3/context.json"
        ],
        "target": {
            "source": rec['cdm']['iiif'],
            "service": [
                {
                    '@id': rec['cdm']['iiif'],
                    'type': 'ImageService2',
                    'profile': 'http://iiif.io/api/image/2/level2.json'
                }
            ],
            "selector": {
                "type": "SvgSelector",
                "value": selector
            }
        },
        "body": {
            "type": "featureCollection",
            "features": features
        }
    }


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
