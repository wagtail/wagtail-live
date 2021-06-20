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

Run the test suite locally

```shell
pytest
```

Or test all supported configurations using tox:

```shell
python -m pip install tox
tox
```

Show test coverage:

```shell
make showcov
```

## Code style linting

Check code style of all files (requires GNU Make to be installed)

```shell
make lint
```

Fix any errors that can be automatically fixed

```shell
make format
```



## Documentation

Run documentation locally

```shell
mkdocs serve
```


Deploy documentation to Github pages:

```shell
mkdocs gh-deploy
```

See [https://wagtail.github.io/wagtail-live/](https://wagtail.github.io/wagtail-live/)
