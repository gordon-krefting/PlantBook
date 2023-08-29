from jinja2 import Environment, PackageLoader

import json
import os

f = open('/Users/gkreftin/temp/PhotoBook.json')
photo_records = json.load(f)
f.close()

# photo records, grouped by scientific name
grouped_photos = {}
unidentified_photos = []

for r in photo_records:
    # we need to sort by rating later, so add one if missing
    if 'rating' not in r:
        r['rating'] = 0

    # we also need to correct the image file extension
    r['fileName'] = os.path.splitext(r['fileName'])[0] + '.jpg'

    # if there's no scientific name, we assume the image is unidentified
    if 'scientificName' not in r:
        key = '?'
    else:
        key = r['scientificName']

    # if the photo has an id, we put it in the correct group
    if not key or '?' in key:
        unidentified_photos.append(r)
    else:
        if key not in grouped_photos:
            grouped_photos[key] = []
        grouped_photos[key].append(r)

scientific_names = list(grouped_photos.keys())
scientific_names.sort()
print(json.dumps(scientific_names, indent=1))

# Normalize the plant records
plants = []
for p in scientific_names:
    # create a new record
    plant = {}
    plant['scientific_name'] = p
    plant['common_name'] = None
    plant['invasive'] = None
    plant['plant_type'] = None
    plant['location'] = set()
    plant['photos'] = []
    plant['errors'] = []
    plants.append(plant)
    common_names = set()

    # Prefer the highest rated image
    grouped_photos[p].sort(key=lambda element: element['rating'], reverse=True)
    for r in grouped_photos[p]:
        if 'commonName' in r:
            common_names.add(r['commonName'])

        plant['photos'].append(r['fileName'])

    # validate common name
    if len(common_names) == 0:
        plant['common_name'] = p
    elif len(common_names) > 1:
        plant['errors'].append('Multiple common names')
    plant['common_name'] = next(iter(common_names))

print(plants)

# Call the template renderer
env = Environment(loader=PackageLoader('book_formatter'))
template = env.get_template('index.jinja2')

with open('/Users/gkreftin/temp/index.html', 'w') as fh:
    fh.write(template.render(
        photo_records=photo_records,
        plants=plants,
        scientific_names=scientific_names,
        unidentified_photos=unidentified_photos,
    ))
