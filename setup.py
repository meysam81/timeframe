import setuptools
import timeframe

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

PACKAGES = setuptools.find_packages(include=("timeframe",))

setuptools.setup(
    name=timeframe.__name__,
    version=timeframe.__version__,
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
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    package_data={
        "README": ["README.md"],
    },
    keywords="datetime timeframe time-frame",
    python_requires=">=3.6, <4",
)
