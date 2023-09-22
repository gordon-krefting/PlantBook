import re


class SnippetGrabber(object):
    def __init__(self, path):
        self.path = path

    def _safename(self, name):
        # a special case for cultivars (we don't want to use the cultivar name)
        name = re.sub(" '[^']*'$", '', name)

        if len(name) < 5:
            raise ValueError('Name too short: %s' % name)

        if re.search("[:|/|\\\\]", name):
            raise ValueError('Name contains illegal character: %s' % name)

        return name.replace(' ', '_')

    def get_snippet(self, name):
        return 'Alliaria petiolata, or garlic mustard'
