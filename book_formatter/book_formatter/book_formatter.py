import dateutil.parser
import imagesize
import os
from snippets.snippets import SnippetGrabber


OUTPUT_DIR = '/Users/gkreftin/temp/'


class PhotoRecord:
    def __init__(self, r):
        if 'scientificName' in r and r['scientificName'] != '?':
            self.scientific_name = r['scientificName']
        else:
            self.scientific_name = None
        self.common_name = r.get('commonName')
        self.nativity = r.get('nativity')
        self.plant_type = r.get('plantType')
        self.location = r.get('location')
        self.rating = r.get('rating', 0)
        self.filename = os.path.splitext(r['fileName'])[0] + '.jpg'
        try:
            self.date = dateutil.parser.isoparse(
                r.get('dateTime', '')
            ).strftime("%B %-d, %Y")
        except ValueError:
            self.date = None

    def init_image_sizes(self, path):
        self.width, self.height = imagesize.get(
            os.path.join(path, 'images', self.filename)
        )
        self.thumbnail_width, self.thumbnail_height = imagesize.get(
            os.path.join(path, 'thumbs', self.filename)
        )


class PlantRecord:

    def __init__(self, records):
        self.scientific_name = records[0].scientific_name
        self.common_name = None
        self.plant_type = None
        self.locations = set()
        self.photo_records = []
        self.errors = set()
        self.snippet = None
        self.nativity = None

        records.sort(key=lambda r: r.rating, reverse=True)
        for r in records:
            if r.common_name and not self.common_name:
                self.common_name = r.common_name
            elif r.common_name and r.common_name != self.common_name:
                self.errors.add(
                    'Common name mismatch: %s != %s'
                    % (r.common_name, self.common_name))

            if r.nativity and not self.nativity:
                self.nativity = r.nativity
            elif r.nativity and r.nativity != self.nativity:
                self.errors.add(
                    'Nativity mismatch: %s != %s'
                    % (r.nativity, self.nativity))

            if r.plant_type and not self.plant_type:
                self.plant_type = r.plant_type
            elif r.plant_type and r.plant_type != self.plant_type:
                self.errors.add(
                    'Plant type mismatch: %s != %s'
                    % (r.plant_type, self.plant_type))

            if r.location:
                self.locations.add(r.location)

            if r.rating > 0 or len(self.photo_records) == 0:
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

    def init_image_sizes(self, path):
        for r in self.plant_records:
            for photo in r.photo_records:
                photo.init_image_sizes(path)

    def init_snippets(self, path):
        sg = SnippetGrabber(os.path.join(path, 'snippets'))
        for r in self.plant_records:
            r.snippet = sg.get_snippet(r.scientific_name)

    def get_plant_record(self, scientific_name):
        for r in self.plant_records:
            if r.scientific_name == scientific_name:
                return r
        return None

    def get_plants_by_type(self, plant_type):
        return [r for r in self.plant_records if r.plant_type == plant_type]

    def get_plants_by_location(self, location):
        return [r for r in self.plant_records if location in r.locations]
