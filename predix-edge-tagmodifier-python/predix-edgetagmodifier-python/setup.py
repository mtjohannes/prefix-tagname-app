
from setuptools import setup, find_packages

install_requires = [
        'paho-mqtt'
        ]

long_description = 'See GitHub README.rst for more details.'
with open('README.md') as file:
    long_description = file.read()

setup(
        name='predix-edge-sample-scaler-python',
        version='1.0.0',
        description='Predix Edge Sample Python App',
        long_description=long_description,
        install_requires=install_requires,
        package_data={
            '': ['*.md', '*.rst'],
            },
        packages=find_packages(exclude=['test', 'test.*']),
        test_suite='test'
        )
