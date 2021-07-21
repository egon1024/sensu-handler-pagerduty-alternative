#!/usr/bin/env python

import setuptools
from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

with open('requirements.txt') as f:
    requirements = [_.strip() for _ in f.readlines()]

setup(
    name='sensu-handler-pagerduty-alternative',
    version='0.1.0',
    author='Cole Tuininga',
    author_email='cole.tuininga+sensu-handler@gmail.com',
    description='A Sensu Go handler to communicate with PagerDuty',
    long_description=readme,
    scripts=['sensu-handler-pagerduty-alternative.py'],
    install_requires=requirements,
)
