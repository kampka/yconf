
from setuptools import setup, find_packages

setup(
    name='yconf',
    version="0.1",
    license='GPL-3',
    author='Christian Kampka',
    author_email='chris@emerge-life.de',
    description='Wrapper that combines argparse with yaml config files.',
    #long_description='Here a longer description',
    install_requires=[
        "PyYAML >= 3.1",
    ],
    tests_require=[
        "fixtures",
        "testtools"
    ],
    test_suite="yconf.tests",
    packages=find_packages(),
    )
