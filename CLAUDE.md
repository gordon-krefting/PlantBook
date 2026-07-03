# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

PlantBook generates a plant-guide website (krefting.org/plantguide) from photos tagged in an Adobe
Lightroom Classic catalog. It only really works for the author's own single-user setup (macOS,
one Lightroom catalog, one remote host) — it is not meant to be generalized.

There are two independent halves that communicate only through a JSON file and a shell call:

1. **`plant-book.lrdevplugin/`** — a Lightroom Classic plugin (Lua) that adds custom metadata
   fields to photos, exports tagged/rated photos + thumbnails on publish, writes a
   `json/PhotoBook.json` control file describing every photo, and then shells out to
   `book_formatter/main.sh`.
2. **`book_formatter/`** — a Python (Poetry) app that reads `PhotoBook.json`, groups photos into
   plant records, renders a static HTML site via Jinja2, and rsyncs it to the remote host.

## Commands (book_formatter/)

Run from `book_formatter/`:

```sh
poetry install                 # set up the venv (first time / after dependency changes)
poetry run pytest tests/       # run the test suite (must pass explicit `tests/` path — bare
                                # `poetry run pytest` from this dir finds nothing)
poetry run pytest tests/test_loading.py::test_plant_count   # run a single test
poetry run python main.py <local_path> <remote_host> <remote_path>   # run the site generator directly
```

Note: `tests/test_snippets.py::test_get_remote_snippet` and `::test_get_snippet` hit the live
Wikipedia API and can fail on network/rate-limit issues (e.g. 403) unrelated to code changes.

There is no lint config in this repo — don't assume flake8/black/ruff are wired up.

`main.sh` is not checked in; it's generated locally by the user from `template.main.sh` (it just
`cd`s into `book_formatter` and runs `poetry run python main.py "$@"`, needed because Lightroom's
plugin sandbox doesn't have Poetry on its PATH).

## Architecture: book_formatter

Entry point `main.py` takes `(local_path, remote_host, remote_path)`:
1. Reads `<local_path>/json/PhotoBook.json` (written by the Lightroom plugin).
2. Builds a `PhotoCollection` from the raw records (`book_formatter/book_formatter.py`).
3. Fills in image dimensions from `<local_path>/public_html/{images,thumbs}/`.
4. Fetches/caches a Wikipedia summary blurb per species via `snippets/snippets.py`.
5. Renders `book_formatter/templates/index.jinja2` to `public_html/index.html`.
6. Copies static assets (css/photoswipe/tabs/img) into `public_html/`.
7. `rsync --delete`s `public_html/` to `remote_host:remote_path`.

Data model (`book_formatter/book_formatter.py`):
- `PhotoRecord` — one photo, built straight from one JSON record (filename, rating, date, location,
  nativity, "introduced" info, etc).
- `PlantRecord` — one species, built by merging all `PhotoRecord`s that share a `scientificName`.
  The merge logic (`_update_*` methods) is where cross-photo consistency is enforced: conflicting
  common names, plant types, nativity, or ID confidence across photos of the same species are
  collected into `self.errors` (rendered in the site) rather than raised — bad tagging data
  degrades gracefully instead of crashing the build. Only photos with `rating > 3` are eligible as
  a plant's "best" display photos; if none qualify, the single highest-rated photo is used.
- `PhotoCollection` — top-level container; groups `PhotoRecord`s by scientific name into
  `PlantRecord`s, tracks unidentified photos (no scientific name) separately, and exposes filter
  helpers (`get_plants_by_type`, `get_plants_by_location`, `get_latest_plants`, etc) used by the
  template.

Controlled vocabularies (plant type, location, nativity, "introduced" method) live in
`book_formatter/values.py` and must stay in sync with the enum values defined in the Lightroom
plugin's `MetadataDefinition.lua` — a value added on one side without the other will silently show
up as an untranslated key or missing option.

`snippets/snippets.py` is a *top-level* package (not nested under `book_formatter/book_formatter/`),
imported as `from snippets.snippets import SnippetGrabber` — this only resolves because `main.py`
and `pytest` are both run with `book_formatter/` (not the inner package dir) as the working
directory/rootdir.

## Architecture: plant-book.lrdevplugin

- `Info.lua` — plugin manifest; registers the metadata provider, tagset, and export/publish
  service provider under toolkit ID `org.krefting.plant-book`.
- `MetadataDefinition.lua` — declares the custom photo metadata fields (scientificName,
  commonName, location, plantType, nativity, idConfidence, introduced, introductionYear, etc) and
  their enum options. This is the source of truth for allowed values.
- `Tagset.lua` — arranges those fields into the metadata panel shown in Lightroom's UI.
- `PublishServiceProvider.lua` — the core publish logic, in
  `exportServiceProvider.processRenderedPhotos`:
  1. Validates the configured `local_path`/`remote_host`/`remote_path` publish settings.
  2. Exports full-size renditions of changed photos into `public_html/images/`.
  3. Exports 150x150 thumbnails into `public_html/thumbs/`.
  4. Finds the child collection literally named `"Plant Photos"`, calls `ExportBookData` to dump
     every photo's metadata (via `getPropertyForPlugin("org.krefting.plant-book", ...)`) into
     `json/PhotoBook.json`.
  5. Shells out to `book_formatter/main.sh <local_path> <remote_host> <remote_path>` — this is the
     bridge into the Python half.
  - Only incremental publish is supported (`supportsIncrementalPublish = 'only'`); export settings
    (format/size/quality) are fixed in code and not user-editable.
- `JSON.lua` — vendored third-party JSON library (not project code).

Logs: the plugin logs to `~/Documents/LrClassicLogs/PlantBookPlugin.log`; `main.py` logs to
`book_formatter/log/o.log` and `book_formatter/log/rsync.log`. `template.logtail.sh` (copy to
`logtail.sh` locally, per the same untracked-template pattern as `main.sh`) tails all three at once.

## Making changes across the boundary

Any change to the JSON schema (`ExportBookData` in `PublishServiceProvider.lua`) must be mirrored
in `PhotoRecord.__init__` (`book_formatter/book_formatter.py`), since the Python side reads fields
by key with no schema validation — a typo'd or renamed key fails silently (field just reads as
`None`) rather than erroring.
