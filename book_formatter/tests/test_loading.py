import json
import pytest
from book_formatter.book_formatter import PhotoRecord, PhotoCollection


@pytest.fixture
def records():
    return json.loads("""[
    {"fileName": "1"},
    {"fileName": "2.NEF", "scientificName": "?",
        "commonName": "foobar", "rating": 3},
    {"fileName": "3.NEF", "scientificName": "Foo bar",
        "commonName": "foobar", "rating": 4},
    {"fileName": "4.jpg", "scientificName": "Foo bar",
        "commonName": "foobarx", "rating": 3, "location": "front yard"},
    {"fileName": "5.jpg", "scientificName": "Foo bar2",
        "rating": 3, "location": "back yard"},
    {"fileName": "6.jpg", "scientificName": "Foo bar2",
        "rating": 3, "invasive": "Yes", "location": "front yard"},
    {"fileName": "7.jpg", "scientificName": "Foo bar2",
        "rating": 3, "invasive": "No", "plantType": "forbs"},
    {"fileName": "8.NEF", "scientificName": "Foo bar3",
        "commonName": "foobar", "rating": 4, "plantType": "forbs"},
    {"fileName": "9.jpg", "scientificName": "Foo bar3",
        "commonName": "foobarx", "rating": 3, "plantType": "trees"},
    {"fileName": "10.NEF", "scientificName": "Foo bar4", "rating": 4,
        "commonName": "foobar", "plantType": "forbs"},
    {"fileName": "11.NEF", "scientificName": "Foo bar4", "rating": 3}
]""")


@pytest.fixture
def photos(records):
    pc = PhotoCollection(records)
    for r in pc.plant_records:
        print(r)
    return PhotoCollection(records)


def test_filename_no_ext(records):
    assert PhotoRecord(records[0]).filename == '1.jpg'


def test_filename_ext(records):
    assert PhotoRecord(records[1]).filename == '2.jpg'


def test_no_rating(records):
    assert PhotoRecord(records[0]).rating == 0


def test_qmark(records):
    assert not PhotoRecord(records[0]).scientific_name


def test_unidentified(photos):
    assert len(photos.unidentified_photos) == 2


def test_plant_count(photos):
    assert len(photos.plant_records) == 4


def test_common_name_conflict(photos):
    r = photos.get_plant_record('Foo bar')
    assert 'foobar' == r.common_name
    assert 'Common name mismatch: foobarx != foobar' in r.errors


def test_missing_common_name(photos):
    r = photos.get_plant_record('Foo bar2')
    assert not r.common_name
    assert 'Missing common name' in r.errors


def test_invasive(photos):
    assert photos.get_plant_record('Foo bar2').invasive


def test_not_invasive(photos):
    assert not photos.get_plant_record('Foo bar').invasive


def test_plant_type(photos):
    assert "forbs" == photos.get_plant_record('Foo bar2').plant_type


def test_missing_plant_type(photos):
    assert 'Missing plant type' in photos.get_plant_record('Foo bar').errors


def test_plant_type_mismatch(photos):
    r = photos.get_plant_record('Foo bar3')
    assert 'forbs' == r.plant_type
    assert 'Plant type mismatch: trees != forbs' in r.errors


def test_location(photos):
    assert 2 == len(photos.get_plant_record('Foo bar2').locations)


def test_missing_location(photos):
    assert 'Missing location' in photos.get_plant_record('Foo bar3').errors


def test_empty_common_name_is_ok(photos):
    r = photos.get_plant_record('Foo bar4')
    assert 'Common name mismatch: None != foobar' not in r.errors


def test_empty_plant_type_is_ok(photos):
    r = photos.get_plant_record('Foo bar4')
    assert 'Plant type mismatch: None != forbs' not in r.errors
