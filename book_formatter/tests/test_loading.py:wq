import json
import pytest
from book_formatter.book_formatter import PhotoRecord


records = json.loads("""[
    {"fileName": "1"},
    {"fileName": "2.NEF", "scientificName": "?",
     "commonName": "foobar", "rating": 3}
]""")


@pytest.fixture
def r1():
    return PhotoRecord(records[0])


@pytest.fixture
def r2():
    return PhotoRecord(records[1])


def test_filename_no_ext(r1):
    assert r1.filename == '1.jpg'


def test_filename_ext(r2):
    assert r2.filename == '2.jpg'


def test_no_rating(r1):
    assert r1.rating == 0


def test_qmark(r1):
    assert not r1.scientific_name
