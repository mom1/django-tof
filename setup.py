# -*- coding: utf-8 -*-
# @Author: MaxST
# @Date:   2019-10-28 20:17:20
# @Last Modified by:   MaxST
# @Last Modified time: 2019-11-07 14:28:57
from setuptools import find_packages, setup

import tof

with open('README.md', 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name='django-tof',
    version=tof.__version__,
    description='Freely distributed library that allows you to translate fields of django models without having to restart the server, without changing the model code, with the storage of translations in the database.',
    long_description=long_description,
    author='Maksim Stolpasov',
    author_email='mstolpasov@gmail.com',
    url='https://github.com/mom1/django-tof',
    packages=find_packages(exclude=[
        'django_tof.egg-info',
    ]),
    zip_safe=False,
    include_package_data=True,
    # install_requires=[
    #     'Django==3.0b1',
    # ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Linguistic',
    ])
