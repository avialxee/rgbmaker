from setuptools import setup

with open("README.md", "r") as rdme:
    desc = rdme.read()

setup(
    name = 'rgbmaker',
    version = '0.0.4.7.8',
    url='https://github.com/avialxee/rgbmaker',
    author='Avinash Kumar',
    author_email='avialxee@gmail.com',
    description='A python package which communicates to different astronomical services and fetches fits and numerical data.',
    py_modules = ["rgbmaker"],
    package_dir={'':'src'},
    classifiers=["Programming Language :: Python :: 3",
                 "Programming Language :: Python :: 3.7",
                 "Programming Language :: Python :: 3.8",
                 "License :: OSI Approved :: BSD License",
                 "Intended Audience :: Science/Research",
                 ],
    long_description=desc,
    long_description_content_type = "text/markdown",
    install_requires=["astropy>=4.2.1", "matplotlib>= 3.4.2",
                      "regions", "numpy>= 1.20.3", "astroquery","requests"
                      ],
    extras_require = {
        "dev" : ["pytest>=3.7",
        ]
    }

)
