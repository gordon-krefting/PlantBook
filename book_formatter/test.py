from jinja2 import Environment, PackageLoader
import os

env = Environment(loader=PackageLoader('book_formatter'))
template = env.get_template('index.html')

root = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(root, '/Users/gkreftin/temp', 'index.html')

with open(filename, 'w') as fh:
    fh.write(template.render(
        h1="Hello Jinja2",
        show_one=True,
        show_two=False,
        names=["Foo", "Bar", "Qux"],
    ))
