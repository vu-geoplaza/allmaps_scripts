import json

CONTEXT = [
    "http://www.w3.org/ns/anno.jsonld",
    "http://geojson.org/geojson-ld/geojson-context.jsonld",
    "http://iiif.io/api/presentation/3/context.json"
]


def createAnnotationPage(rec):
    items = []
    i = 0
    while i < len(rec['georeferences']):
        page = createAnnotation(rec, index=i, is_page=True)
        page['target']['type'] = 'Image'
        page['target']['source'] = f'{page["target"]["source"]}/full/full/0/default.jpg'
        items.append(page)
        i += 1

    return {'type': 'AnnotationPage',
            '@context': CONTEXT,
            'items': items}


def createAnnotation(rec, index=0, is_page=False):
    shrink_factor = rec['cdm']['width'] / rec['omo']['width']  # images in Cdm have been resized!

    points = []
    for coord in rec['georeferences'][index]['cutline'][:-1]:
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

    data = {
        "type": "Annotation",
        "target": {
            "type": "Image",
            **({'@context': CONTEXT} if not is_page else {}),
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
            "type": "FeatureCollection",
            "features": features
        }
    }
    return data


def store(annot, folder):
    with open(f'{folder}/ubvu_{id}.json', 'w') as f:
        json.dump(annot, f, indent=4)


fin = open('ubvu_maps.json', 'r')
data = json.load(fin)
count_unreviewed = 0
count_reviewed = 0
count_unreferenced = 0
for id in data:
    num = data[id]['omo']['num_georeferences']
    if num > 0:
        reviewed = data[id]['omo']['is_reviewed']
        if data[id]['omo']['num_georeferences'] == 1:
            annot = createAnnotation(data[id])
        elif data[id]['omo']['num_georeferences'] > 1:
            annot = createAnnotationPage(data[id])

        if reviewed:
            folder = 'annotations'
            count_reviewed += 1
        else:
            folder = 'annotations_unreviewed'
            count_unreviewed += 1
        store(annot, folder)
    else:
        count_unreferenced += 1

print(
    f'{count_reviewed} reviewed annotations, {count_unreviewed} unreviewed annotations, {count_unreferenced} maps not georeferenced')
