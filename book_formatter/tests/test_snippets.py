import pytest
from snippets.snippets import SnippetGrabber, _safename


@pytest.fixture
def sg():
    return SnippetGrabber('/Users/gkreftin/temp/snippets')


def test_get_snippet(sg):
    assert sg.get_snippet('Alliaria petiolata').startswith(
        'Alliaria petiolata, or garlic mustard')


def test_safename_spaces():
    assert _safename('Alliaria petiolata') == 'Alliaria_petiolata'


def test_safename_culivar():
    assert _safename("Chelone lyonii 'Hot Lips'") == 'Chelone_lyonii'


def test_safename_culivar_more_quotes():
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
