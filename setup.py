#!/usr/bin/env python
#encoding: utf-8

from setuptools import setup

setup(name="snip_sort",
        version='0.1.0',
        description="A utility to sort snips based on hits against different species. Sort based on chrom & pos",
        author='James Rivett-Carnac',
        author_email='james.rivettcarnac@gmail.com',
        packages=['snip_sort',],
        install_requires=['path.py',],
        scripts=['scripts/snip_sort',],
        classifiers=[
            'License :: OSI Approved :: MIT License',
        ]
        )

