"""
EatMe
-------------

EatMe is an Alexa food skill helping you to find a good random place to eat
"""
from setuptools import setup, find_packages
from eatme import __version__
from pip.req import parse_requirements

# install_reqs = parse_requirements('requirements.txt', session=False)
# prod_requires = [str(ir.req) for ir in install_reqs]

setup(
    name='eatme',
    version=__version__,
    url='https://github.com/KNNCreative/EatMe-Alexa-Food-Skill',
    license='MIT',
    author='Kien Pham',
    author_email='info@knncreative.com',
    description='EatMe - Alexa Food Skill',
    long_description=__doc__,
    packages=['eatme'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'requests',
        'boto3'
    ],
    entry_points={
        "console_scripts": [
            "eatme = eatme.eatme:cli"
      ]
    },
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
