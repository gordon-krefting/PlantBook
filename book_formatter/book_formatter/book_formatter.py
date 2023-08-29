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


def main():
    f = open('/Users/gkreftin/temp/PhotoBook.json')
    raw_records = json.load(f)
    f.close()

    for r in raw_records:
        photo_record = PhotoRecord(r)
        print(photo_record)


if __name__ == "__main__":
    main()
