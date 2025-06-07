from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in esignature/__init__.py
from esignature import __version__ as version

setup(
    name="esignature",
    version=version,
    description="Digital signature solution for ERPNext with pyHanko integration",
    author="Your Company",
    author_email="admin@yourcompany.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
