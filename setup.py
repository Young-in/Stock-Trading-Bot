import setuptools

"""
My package path is not included in sys.path becuase I'm working in virtual environment.
'setup.py' inserts working directory to sys.path.

Put command like below

python3 setup.py develop

"""

setuptools.setup(
    name="test",
    package_dir={"":"."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)