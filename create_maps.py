import json


def createMap(rec, index=0):
    print(rec['cdm']['dmrecord'])
    if rec['omo']['width'] > 0:  # dmrecord 2388!!
        shrink_factor = rec['cdm']['width'] / rec['omo']['width']  # images in Cdm have been resized!
    else:
        shrink_factor = 1

    pixelMask = []
    for coord in rec['georeferences'][index]['cutline'][:-1]:
        pixelMask.append([int(round(coord[0] * shrink_factor)), int(round(coord[1] * shrink_factor))])
    gcps = []
    gcp_index=1
    for cp in rec['georeferences'][index]['gcps']:
        gcps.append({
            'id': gcp_index,
            'image': [int(round(cp['pixel'][0] * shrink_factor)), int(round(cp['pixel'][1] * shrink_factor))],
            'world': cp['location']
        })
        gcp_index += 1

    return {
        'version': 1,
        'image': {
            'uri': rec["cdm"]["iiif"],
            'width': int(round(rec["omo"]["width"] * shrink_factor)),
            'height': int(round(rec["omo"]["height"] * shrink_factor)),
            'version': 2
        },
        'pixelMask': pixelMask,
        'gcps': gcps
    }


def store(annot, folder, id):
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
        if reviewed:
            folder = 'maps'
            count_reviewed += 1
        else:
            folder = 'maps_unreviewed'
            count_unreviewed += 1
        i = 0
        maps = []
        while i < num:
            maps.append(createMap(rec=data[id], index=i))
            i += 1
        if i==1:
            store(maps[0], folder, id)
        else:
            store(maps, folder, id)
    else:
        count_unreferenced += 1

print(
    f'{count_reviewed} reviewed georeferences, {count_unreviewed} unreviewed georeferences, {count_unreferenced} images not georeferenced')
