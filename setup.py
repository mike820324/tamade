from setuptools import setup, find_packages

setup(
    name="tamade",
    version="0.1.0",
    description="Get PHP settings from c source code.",
    long_description="""
tamade is a simple tool that will grab all the php ini settings from source code.

Source code: https://github.com/mike820324/tamade

Documentation: https://github.com/mike820324/tamade/blob/master/README.md
    """,
    url="https://github.com/mike820324/tamade",
    author="MicroMike",
    author_email="mike820324@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: PHP",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities"
    ],
    keywords=["php", "parsing", "ini"],
    packages=find_packages(include=["tamade"]),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "tamade=tamade.command_line:main"
        ]
    }
)
