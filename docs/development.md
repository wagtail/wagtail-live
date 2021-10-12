# Development

Install this package in development mode:

```shell
git clone git@github.com:wagtail/wagtail-live.git
cd wagtail-live
```

With your preferred virtualenv activated, install the package in development mode with the included testing and documentation dependencies:

```shell
python -m pip install -e '.[test,docs]' -U
```

## Testing

Run the test suite locally:

```shell
pytest
```

Or test all supported configurations using tox:

```shell
python -m pip install tox
tox
```

## Code style linting

Check the code style of all files (requires GNU Make to be installed):

```shell
make lint
```

Fix any errors that can be automatically fixed:

```shell
make format
```



## Documentation

Run documentation locally:

```shell
mkdocs serve
```


Deploy documentation to Github pages:

```shell
mkdocs gh-deploy
```


## Releasing new versions

This package follows [SemVer](https://semver.org/).

Please keep SemVer in mind when updating the version number in `src/wagtail_live/__init__.py`. 

### Building the package & publishing to PyPI

Make sure you install the `build` extra before attempting to make a release:

```sh
pip install -e '.[build]'
```

This project comes with a helper script that assists in making a release.

```sh
./make_release.sh
```

This script will:

1. Verify that no git tag exists for the current version number.
2. Builds wheels and source distributions.
3. Show instructions on how to create a git tag.
4. Show instructions on how to upload to PyPI.