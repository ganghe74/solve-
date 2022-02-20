from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="solve",
    version="0.0.0",
    description="a small cli tool for ps",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
        'Beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'solve = src.main:cli'
        ],
    },
)
