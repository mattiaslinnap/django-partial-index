## Making a new release for PyPI

1. Update version number in `partial_index/__init__.py`
1. Update version number in `setup.py`
1. Update download link version number in `setup.py`
1. If added or removed support for some Python/Django versions, update classifiers in `setup.py`
1. Update PyPI version badge number in `README.md`
1. Update version history at the end of `README.md`
1. Push to release branch on github, review that tests pass on Travis.
1. `python3 setup.py sdist bdist_wheel upload`
1. Go to https://github.com/mattiaslinnap/django-partial-index/releases and click New Release, fill details:
  1. New tag name should be just the numeric version ("1.2.3" not "v1.2.3")
  1. From branch "release"
  1. Release title should be "v1.2.3"
  1.
