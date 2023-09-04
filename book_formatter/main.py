# TODO fix up the paths
import json
import shutil
from book_formatter.book_formatter import PhotoCollection
from book_formatter.values import LOCATIONS, PLANT_TYPES
from jinja2 import Environment, PackageLoader
from os.path import dirname, join as joinpath

OUTPUT_DIR = '/Users/gkreftin/temp/'


def main():
    f = open(OUTPUT_DIR + 'PhotoBook.json')
    raw_records = json.load(f)
    f.close()

    photos = PhotoCollection(raw_records)

    print(json.dumps(photos.scientific_names, indent=1))

    env = Environment(loader=PackageLoader('book_formatter', 'templates'))
    template = env.get_template('index.jinja2')

    with open(OUTPUT_DIR + 'index.html', 'w') as fh:
        fh.write(template.render(
            plants=photos.plant_records,
            unidentified_photos=photos.unidentified_photos,
            plant_types=PLANT_TYPES,
            locations=LOCATIONS,
        ))

    cssfile = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'plantbook.css')
    shutil.copyfile(cssfile, OUTPUT_DIR + 'plantbook.css')


if __name__ == "__main__":
    main()
