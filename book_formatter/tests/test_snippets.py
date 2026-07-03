import json
import pytest
import tempfile
from snippets.snippets import SnippetGrabber, _safename, _get_remote_snippet

GARLIC_MUSTARD_HTML = (
    '<p><i><b>Alliaria petiolata</b></i>, or <b>garlic mustard</b>, '
    'is a biennial flowering plant.</p>')


class _FakeResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def _mock_wikipedia(monkeypatch, status_code, extract_html=None):
    body = json.dumps({'extract_html': extract_html} if extract_html else {})
    monkeypatch.setattr(
        'snippets.snippets.requests.get',
        lambda url: _FakeResponse(status_code, body))


@pytest.fixture
def sg():
    return SnippetGrabber(tempfile.mkdtemp())


def test_safename_spaces():
    assert _safename('Alliaria petiolata') == 'Alliaria_petiolata'


def test_safename_cultivar():
    assert _safename("Chelone lyonii 'Hot Lips'") == 'Chelone_lyonii'


def test_safename_cultivar_2():
    assert _safename(
        "Narcissus poeticus var. recurvus"
    ) == 'Narcissus_poeticus'


def test_safename_cultivar_more_quotes():
    assert _safename(
        "Chelone 'banana' lyonii 'Hot Lips'"
    ) == "Chelone_'banana'_lyonii"


def test_safename_species():
    assert _safename("Spirogyra sp.") == 'Spirogyra'


def test_safename_species_2():
    assert _safename("Narcissus sp.") == 'Narcissus_(plant)'


def test_safename_colon():
    with pytest.raises(ValueError):
        _safename("Foo : bar ")


def test_safename_slash():
    with pytest.raises(ValueError):
        _safename("Foo / bar ")


def test_safename_backslash():
    with pytest.raises(ValueError):
        _safename("Foo \\ bar ")


def test_get_remote_snippet(monkeypatch):
    _mock_wikipedia(monkeypatch, 200, extract_html=GARLIC_MUSTARD_HTML)
    assert _get_remote_snippet('Alliaria petiolata').startswith(
        '<p><i><b>Alliaria petiolata</b></i>, or <b>garlic mustard')


def test_get_bad_snippet(monkeypatch):
    _mock_wikipedia(monkeypatch, 404)
    with pytest.raises(ValueError):
        _get_remote_snippet('Alliaria petiolataX')


@pytest.mark.network
def test_get_remote_snippet_live():
    """Sanity check against the real Wikipedia API. Excluded from the
    default run (see pyproject.toml `-m "not network"`); run explicitly
    with `poetry run pytest tests/ -m network` to catch API/format drift."""
    assert _get_remote_snippet('Alliaria petiolata').startswith(
        '<p><i><b>Alliaria petiolata</b></i>, or <b>garlic mustard')


def test_get_empty_local_snippet(sg):
    assert not sg._get_local_snippet('Alliaria petiolata')


def test_get_local_snippet(sg):
    sg._store_local_snippet('Alliaria petiolata', 'foo')
    assert sg._get_local_snippet('Alliaria petiolata') == 'foo'


def test_get_snippet(sg, monkeypatch):
    """ first time, grabs from the web, second time, from local """
    _mock_wikipedia(monkeypatch, 200, extract_html=GARLIC_MUSTARD_HTML)
    assert sg.get_snippet('Alliaria petiolata').startswith(
        '<p><i><b>Alliaria petiolata</b></i>, or <b>garlic mustard')
    assert sg.get_snippet('Alliaria petiolata').startswith(
        '<p><i><b>Alliaria petiolata</b></i>, or <b>garlic mustard')
