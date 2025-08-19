from setuptools import find_packages, setup

setup(
    name="AlgoTree",
    version="1.0.0",
    author="Alex Towell",
    author_email="lex@metafunctor.com",
    description="A powerful tree manipulation library with pattern matching and transformations",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    packages=find_packages() + ['bin'],
    url='https://github.com/queelius/AlgoTree',
    project_urls={
        "Documentation": "https://queelius.github.io/AlgoTree/",
        "Source Code": "https://github.com/queelius/AlgoTree",
        "Issue Tracker": "https://github.com/queelius/AlgoTree/issues",
        "Changelog": "https://github.com/queelius/AlgoTree/blob/main/CHANGELOG.md",
    },
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies (if any)
    ],
    extras_require={
        'dev': [
            'sphinx',
            'sphinx-rtd-theme',
            'sphinxcontrib-napoleon',
            'coverage',
            'pytest',
            'flake8',
        ],
        'analytics': [
            'pandas>=1.3.0',
            'pyarrow>=6.0.0',
        ],
        'jupyter': [
            'ipywidgets>=7.6.0',
            'IPython>=7.0.0',
        ],
    },
    test_suite="test",
    entry_points={
        'console_scripts': [
            'jt=bin.jt:main',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="tree data-structure algorithms pattern-matching transformation fluent-api",
)
