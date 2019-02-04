from setuptools import setup, find_namespace_packages

setup(
    name="weatherapp.core",
    version="0.1.0",
    author="Roman Kovtunets",
    description="CLI weather aggregator",
    long_description="""Simple CLI weather aggregator. Educational project: web parsing (BS),
                        configuring with configparser and JSON,
                        classes and objects(abstract objects, inheritance, polymorphism,
                        iterators/generators etc), CLI, files management, caching,
                        RegEx, error handling, logging, packaging, stdin/out, and testing""",
    packages=find_packages(),
    entry_points={
        'console_scripts': 'wfapp=weatherapp.core.app:main'
    },
    install_requires=[
        'requests',
        'bs4'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
