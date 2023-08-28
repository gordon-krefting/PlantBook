from jinja2 import Environment, PackageLoader

import json

f = open('/Users/gkreftin/temp/PhotoBook.json')
photo_records = json.load(f)
f.close()

env = Environment(loader=PackageLoader('book_formatter'))
template = env.get_template('index.jinja2')

with open('/Users/gkreftin/temp/index.html', 'w') as fh:
    fh.write(template.render(
        photo_records=photo_records
    ))
