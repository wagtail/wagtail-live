# Development

Install this package in development mode:

```shell
git clone git@github.com:wagtail/wagtail-live.git
cd wagtail-live
```

With your preferred virtualenv activated, install the package in development mode with the included testing and documentation dependencies:

```shell
[TODO: needs setup.cfg and setup.py] python -m pip install -e '.[test,docs]' -U

[TODO: temp remove]  python -m pip install -r development_requirements.txt
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
