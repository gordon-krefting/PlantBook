import json
import os


class PhotoRecord:
    scientific_name = None
    common_name = None

    def __init__(self, r):
        if 'scientificName' in r and r['scientificName'] != '?':
            self.scientific_name = r['scientificName']
        self.common_name = r.get('commonName')
        self.rating = r.get('rating', 0)
        self.filename = os.path.splitext(r['fileName'])[0] + '.jpg'


class PlantRecord:
    scientific_name = None
    common_name = None
    invasive = None
    plant_type = None
    location = set()
    photos = []
    errors = []

    def __init__(self, records):
        self.scientific_name = records[0].scientific_name
        records.sort(key=lambda r: r['rating'])
        for r in records:
            self.common_name = r.common_name or self.common_name
            self.invasive = r.invasive == "Yes" or self.invasive
            self.photos.append(r.filename)


def main():
    f = open('/Users/gkreftin/temp/PhotoBook.json')
    raw_records = json.load(f)
    f.close()

    grouped_photos = {}
    unidentified_photos = []

    for r in raw_records:
        photo_record = PhotoRecord(r)
        key = photo_record.scientific_name
        if not key:
            unidentified_photos.append(photo_record)
        else:
            if key not in grouped_photos:
                grouped_photos[key] = []
            grouped_photos[key].append(r)

    scientific_names = list(grouped_photos.keys())
    scientific_names.sort()
    print(json.dumps(scientific_names, indent=1))


if __name__ == "__main__":
    main()
