# rgbmaker
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
