from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "wagtail>=2.12",
]

docs_requires = [
    "mkdocs>=1.1,<1.2",
    "mkdocs-material>=7.1,<7.2",
]

test_requires = [
    "black==21.5b2",
    "isort==5.8.0",
    "flake8==3.9.2",
    "pytest>=6.2,<6.3",
    "pytest-cov>=2.12,<3",
    "pytest-django>=4.3.0,<5",
]

setup(
    name="wagtail-live",
    version="0.1",
    description="An app for high speed content publishing from a messaging app to a Wagtail site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tidiane Dia and Wagtail Core Team",
    author_email="hello@wagtail.io",
    install_requires=install_requires,
    tests_require=test_requires,
    extras_require={
        "test": test_requires,
        "docs": docs_requires,
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
