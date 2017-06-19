# coding: utf-8
from setuptools import setup, find_packages
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


__version__ = "2016.12.4"

setup(
    name='cfmmc',
    version=__version__,
    keywords='cfmmc',
    description=u'中国期货监控中心模拟浏览器操作',
    long_description=read("README.md"),

    url='https://github.com/lamter/cfmmcspider',
    author='lamter',
    author_email='lamter.fu@gmail.com',

    packages=find_packages(),
    package_data={
        "tradingtime": ["*.json"],
    },
    install_requires=read("requirements.txt").splitlines(),
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'License :: OSI Approved :: MIT License'],
)
