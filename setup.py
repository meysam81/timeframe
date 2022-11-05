import os

import setuptools

import timeframe

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

PACKAGES = setuptools.find_packages(include=("timeframe",))
PACKAGE_VERSION = os.getenv(
    "PACKAGE_VERSION", getattr(timeframe, "__version__", "0.0.0")
)

setuptools.setup(
    name=timeframe.__name__,
    version=PACKAGE_VERSION,
    author=timeframe.__author__,
    author_email=timeframe.__author_email__,
    description="Calculation of time frames using the built-in datetime module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meysam81/timeframe",
    packages=PACKAGES,
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.6",
)
