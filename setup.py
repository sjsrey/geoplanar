from distutils.core import setup

import os

# Get __version__ from libpysal/__init__.py without importing the package
# __version__ has to be defined in the first line
with open("geoplanar/__init__.py", "r") as f:
    exec(f.readline())


from setuptools import setup

with open("requirements.txt") as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]

with open("README.md") as f:
    long_description = f.read()



setup(name='geoplanar',
    version=__version__,
    description='Geographic planar enforcement of polygon geoseries',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sjsrey/geoplanar",
    author='Serge Rey',
    author_email='sjsrey@gmail.com',
    license="3-Clause BSD",
    packages=['geoplanar'],
    package_data={"": ["requirements.txt"]},
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    zip_safe=False,
)
