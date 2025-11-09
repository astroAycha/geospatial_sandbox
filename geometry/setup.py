from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(name = 'minimal_geometry',
      version='0.0.1',
      description='Minimal Geometry package for practice purposes',
      author='AT',
      author_email='',
      packages=find_packages(),
      install_requires=[],
      long_description=long_description)