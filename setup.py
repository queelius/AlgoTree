from setuptools import find_packages, setup

setup(
    name="AlgoTree",
    version="0.1.1",
    author="Alex Towell",
    author_email="lex@metafunctor.com",
    description="A algorithmic tookit for working with trees in Python",
    long_description=open("README.rst").read(),
#    long_description_content_type="text/markdown",
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    url='https://github.com/queelius/AlgoTree',
    python_requires=">=3.6",
    extras_require={
         'dev': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinxcontrib-napoleon',
            'coverage',
        ],
    },
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'jt=bin.jt:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
