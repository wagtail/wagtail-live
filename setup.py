from setuptools import find_packages, setup

from src.wagtail_live import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "wagtail>=2.12",
]

docs_requires = [
    "mkdocs>=1.1,<1.2",
    "mkdocs-material>=7.1,<7.2",
    "mkdocstrings>=0.15.2,<0.16",
]

test_requires = [
    "black==21.5b2",
    "isort==5.8.0",
    "flake8==3.9.2",
    "pytest>=6.2,<6.3",
    "pytest-cov>=2.12,<3",
    "pytest-django>=4.3.0,<5",
    "pytest-factoryboy>=2.1.0,<3",
    "pytest-mock>=3.6.1,<3.7.0",
    "pytest-asyncio",
    "channels",
    "mock>=4.0.3,<5.0.0",
    "wagtail-factories>=2.0.1,<3",
]

build_requires = [
    "twine",
    "check-wheel-contents",
]

setup(
    name="wagtail-live",
    version=__version__,
    description="An app for high speed content publishing from a messaging app to a Wagtail site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tidiane Dia and Wagtail Core Team",
    author_email="hello@wagtail.io",
    url="https://github.com/wagtail/wagtail-live/",
    project_urls={
        "Documentation": "https://wagtail.github.io/wagtail-live/",
        "Source": "https://github.com/wagtail/wagtail-live/",
        "Issue tracker": "https://github.com/wagtail/wagtail-live/issues/",
    },
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
        "docs": docs_requires,
        "build": build_requires,
    },
    package_dir={"": "src"},
    packages=find_packages("src"),
    include_package_data=True,
    zip_safe=False,
    license="BSD-3-Clause",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
