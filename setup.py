import re

from setuptools import setup, find_packages

with open('isimip_publisher/__init__.py') as f:
    metadata = dict(re.findall(r'__(.*)__ = [\']([^\']*)[\']', f.read()))

setup(
    name=metadata['title'],
    version=metadata['version'],
    author=metadata['author'],
    author_email=metadata['email'],
    maintainer=metadata['author'],
    maintainer_email=metadata['email'],
    license=metadata['license'],
    url='https://github.com/ISI-MIP/isimip-publisher',
    description=u'',
    long_description=open('README.md').read(),
    install_requires=[
        'PyYAML',
        'netCDF4',
        'python-dotenv'
    ],
    classifiers=[
        # https://pypi.org/classifiers/
        'Development Status :: 1 - Planning',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'isimip-publisher=isimip_publisher.main:main',
        ]
    }
)
