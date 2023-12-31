""" Classes for photo records and photo collections
TODO a lot of inconsistencies in the "init" methods,
"update" methods, and "get" methods.  Need to clean up
"""
import dateutil.parser
import imagesize
import os
from book_formatter.values import (
    PLANTING_TYPES, LOCATIONS
)
from snippets.snippets import SnippetGrabber
from sortedcontainers import SortedSet


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
        self.safe_filename = self.filename.replace(' ', '%20')
        try:
            self.date = dateutil.parser.isoparse(
                r.get('dateTime', '')
            ).strftime("%B %-d, %Y")
        except ValueError:
            self.date = None
        try:
            self.datetime = dateutil.parser.isoparse(
                r.get('dateTime', '')
            ).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            self.datetime = None
        self.introduced = r.get('introduced')
        self.introduction_year = r.get('introductionYear')
        self.notes = r.get('notes')
        self.location_description = r.get('locationDescription')
        self.caption = r.get('caption')
        self.idConfidence = r.get('idConfidence')
        self.location_line = self._init_location_line()
        self.introduction_line = self._init_introduction_line()

    def init_image_sizes(self, path):
        self.width, self.height = imagesize.get(
            os.path.join(path, 'images', self.filename)
        )
        self.thumbnail_width, self.thumbnail_height = imagesize.get(
            os.path.join(path, 'thumbs', self.filename)
        )

    def _init_location_line(self):
        if self.location:
            o = LOCATIONS[self.location]
            if self.location_description:
                o += ' (' + self.location_description + ')'
            return o
        return None

    def _init_introduction_line(self):
        if self.introduced and self.introduction_year:
            return '%s (%s)' % (PLANTING_TYPES[self.introduced],
                                self.introduction_year)
        return None


class PlantRecord:
    def _update_introduced_lines(self, r):
        if r.introduced and r.introduction_year:
            self.introduced_lines.add('%s (%s)' % (
                PLANTING_TYPES[r.introduced], r.introduction_year))
        elif r.introduced == 'preexistent':
            self.introduced_lines.add(PLANTING_TYPES[r.introduced])
        elif r.introduced or r.introduction_year:
            self.errors.add('introduced and introduction_year both required')

    def _finalize_introduced_lines(self):
        if len(self.introduced_lines) == 1 and \
                self.introduced_lines[0] == 'Preexistent':
            self.introduced_lines = []

    def _update_notes(self, r):
        if r.notes and not self.notes:
            self.notes = r.notes
        elif r.notes and r.notes != self.notes:
            self.errors.add('Notes fields should be combined')

    def _update_common_name(self, r):
        if r.common_name and not self.common_name:
            self.common_name = r.common_name
        elif r.common_name and r.common_name != self.common_name:
            self.errors.add(
                'Common name mismatch: %s != %s'
                % (r.common_name, self.common_name))

    def _update_location(self, r):
        if r.location:
            self.locations.add(r.location)
            if r.location_description:
                if r.location not in self.location_descriptions:
                    self.location_descriptions[r.location] = []
                self.location_descriptions[r.location].append(
                    r.location_description)

    def _update_updated_datetime(self, r):
        if self.updated_datetime is None:
            self.updated_datetime = r.datetime
        elif r.datetime is not None and r.datetime > self.updated_datetime:
            self.updated_datetime = r.datetime

    def _error_check(self):
        if self.common_name is None:
            self.errors.add('Missing common name')

        if self.plant_type is None:
            self.errors.add('Missing plant type')

        if len(self.locations) == 0:
            self.errors.add('Missing location')

    def __init__(self, records):
        self.scientific_name = records[0].scientific_name
        self.common_name = None
        self.plant_type = None
        self.locations = set()
        self.location_descriptions = {}
        self.photo_records = []
        self.errors = set()
        self.snippet = None
        self.nativity = None
        self.introduced_lines = SortedSet()
        self.notes = None
        self.idConfidence = None
        self.updated_datetime = None

        records.sort(key=lambda r: r.rating, reverse=True)
        for r in records:
            self._update_common_name(r)
            self._update_notes(r)

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
            self._update_location(r)

            if r.rating > 0 or len(self.photo_records) == 0:
                self.photo_records.append(r)

            if r.idConfidence and not self.idConfidence:
                self.idConfidence = r.idConfidence
            elif r.idConfidence and r.idConfidence != self.idConfidence:
                self.errors.add(
                    'ID Confidence mismatch: %s != %s'
                    % (r.idConfidence, self.idConfidence))

            self._update_introduced_lines(r)
            self._update_updated_datetime(r)
        self._finalize_introduced_lines()
        self._error_check()

    def get_location_csv(self):
        return ', '.join({LOCATIONS[loc] for loc in self.locations})

    def get_location_csv_old(self):
        t = set()
        for location in self.locations:
            o = LOCATIONS[location]
            if location in self.location_descriptions:
                o += ' (' + ', '.join(
                    self.location_descriptions[location]
                ) + ')'
            t.add(o)
        s = ', '.join(t)
        return s

    def get_introduced_lines_csv(self):
        return ', '.join(self.introduced_lines)

    def has_errors(self):
        return len(self.errors) > 0


class PhotoCollection():
    def __init__(self, raw_records):
        self.grouped_photos = {}
        self.unidentified_photos = []
        self.best_photos = {}
        self.plant_records_by_filename = {}
        self.plant_records = []

        # Loop through the raw records and group them by scientific name
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

        # Loop through the grouped photos and create PlantRecords
        # Also keep track of the best photos
        for scientific_name in self.scientific_names:
            photo_group = self.grouped_photos[scientific_name]
            plant_record = PlantRecord(photo_group)
            self.plant_records.append(plant_record)
            for photo_record in photo_group:
                if photo_record.rating > 3:
                    self.best_photos[photo_record.filename] = photo_record
                self.plant_records_by_filename[photo_record.filename] = \
                    plant_record

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

    def get_latest_plants(self):
        s = sorted(
            [r for r in self.plant_records if r.updated_datetime is not None],
            key=lambda r: r.updated_datetime, reverse=True)
        return s[:20]

    def get_plants_by_id_confidence(self, conf):
        return [r for r in self.plant_records if r.idConfidence == conf]
