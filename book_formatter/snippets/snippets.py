import json
import re
import requests


def _safename(name):
    """Convert a name to a safe filename.

    Works for OSX, maybe UNIXes, but probably not Windows."""
    # A very special case for Narcissus
    name = re.sub('Narcissus sp.', 'Narcissus_(plant)', name)

    # a special case for cultivars (we don't want to use the cultivar name)
    name = re.sub(" '[^']*'$", '', name)

    # another special case for cultivars
    name = re.sub(" var\\..*", '', name)

    # special case for species
    name = re.sub(" sp\\..*", '', name)

    if len(name) < 5:
        raise ValueError('Name too short: %s' % name)

    if re.search("[:|/|\\\\]", name):
        raise ValueError('Name contains illegal character: %s' % name)

    return name.replace(' ', '_')


def _get_remote_snippet(name):
    url = 'https://en.wikipedia.org/api/rest_v1/page/summary/' + name
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError('Could not get snippet for %s' % url
                         + ' (status code %s)' % r.status_code)
    j = json.loads(r.text)
    snippet = j['extract_html']
    link = (' <a '
            'href="https://en.wikipedia.org/wiki/%s" '
            'class="snippet-link" '
            'target="_blank"'
            '>Wikipedia</a>' % (name))
    snippet = re.sub("</p>$", link, snippet)
    return snippet


class SnippetGrabber(object):
    def __init__(self, path):
        self.path = path

    def _get_local_snippet(self, name):
        try:
            with open(self.path + '/' + _safename(name) + '.txt') as f:
                return f.read()
        except IOError:
            return None

    def _store_local_snippet(self, name, snippet):
        with open(self.path + '/' + _safename(name) + '.txt', 'w') as f:
            f.write(snippet)

    def get_snippet(self, name):
        snippet = self._get_local_snippet(_safename(name))
        if not snippet:
            try:
                snippet = _get_remote_snippet(_safename(name))
            except ValueError:
                snippet = " "
            self._store_local_snippet(_safename(name), snippet)
        if len(snippet) > 1:
            return snippet
        else:
            return None
