"""
EatMe
-------------

EatMe is an Alexa food skill helping you to find a good random place to eat
"""
from setuptools import setup

setup(
    name='EatMe',
    version='0.0.1',
    url='https://github.com/KNNCreative/EatMe-Alexa-Food-Skill',
    license='MIT',
    author='Kien Pham',
    author_email='shop@kienpham.com',
    description='EatMe - Alexa Food Skill',
    long_description=__doc__,
    packages=['eatme'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Framework :: Flask',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
