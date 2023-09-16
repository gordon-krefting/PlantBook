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
    photos.init_image_sizes()

    print(json.dumps(photos.scientific_names, indent=1))

    env = Environment(loader=PackageLoader('book_formatter', 'templates'))
    template = env.get_template('index.jinja2')

    with open(OUTPUT_DIR + 'index.html', 'w') as fh:
        fh.write(template.render(
            plants=photos.plant_records,
            unidentified_photos=photos.unidentified_photos,
            plant_types=PLANT_TYPES,
            locations=LOCATIONS,
            plant_collection=photos,
        ))

    cssfile = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'plantbook.css')
    shutil.copyfile(cssfile, OUTPUT_DIR + 'plantbook.css')

    photoswipedir = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'photoswipe')
    shutil.copytree(
        photoswipedir,
        OUTPUT_DIR + 'photoswipe',
        dirs_exist_ok=True)

    tabsdir = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'tabs')
    shutil.copytree(
        tabsdir,
        OUTPUT_DIR + 'tabs',
        dirs_exist_ok=True)


if __name__ == "__main__":
    main()
