import pytest
import tempfile
from snippets.snippets import SnippetGrabber, _safename, _get_remote_snippet


@pytest.fixture
def sg():
    return SnippetGrabber(tempfile.mkdtemp())


def test_safename_spaces():
    assert _safename('Alliaria petiolata') == 'Alliaria_petiolata'


def test_safename_cultivar():
    assert _safename("Chelone lyonii 'Hot Lips'") == 'Chelone_lyonii'


def test_safename_cultivar_more_quotes():
    assert _safename(
        "Chelone 'banana' lyonii 'Hot Lips'"
    ) == "Chelone_'banana'_lyonii"


def test_safename_colon():
    with pytest.raises(ValueError):
        _safename("Foo : bar ")


def test_safename_slash():
    with pytest.raises(ValueError):
        _safename("Foo / bar ")


def test_safename_backslash():
    with pytest.raises(ValueError):
        _safename("Foo \\ bar ")


def test_get_remote_snippet():
    assert _get_remote_snippet('Alliaria petiolata').startswith(
        'Alliaria petiolata, or garlic mustard')


def test_get_bad_snippet():
    with pytest.raises(ValueError):
        _get_remote_snippet('Alliaria petiolataX')


def test_get_empty_local_snippet(sg):
    assert not sg._get_local_snippet('Alliaria petiolata')


def test_get_local_snippet(sg):
    sg._store_local_snippet('Alliaria petiolata', 'foo')
    assert sg._get_local_snippet('Alliaria petiolata') == 'foo'


def test_get_snippet(sg):
    """ first time, grabs from the web, second time, from local """
    assert sg.get_snippet('Alliaria petiolata').startswith(
        'Alliaria petiolata, or garlic mustard')
    assert sg.get_snippet('Alliaria petiolata').startswith(
        'Alliaria petiolata, or garlic mustard')
