import imagesize
import os


OUTPUT_DIR = '/Users/gkreftin/temp/'


class PhotoRecord:
    def __init__(self, r):
        if 'scientificName' in r and r['scientificName'] != '?':
            self.scientific_name = r['scientificName']
        else:
            self.scientific_name = None
        self.common_name = r.get('commonName')
        self.plant_type = r.get('plantType')
        self.location = r.get('location')
        self.rating = r.get('rating', 0)
        self.invasive = r.get('invasive', 'no')
        self.filename = os.path.splitext(r['fileName'])[0] + '.jpg'

    def init_image_sizes(self):
        self.width, self.height = imagesize.get(
            OUTPUT_DIR + 'images/' + self.filename)
        self.twidth, self.theight = imagesize.get(
            OUTPUT_DIR + 'images/' + self.filename)


class PlantRecord:
    def __init__(self, records):
        self.scientific_name = records[0].scientific_name
        self.common_name = None
        self.invasive = False
        self.plant_type = None
        self.locations = set()
        # deprecate this
        self.photos = []
        self.photo_records = []
        self.errors = set()

        records.sort(key=lambda r: r.rating, reverse=True)
        for r in records:
            if r.common_name and not self.common_name:
                self.common_name = r.common_name
            elif r.common_name and r.common_name != self.common_name:
                self.errors.add(
                    'Common name mismatch: %s != %s'
                    % (r.common_name, self.common_name))

            if r.plant_type and not self.plant_type:
                self.plant_type = r.plant_type
            elif r.plant_type and r.plant_type != self.plant_type:
                self.errors.add(
                    'Plant type mismatch: %s != %s'
                    % (r.plant_type, self.plant_type))
            self.invasive = r.invasive == "yes" or self.invasive

            if r.location:
                self.locations.add(r.location)

            self.photos.append(r.filename)
            self.photo_records.append(r)

        if self.common_name is None:
            self.errors.add('Missing common name')

        if self.plant_type is None:
            self.errors.add('Missing plant type')

        if len(self.locations) == 0:
            self.errors.add('Missing location')


class PhotoCollection():
    def __init__(self, raw_records):
        self.grouped_photos = {}
        self.unidentified_photos = []
        self.plant_records = []

        for r in raw_records:
            photo_record = PhotoRecord(r)
            key = photo_record.scientific_name
            if not key:
                self.unidentified_photos.append(photo_record)
            else:
                if key not in self.grouped_photos:
                    self.grouped_photos[key] = []
                self.grouped_photos[key].append(photo_record)

        self.scientific_names = list(self.grouped_photos.keys())
        self.scientific_names.sort()

        for scientific_name in self.scientific_names:
            self.plant_records.append(
                PlantRecord(self.grouped_photos[scientific_name]))

    def init_image_sizes(self):
        for r in self.plant_records:
            for photo in r.photo_records:
                photo.init_image_sizes()

    def get_plant_record(self, scientific_name):
        for r in self.plant_records:
            if r.scientific_name == scientific_name:
                return r
        return None
