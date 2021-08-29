# rgbmaker  [![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)  [![PyPI version](https://badge.fury.io/py/rgbmaker.svg)](https://badge.fury.io/py/rgbmaker)
A python package which communicates to different astronomical services and fetches fits and numerical data.

# Developement
```bash
$ pip install -e .[dev]
```

# Installation:
```bash
$ pip install rgbmaker
```

# Usage
```bash
$ from rgbmaker.fetch import query
$ result = query(name='Avi', position='3C 33.1', radius=0.12, kind='jpg')
$ print(result)
```
# Demo


https://user-images.githubusercontent.com/36457781/128387219-07490fdd-c417-452b-8c68-20cfa499b1b6.mp4

