import re


def _safename(name):
    """Convert a name to a safe filename.

    Works for OSX, maybe UNIXes, but probably not Windows."""
    # a special case for cultivars (we don't want to use the cultivar name)
    name = re.sub(" '[^']*'$", '', name)

    if len(name) < 5:
        raise ValueError('Name too short: %s' % name)

    if re.search("[:|/|\\\\]", name):
        raise ValueError('Name contains illegal character: %s' % name)

    return name.replace(' ', '_')


class SnippetGrabber(object):
    def __init__(self, path):
        self.path = path

    def get_snippet(self, name):
        return 'Alliaria petiolata, or garlic mustard'
