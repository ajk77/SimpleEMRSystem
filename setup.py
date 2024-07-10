from setuptools import setup
import os

from SEMRproject import __VERSION__

NAME = 'SimpleEMRSystem'
VERSION = __VERSION__


def read(fn):
        return open(os.path.join(os.path.dirname(__file__), fn)).read()


setup(
    name=NAME,
    version=VERSION,
    description='The Simple EMR System is a rapidly deployable and readily customizable electronic medical record (EMR) user interface for supporting laboratory-based research studies of EMR design and usability.',
    long_description=read('README.md'),
    author='Andrew J King',
    author_email='andrew.king@pitt.edu',
    url='https://github.com/ajk77/SimpleEMRSystem',
    license='GPL-3.0 license',
    packages=['SEMRinterface','SEMRproject']
)
