import argparse
import json
import logging
import shutil
import subprocess

from book_formatter.book_formatter import PhotoCollection
from book_formatter.values import (
    LOCATIONS, PLANT_TYPES, NATIVITY_VALUES, NATIVITY_LABELS
)
from jinja2 import Environment, PackageLoader
from os.path import dirname, join as joinpath

logging.basicConfig(
    filename='log/o.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s - %(message)s',
)

OUTPUT_DIR = '/Users/gkreftin/temp/'


def main():
    logging.info('Starting main')
    parser = argparse.ArgumentParser()
    parser.add_argument('local_path')
    parser.add_argument('remote_host')
    parser.add_argument('remote_path')
    args = parser.parse_args()
    logging.info('args.local_path: %s', args.local_path)

    local_path = args.local_path
    json_path = joinpath(local_path, 'json', 'PhotoBook.json')
    web_root = joinpath(local_path, 'public_html')

    f = open(json_path, 'r')
    raw_records = json.load(f)
    f.close()

    photos = PhotoCollection(raw_records)
    logging.info('Reading image sizes')
    photos.init_image_sizes(web_root)
    logging.info('Reading snippets')
    photos.init_snippets(local_path)

    logging.info('Writing index.html')
    env = Environment(loader=PackageLoader('book_formatter', 'templates'))
    template = env.get_template('index.jinja2')

    with open(joinpath(web_root, 'index.html'), 'w') as fh:
        fh.write(template.render(
            plants=photos.plant_records,
            unidentified_photos=photos.unidentified_photos,
            plant_types=PLANT_TYPES,
            locations=LOCATIONS,
            nativity_values=NATIVITY_VALUES,
            nativity_labels=NATIVITY_LABELS,
            plant_collection=photos,
        ))

    logging.info('Copying css and js files')
    cssfile = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'plantbook.css')
    shutil.copyfile(cssfile, joinpath(web_root, 'plantbook.css'))

    photoswipedir = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'photoswipe')
    shutil.copytree(
        photoswipedir,
        joinpath(web_root, 'photoswipe'),
        dirs_exist_ok=True)

    tabsdir = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'tabs')
    shutil.copytree(
        tabsdir,
        joinpath(web_root, 'tabs'),
        dirs_exist_ok=True)

    tabsdir = joinpath(
        dirname(__file__),
        'book_formatter/templates',
        'img')
    shutil.copytree(
        tabsdir,
        joinpath(web_root, 'img'),
        dirs_exist_ok=True)

    # Do the rsync
    cmd = ['rsync',
           '-az',
           # '-vv',
           # '--stats',
           '--delete',
           '--log-file=log/rsync.log',
           web_root + "/",  # trailing slash is important
           args.remote_host + ":" + args.remote_path
           ]
    logging.info('syncing to remote')
    logging.info('cmd: %s', cmd)
    retval = subprocess.run(cmd)
    logging.info('retval: %s', retval)
    logging.info('Done')


if __name__ == "__main__":
    main()
