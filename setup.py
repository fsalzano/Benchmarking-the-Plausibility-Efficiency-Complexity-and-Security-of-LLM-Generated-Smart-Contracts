from setuptools import setup, find_packages

setup(
    name='sc_cognitive_complexity',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'py-solc-x',
    ],    description='A module for cognitive complexity evaluation.',
    author='Your Name',
    author_email='your.email@example.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
