import os
import versioneer
from distutils.core import setup
from setuptools import setup


with open("requirements.txt") as f:
    tests_require = f.readlines()
install_requires = [t.strip() for t in tests_require]

with open("README.md") as f:
    long_description = f.read()


setup(name='geoplanar',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass({"build_py": build_py}),  
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
