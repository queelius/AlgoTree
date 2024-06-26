from setuptools import find_packages, setup

setup(
    name="AlgoTree",
    version="0.1.1",
    author="Alex Towell",
    author_email="lex@metafunctor.com",
    description="A algorithmic tookit for working with trees in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["anytree>=2.8.0", "graphviz>=0.16"],
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
    #    entry_points={
    #        'console_scripts': [
    #            'jsontree=bin.jsontree:main',
    #        ],
    #    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
    ],
)
