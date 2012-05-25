import os
from setuptools import setup, find_packages

from django_lithium_api import __version__ as version

install_requires = [
    'setuptools',
]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = 'django-lithium-api',
    version = version,
    description = "A (very) limited implementation of the Lithium REST API for Django",
    long_description = read('README.rst'),
    author = 'Benjamin Wohlwend',
    author_email = 'piquadrat@gmail.com',
    url = 'https://github.com/piquadrat/django-lithium-api',
    packages = find_packages(),
    zip_safe=False,
    include_package_data = True,
    install_requires=[
        'Django>=1.3',
        'requests',
        'python-dateutil==1.5',
        'lxml',
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)
