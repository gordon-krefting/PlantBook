import pytest
from snippets.snippets import SnippetGrabber


@pytest.fixture
def sg():
    return SnippetGrabber('/Users/gkreftin/temp/snippets')


def test_get_snippet(sg):
    assert sg.get_snippet('Alliaria petiolata').startswith(
        'Alliaria petiolata, or garlic mustard')


def test_safename_spaces(sg):
    assert sg._safename('Alliaria petiolata') == 'Alliaria_petiolata'


def test_safename_variety(sg):
    assert sg._safename("Chelone lyonii 'Hot Lips'") == 'Chelone_lyonii'
    assert sg._safename(
        "Chelone 'banana' lyonii 'Hot Lips'"
    ) == "Chelone_'banana'_lyonii"


def test_safename_colon(sg):
    with pytest.raises(ValueError):
        sg._safename("Foo : bar ")


def test_safename_slash(sg):
    with pytest.raises(ValueError):
        sg._safename("Foo / bar ")


def test_safename_backslash(sg):
    with pytest.raises(ValueError):
        sg._safename("Foo \\ bar ")
