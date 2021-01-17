import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

PACKAGES = setuptools.find_packages("src")

setuptools.setup(
    name="timeframe",
    version="0.1.0",
    author="Meysam Azad",
    author_email="MeysamAzad81@gmail.com",
    description="Time Frame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/meysam81/timeframe",
    packages=PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
